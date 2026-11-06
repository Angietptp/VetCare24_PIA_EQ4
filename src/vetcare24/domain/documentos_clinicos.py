"""Receta (US13) y orden de estudio (US14): documentos clínicos que emite el veterinario.

Igual que la nota clínica, son registros inmutables ligados a una mascota y, opcionalmente, a
una cita REALIZADA de esa mascota. La receta lleva al menos un medicamento.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from vetcare24.domain._validacion import exigir_texto
from vetcare24.domain.cita import Cita
from vetcare24.domain.errors import InvarianteViolada
from vetcare24.domain.eventos import EventoDeDominio, OrdenDeEstudioEmitida, RecetaEmitida
from vetcare24.domain.mascota import Mascota
from vetcare24.domain.nota_clinica import validar_cita_de_la_mascota


def _limpiar(texto: str) -> str:
    return " ".join(texto.split())


def _con_zona(valor: object, nombre: str) -> datetime:
    if not isinstance(valor, datetime) or valor.tzinfo is None or valor.utcoffset() is None:
        raise InvarianteViolada(
            "FECHA_HORA_SIN_ZONA", f"{nombre} debe ser una fecha y hora con zona horaria")
    return valor


@dataclass(frozen=True)
class Medicamento:
    nombre: str
    dosis: str
    indicaciones: str | None = None

    def __post_init__(self) -> None:
        exigir_texto(self.nombre, "MEDICAMENTO_VACIO", "El nombre del medicamento")
        exigir_texto(self.dosis, "DOSIS_VACIA", "La dosis")
        if self.indicaciones is not None:
            exigir_texto(self.indicaciones, "INDICACIONES_VACIAS", "Las indicaciones")
        object.__setattr__(self, "nombre", _limpiar(self.nombre))
        object.__setattr__(self, "dosis", _limpiar(self.dosis))
        if self.indicaciones is not None:
            object.__setattr__(self, "indicaciones", _limpiar(self.indicaciones))


class _Documento:
    def __init__(self) -> None:
        self._eventos: list[EventoDeDominio] = []

    def extraer_eventos(self) -> tuple[EventoDeDominio, ...]:
        pendientes = tuple(self._eventos)
        self._eventos.clear()
        return pendientes

    def _registrar_evento(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)


class Receta(_Documento):
    def __init__(
        self, *, receta_id: str, mascota_id: str, medicamentos: tuple[Medicamento, ...],
        registrada_en: datetime, cita_id: str | None = None,
    ) -> None:
        super().__init__()
        exigir_texto(receta_id, "ID_VACIO", "El id de la receta")
        exigir_texto(mascota_id, "MASCOTA_REQUERIDA", "La mascota")
        if not medicamentos:
            raise InvarianteViolada("RECETA_SIN_MEDICAMENTOS", "La receta necesita un medicamento")
        if cita_id is not None:
            exigir_texto(cita_id, "CITA_REQUERIDA", "La cita")
        _con_zona(registrada_en, "registrada_en")
        self._receta_id = receta_id
        self._mascota_id = mascota_id
        self._medicamentos = tuple(medicamentos)
        self._registrada_en = registrada_en
        self._cita_id = cita_id

    @property
    def receta_id(self) -> str:
        return self._receta_id

    @property
    def mascota_id(self) -> str:
        return self._mascota_id

    @property
    def medicamentos(self) -> tuple[Medicamento, ...]:
        return self._medicamentos

    @property
    def registrada_en(self) -> datetime:
        return self._registrada_en

    @property
    def cita_id(self) -> str | None:
        return self._cita_id

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, Receta) and otro._receta_id == self._receta_id

    def __hash__(self) -> int:
        return hash(self._receta_id)


class OrdenDeEstudio(_Documento):
    def __init__(
        self, *, orden_id: str, mascota_id: str, estudio: str, registrada_en: datetime,
        indicaciones: str | None = None, cita_id: str | None = None,
    ) -> None:
        super().__init__()
        exigir_texto(orden_id, "ID_VACIO", "El id de la orden")
        exigir_texto(mascota_id, "MASCOTA_REQUERIDA", "La mascota")
        exigir_texto(estudio, "ESTUDIO_VACIO", "El estudio")
        if indicaciones is not None:
            exigir_texto(indicaciones, "INDICACIONES_VACIAS", "Las indicaciones")
        if cita_id is not None:
            exigir_texto(cita_id, "CITA_REQUERIDA", "La cita")
        _con_zona(registrada_en, "registrada_en")
        self._orden_id = orden_id
        self._mascota_id = mascota_id
        self._estudio = _limpiar(estudio)
        self._indicaciones = _limpiar(indicaciones) if indicaciones is not None else None
        self._registrada_en = registrada_en
        self._cita_id = cita_id

    @property
    def orden_id(self) -> str:
        return self._orden_id

    @property
    def mascota_id(self) -> str:
        return self._mascota_id

    @property
    def estudio(self) -> str:
        return self._estudio

    @property
    def indicaciones(self) -> str | None:
        return self._indicaciones

    @property
    def registrada_en(self) -> datetime:
        return self._registrada_en

    @property
    def cita_id(self) -> str | None:
        return self._cita_id

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, OrdenDeEstudio) and otro._orden_id == self._orden_id

    def __hash__(self) -> int:
        return hash(self._orden_id)


class EmisorDeDocumentos:
    """Servicio de dominio: emite recetas y órdenes validando la cita con la que se ligan."""

    def __init__(self, reloj: Callable[[], datetime]) -> None:
        self._reloj = reloj

    def emitir_receta(
        self, *, receta_id: str, mascota: Mascota, medicamentos: tuple[Medicamento, ...],
        cita: Cita | None = None,
    ) -> Receta:
        validar_cita_de_la_mascota(cita, mascota, "emitir", "receta")
        receta = Receta(
            receta_id=receta_id, mascota_id=mascota.mascota_id, medicamentos=medicamentos,
            registrada_en=self._reloj(), cita_id=cita.cita_id if cita is not None else None)
        receta._registrar_evento(RecetaEmitida(
            ocurrido_en=receta.registrada_en, receta_id=receta_id, mascota_id=mascota.mascota_id,
            medicamentos=len(receta.medicamentos), cita_id=receta.cita_id))
        return receta

    def emitir_orden(
        self, *, orden_id: str, mascota: Mascota, estudio: str, indicaciones: str | None = None,
        cita: Cita | None = None,
    ) -> OrdenDeEstudio:
        validar_cita_de_la_mascota(cita, mascota, "emitir", "orden de estudio")
        orden = OrdenDeEstudio(
            orden_id=orden_id, mascota_id=mascota.mascota_id, estudio=estudio,
            registrada_en=self._reloj(), indicaciones=indicaciones,
            cita_id=cita.cita_id if cita is not None else None)
        orden._registrar_evento(OrdenDeEstudioEmitida(
            ocurrido_en=orden.registrada_en, orden_id=orden_id, mascota_id=mascota.mascota_id,
            estudio=orden.estudio, cita_id=orden.cita_id))
        return orden
