"""Nota clínica y expediente (CU-02, US de expediente, NB-10..NB-13, R-02, R-03).

El expediente clínico de una mascota es la lista, en orden cronológico, de sus notas clínicas.
Una nota es un registro histórico: una vez guardada NO se modifica ni se borra (NB-12); una
corrección se registra como una nota nueva. Una nota puede ligarse a la cita en la que se
generó (opcional), y entonces esa cita debe ser de la misma mascota y estar REALIZADA (R-03).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from vetcare24.domain._validacion import exigir_texto
from vetcare24.domain.cita import Cita, EstadoCita
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida
from vetcare24.domain.eventos import EventoDeDominio, NotaClinicaRegistrada
from vetcare24.domain.mascota import Mascota

ENTIDAD = "nota clínica"


def _limpiar(texto: str) -> str:
    return " ".join(texto.split())


class NotaClinica:
    """Agregado raíz inmutable. Una nota nueva se crea con `RegistroClinico.registrar`."""

    def __init__(
        self,
        *,
        nota_id: str,
        mascota_id: str,
        diagnostico: str,
        registrada_en: datetime,
        indicaciones: str | None = None,
        cita_id: str | None = None,
    ) -> None:
        exigir_texto(nota_id, "ID_VACIO", "El id de la nota")
        exigir_texto(mascota_id, "MASCOTA_REQUERIDA", "La mascota")
        exigir_texto(diagnostico, "DIAGNOSTICO_VACIO", "El diagnóstico")
        if not isinstance(registrada_en, datetime) or registrada_en.tzinfo is None:
            raise InvarianteViolada(
                "FECHA_HORA_SIN_ZONA", "registrada_en debe ser una fecha y hora con zona horaria")
        if indicaciones is not None:
            exigir_texto(indicaciones, "INDICACIONES_VACIAS", "Las indicaciones")
        if cita_id is not None:
            exigir_texto(cita_id, "CITA_REQUERIDA", "La cita")
        self._nota_id = nota_id
        self._mascota_id = mascota_id
        self._diagnostico = _limpiar(diagnostico)
        self._indicaciones = _limpiar(indicaciones) if indicaciones is not None else None
        self._cita_id = cita_id
        self._registrada_en = registrada_en
        self._eventos: list[EventoDeDominio] = []

    @property
    def nota_id(self) -> str:
        return self._nota_id

    @property
    def mascota_id(self) -> str:
        return self._mascota_id

    @property
    def diagnostico(self) -> str:
        return self._diagnostico

    @property
    def indicaciones(self) -> str | None:
        return self._indicaciones

    @property
    def cita_id(self) -> str | None:
        return self._cita_id

    @property
    def registrada_en(self) -> datetime:
        return self._registrada_en

    def extraer_eventos(self) -> tuple[EventoDeDominio, ...]:
        pendientes = tuple(self._eventos)
        self._eventos.clear()
        return pendientes

    def _registrar_evento(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, NotaClinica) and otro._nota_id == self._nota_id

    def __hash__(self) -> int:
        return hash(self._nota_id)

    def __repr__(self) -> str:
        return f"NotaClinica({self._nota_id!r}, {self._mascota_id!r})"


def validar_cita_de_la_mascota(
    cita: Cita | None, mascota: Mascota, accion: str, entidad: str
) -> None:
    """Un documento ligado a una cita exige que sea de la misma mascota y esté REALIZADA."""
    if cita is None:
        return
    motivos = []
    if cita.mascota_id != mascota.mascota_id:
        motivos.append("CITA_DE_OTRA_MASCOTA")
    if cita.estado is not EstadoCita.REALIZADA:
        motivos.append("CITA_NO_REALIZADA")
    if motivos:
        raise PrecondicionNoCumplida(accion, tuple(motivos), entidad)


class RegistroClinico:
    """Servicio de dominio: crea notas clínicas validando la cita con la que se ligan."""

    def __init__(self, reloj: Callable[[], datetime]) -> None:
        self._reloj = reloj

    def registrar(
        self,
        *,
        nota_id: str,
        mascota: Mascota,
        diagnostico: str,
        indicaciones: str | None = None,
        cita: Cita | None = None,
    ) -> NotaClinica:
        validar_cita_de_la_mascota(cita, mascota, "registrar", ENTIDAD)
        nota = NotaClinica(
            nota_id=nota_id, mascota_id=mascota.mascota_id, diagnostico=diagnostico,
            registrada_en=self._reloj(), indicaciones=indicaciones,
            cita_id=cita.cita_id if cita is not None else None)
        nota._registrar_evento(NotaClinicaRegistrada(
            ocurrido_en=nota.registrada_en, nota_id=nota.nota_id,
            mascota_id=nota.mascota_id, cita_id=nota.cita_id))
        return nota
