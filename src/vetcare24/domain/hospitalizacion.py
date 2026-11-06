"""Hospitalización (CU-04, NB-18, R-04, R-08): internamiento de una mascota con hoja de monitoreo.

    INGRESADA --registrar_monitoreo--> INGRESADA   (agrega una lectura a la hoja)
    INGRESADA --dar_alta-------------> ALTA

Una mascota solo puede tener una hospitalización ingresada a la vez (decisión O-03). Las lecturas de
monitoreo solo se agregan mientras está ingresada y no se editan. El alta exige indicar el
resumen de alta; una hospitalización dada de alta ya no admite cambios.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from vetcare24.domain._validacion import exigir_texto
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida, TransicionInvalida
from vetcare24.domain.eventos import (
    EventoDeDominio,
    HospitalizacionFinalizada,
    HospitalizacionIniciada,
)
from vetcare24.domain.mascota import Mascota

ENTIDAD = "hospitalización"


class EstadoHospitalizacion(StrEnum):
    INGRESADA = "INGRESADA"
    ALTA = "ALTA"


class AccionHospitalizacion(StrEnum):
    REGISTRAR_MONITOREO = "registrar_monitoreo"
    DAR_ALTA = "dar_alta"


TRANSICIONES: Mapping[
    tuple[EstadoHospitalizacion, AccionHospitalizacion], EstadoHospitalizacion
] = {
    (EstadoHospitalizacion.INGRESADA, AccionHospitalizacion.REGISTRAR_MONITOREO):
        EstadoHospitalizacion.INGRESADA,
    (EstadoHospitalizacion.INGRESADA, AccionHospitalizacion.DAR_ALTA):
        EstadoHospitalizacion.ALTA,
}


def _con_zona(valor: object, nombre: str) -> datetime:
    if not isinstance(valor, datetime) or valor.tzinfo is None or valor.utcoffset() is None:
        raise InvarianteViolada(
            "FECHA_HORA_SIN_ZONA", f"{nombre} debe ser una fecha y hora con zona horaria")
    return valor


def _limpiar(texto: str) -> str:
    return " ".join(texto.split())


@dataclass(frozen=True)
class LecturaDeMonitoreo:
    """Una anotación de la hoja de monitoreo; temperatura y frecuencia son opcionales."""

    registrada_en: datetime
    observaciones: str
    temperatura_c: Decimal | None = None
    frecuencia_cardiaca: int | None = None

    def __post_init__(self) -> None:
        _con_zona(self.registrada_en, "registrada_en")
        exigir_texto(self.observaciones, "OBSERVACIONES_VACIAS", "Las observaciones")
        if self.temperatura_c is not None and not (
                isinstance(self.temperatura_c, Decimal) and Decimal(25) <= self.temperatura_c
                <= Decimal(45)):
            raise InvarianteViolada(
                "TEMPERATURA_INVALIDA", "La temperatura debe estar entre 25 y 45 °C")
        if self.frecuencia_cardiaca is not None and (
                isinstance(self.frecuencia_cardiaca, bool)
                or not isinstance(self.frecuencia_cardiaca, int)
                or not 1 <= self.frecuencia_cardiaca <= 400):
            raise InvarianteViolada(
                "FRECUENCIA_INVALIDA", "La frecuencia cardiaca debe estar entre 1 y 400 lpm")


class Hospitalizacion:
    """Agregado raíz. Se crea con `CicloDeVidaDeHospitalizacion.ingresar` y cambia solo por
    la máquina de estados (como las demás entidades)."""

    def __init__(
        self,
        *,
        hospitalizacion_id: str,
        mascota_id: str,
        motivo: str,
        ingresada_en: datetime,
        estado: EstadoHospitalizacion = EstadoHospitalizacion.INGRESADA,
        lecturas: tuple[LecturaDeMonitoreo, ...] = (),
        alta_en: datetime | None = None,
        resumen_alta: str | None = None,
    ) -> None:
        exigir_texto(hospitalizacion_id, "ID_VACIO", "El id de la hospitalización")
        exigir_texto(mascota_id, "MASCOTA_REQUERIDA", "La mascota")
        exigir_texto(motivo, "MOTIVO_VACIO", "El motivo del ingreso")
        _con_zona(ingresada_en, "ingresada_en")
        if not isinstance(estado, EstadoHospitalizacion):
            raise InvarianteViolada("ESTADO_INVALIDO", f"Estado desconocido: {estado!r}")
        if alta_en is not None:
            _con_zona(alta_en, "alta_en")
            if alta_en < ingresada_en:
                raise InvarianteViolada(
                    "ALTA_ANTES_DE_INGRESO", "El alta no puede ser anterior al ingreso")
        if resumen_alta is not None:
            exigir_texto(resumen_alta, "RESUMEN_ALTA_VACIO", "El resumen de alta")
        if (estado is EstadoHospitalizacion.ALTA) != (alta_en is not None and resumen_alta
                                                      is not None):
            raise InvarianteViolada(
                "ESTADO_INCONSISTENTE",
                "Una hospitalización en ALTA debe tener fecha y resumen de alta, y solo ella")
        for lectura in lecturas:
            if lectura.registrada_en < ingresada_en:
                raise InvarianteViolada(
                    "LECTURA_ANTES_DE_INGRESO", "Una lectura no puede ser anterior al ingreso")
        self._id = hospitalizacion_id
        self._mascota_id = mascota_id
        self._motivo = _limpiar(motivo)
        self._ingresada_en = ingresada_en
        self._estado = estado
        self._lecturas: list[LecturaDeMonitoreo] = list(lecturas)
        self._alta_en = alta_en
        self._resumen_alta = _limpiar(resumen_alta) if resumen_alta is not None else None
        self._eventos: list[EventoDeDominio] = []

    @property
    def hospitalizacion_id(self) -> str:
        return self._id

    @property
    def mascota_id(self) -> str:
        return self._mascota_id

    @property
    def motivo(self) -> str:
        return self._motivo

    @property
    def ingresada_en(self) -> datetime:
        return self._ingresada_en

    @property
    def estado(self) -> EstadoHospitalizacion:
        return self._estado

    @property
    def lecturas(self) -> tuple[LecturaDeMonitoreo, ...]:
        return tuple(self._lecturas)

    @property
    def alta_en(self) -> datetime | None:
        return self._alta_en

    @property
    def resumen_alta(self) -> str | None:
        return self._resumen_alta

    @property
    def esta_ingresada(self) -> bool:
        return self._estado is EstadoHospitalizacion.INGRESADA

    def extraer_eventos(self) -> tuple[EventoDeDominio, ...]:
        pendientes = tuple(self._eventos)
        self._eventos.clear()
        return pendientes

    # --- solo para CicloDeVidaDeHospitalizacion ---

    def _agregar_lectura(self, lectura: LecturaDeMonitoreo) -> None:
        if lectura.registrada_en < self._ingresada_en:
            raise InvarianteViolada(
                "LECTURA_ANTES_DE_INGRESO", "Una lectura no puede ser anterior al ingreso")
        self._lecturas.append(lectura)

    def _dar_alta(self, alta_en: datetime, resumen: str) -> None:
        Hospitalizacion(  # valida antes de cambiar
            hospitalizacion_id=self._id, mascota_id=self._mascota_id, motivo=self._motivo,
            ingresada_en=self._ingresada_en, estado=EstadoHospitalizacion.ALTA,
            lecturas=tuple(self._lecturas), alta_en=alta_en, resumen_alta=resumen)
        self._estado = EstadoHospitalizacion.ALTA
        self._alta_en = alta_en
        self._resumen_alta = _limpiar(resumen)

    def _registrar_evento(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, Hospitalizacion) and otro._id == self._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"Hospitalizacion({self._id!r}, {self._mascota_id!r}, {self._estado.value})"


class CicloDeVidaDeHospitalizacion:
    """Servicio de dominio: ingresa, monitorea y da de alta respetando la máquina de estados."""

    def __init__(self, reloj: Callable[[], datetime]) -> None:
        self._reloj = reloj

    def ingresar(
        self, *, hospitalizacion_id: str, mascota: Mascota, motivo: str,
        hospitalizaciones_de_la_mascota: tuple[Hospitalizacion, ...] = (),
    ) -> Hospitalizacion:
        if any(h.esta_ingresada for h in hospitalizaciones_de_la_mascota):  # O-03
            raise PrecondicionNoCumplida(
                "ingresar", ("MASCOTA_YA_HOSPITALIZADA",), ENTIDAD)
        hospitalizacion = Hospitalizacion(
            hospitalizacion_id=hospitalizacion_id, mascota_id=mascota.mascota_id, motivo=motivo,
            ingresada_en=self._reloj())
        hospitalizacion._registrar_evento(HospitalizacionIniciada(
            ocurrido_en=hospitalizacion.ingresada_en,
            hospitalizacion_id=hospitalizacion.hospitalizacion_id,
            mascota_id=hospitalizacion.mascota_id, motivo=hospitalizacion.motivo))
        return hospitalizacion

    def registrar_monitoreo(
        self, hospitalizacion: Hospitalizacion, *, observaciones: str,
        temperatura_c: Decimal | None = None, frecuencia_cardiaca: int | None = None,
    ) -> LecturaDeMonitoreo:
        self._exigir(hospitalizacion, AccionHospitalizacion.REGISTRAR_MONITOREO)
        lectura = LecturaDeMonitoreo(
            registrada_en=self._reloj(), observaciones=observaciones,
            temperatura_c=temperatura_c, frecuencia_cardiaca=frecuencia_cardiaca)
        hospitalizacion._agregar_lectura(lectura)
        return lectura

    def dar_alta(self, hospitalizacion: Hospitalizacion, resumen_alta: str) -> None:
        self._exigir(hospitalizacion, AccionHospitalizacion.DAR_ALTA)
        hospitalizacion._dar_alta(self._reloj(), resumen_alta)
        hospitalizacion._registrar_evento(HospitalizacionFinalizada(
            ocurrido_en=hospitalizacion.alta_en or self._reloj(),
            hospitalizacion_id=hospitalizacion.hospitalizacion_id,
            mascota_id=hospitalizacion.mascota_id,
            lecturas=len(hospitalizacion.lecturas)))

    @staticmethod
    def _exigir(hospitalizacion: Hospitalizacion, accion: AccionHospitalizacion) -> None:
        if (hospitalizacion.estado, accion) not in TRANSICIONES:
            raise TransicionInvalida(hospitalizacion.estado.value, accion.value, ENTIDAD)
