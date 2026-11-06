"""Reporte de supervisión de la operación de la clínica (NB-21).

Solo consulta: cuenta lo que ya guardan los demás casos de uso (citas, emergencias,
hospitalizaciones, cobros, recetas y órdenes de estudio). Lo consulta el responsable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from vetcare24.application.control_de_acceso import Permiso, Rol, exigir
from vetcare24.application.servicios import FabricaDeUnidades
from vetcare24.domain.ciclo_de_vida import ahora_utc
from vetcare24.domain.cita import EstadoCita
from vetcare24.domain.emergencia import EstadoEmergencia
from vetcare24.domain.hospitalizacion import EstadoHospitalizacion
from vetcare24.domain.money import Money


@dataclass(frozen=True)
class ReporteDeOperacion:
    generado_en: datetime
    citas_por_estado: dict[str, int]
    emergencias_por_estado: dict[str, int]
    hospitalizaciones_por_estado: dict[str, int]
    cobros_registrados: int
    ingresos_mxn: Money
    ingresos_por_metodo: dict[str, Money]
    recetas_emitidas: int
    ordenes_de_estudio_emitidas: int


class ServicioDeReportes:
    def __init__(
        self, fabrica: FabricaDeUnidades, reloj: Callable[[], datetime] = ahora_utc
    ) -> None:
        self._fabrica = fabrica
        self._reloj = reloj

    def operacion(self, rol: Rol) -> ReporteDeOperacion:
        exigir(rol, Permiso.CONSULTAR_REPORTES)
        with self._fabrica() as uow:
            citas = Counter(c.estado.value for c in uow.citas.listar())
            emergencias = Counter(e.estado.value for e in uow.emergencias.listar())
            hospitalizaciones = Counter(h.estado.value for h in uow.hospitalizaciones.listar())
            cobros = uow.cobros.todos()
            recetas = len(uow.recetas.listar())
            ordenes = len(uow.ordenes.listar())
        por_metodo: dict[str, Decimal] = {}
        for cobro in cobros:
            por_metodo[cobro.metodo.value] = (
                por_metodo.get(cobro.metodo.value, Decimal(0)) + cobro.total.monto)
        return ReporteDeOperacion(
            generado_en=self._reloj(),
            citas_por_estado={e.value: citas.get(e.value, 0) for e in EstadoCita},
            emergencias_por_estado={
                e.value: emergencias.get(e.value, 0) for e in EstadoEmergencia},
            hospitalizaciones_por_estado={
                e.value: hospitalizaciones.get(e.value, 0) for e in EstadoHospitalizacion},
            cobros_registrados=len(cobros),
            ingresos_mxn=Money.suma(c.total for c in cobros),
            ingresos_por_metodo={m: Money(v) for m, v in sorted(por_metodo.items())},
            recetas_emitidas=recetas, ordenes_de_estudio_emitidas=ordenes)
