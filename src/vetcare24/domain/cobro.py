"""Cobro de una cita (US10, BPMN «Facturar y cobrar servicios»).

Recepción cobra una cita REALIZADA, una sola vez, por el total vigente de sus servicios (D-02).
Es el registro del pago, no una factura fiscal (A-02). Después del cobro se puede entregar la
documentación al propietario.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from enum import StrEnum

from vetcare24.domain._validacion import exigir_texto
from vetcare24.domain.catalogo import ServicioVeterinario
from vetcare24.domain.cita import Cita, EstadoCita
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida
from vetcare24.domain.eventos import CobroRegistrado, EventoDeDominio
from vetcare24.domain.money import Money

ENTIDAD = "cobro"


class MetodoDePago(StrEnum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"


class Cobro:
    def __init__(
        self, *, cobro_id: str, cita_id: str, mascota_id: str, total: Money,
        metodo: MetodoDePago, cobrado_en: datetime,
    ) -> None:
        exigir_texto(cobro_id, "ID_VACIO", "El id del cobro")
        exigir_texto(cita_id, "CITA_REQUERIDA", "La cita")
        exigir_texto(mascota_id, "MASCOTA_REQUERIDA", "La mascota")
        if not isinstance(total, Money):
            raise InvarianteViolada("MONTO_INVALIDO", "El total debe ser un importe")
        if not isinstance(metodo, MetodoDePago):
            raise InvarianteViolada("METODO_INVALIDO", f"Método de pago desconocido: {metodo!r}")
        if not isinstance(cobrado_en, datetime) or cobrado_en.tzinfo is None:
            raise InvarianteViolada(
                "FECHA_HORA_SIN_ZONA", "cobrado_en debe ser una fecha y hora con zona horaria")
        self._cobro_id = cobro_id
        self._cita_id = cita_id
        self._mascota_id = mascota_id
        self._total = total
        self._metodo = metodo
        self._cobrado_en = cobrado_en
        self._eventos: list[EventoDeDominio] = []

    @property
    def cobro_id(self) -> str:
        return self._cobro_id

    @property
    def cita_id(self) -> str:
        return self._cita_id

    @property
    def mascota_id(self) -> str:
        return self._mascota_id

    @property
    def total(self) -> Money:
        return self._total

    @property
    def metodo(self) -> MetodoDePago:
        return self._metodo

    @property
    def cobrado_en(self) -> datetime:
        return self._cobrado_en

    def extraer_eventos(self) -> tuple[EventoDeDominio, ...]:
        pendientes = tuple(self._eventos)
        self._eventos.clear()
        return pendientes

    def _registrar_evento(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, Cobro) and otro._cobro_id == self._cobro_id

    def __hash__(self) -> int:
        return hash(self._cobro_id)


class RegistroDeCobros:
    """Servicio de dominio: cobra una cita si cumple las precondiciones."""

    def __init__(self, reloj: Callable[[], datetime]) -> None:
        self._reloj = reloj

    def cobrar(
        self, *, cobro_id: str, cita: Cita, catalogo: Mapping[str, ServicioVeterinario],
        metodo: MetodoDePago, cobro_existente: Cobro | None = None,
    ) -> Cobro:
        motivos = []
        if cita.estado is not EstadoCita.REALIZADA:
            motivos.append("CITA_NO_REALIZADA")
        if cobro_existente is not None:
            motivos.append("CITA_YA_COBRADA")
        if motivos:
            raise PrecondicionNoCumplida("cobrar", tuple(motivos), ENTIDAD)
        cobro = Cobro(
            cobro_id=cobro_id, cita_id=cita.cita_id, mascota_id=cita.mascota_id,
            total=cita.total(catalogo), metodo=metodo, cobrado_en=self._reloj())
        cobro._registrar_evento(CobroRegistrado(
            ocurrido_en=cobro.cobrado_en, cobro_id=cobro_id, cita_id=cita.cita_id,
            mascota_id=cita.mascota_id, total=cobro.total, metodo=metodo.value))
        return cobro
