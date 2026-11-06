"""Casos de uso de Hospitalización (CU-04, NB-18, R-04, R-08, R-14).

Veterinario y personal clínico ingresan a la mascota (US17) y registran la hoja de monitoreo
(US18, US19, R-04); solo el veterinario da el alta (O-04).
Los eventos se publican después de confirmar la transacción.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from vetcare24.application.comandos import IngresarHospitalizacion, RegistrarMonitoreo
from vetcare24.application.control_de_acceso import Permiso, Rol, exigir
from vetcare24.application.despachador import Despachador
from vetcare24.application.errores import NoEncontrado, YaExiste
from vetcare24.application.puertos import UnidadDeTrabajo
from vetcare24.application.servicios import FabricaDeUnidades, nuevo_id
from vetcare24.domain.ciclo_de_vida import ahora_utc
from vetcare24.domain.hospitalizacion import (
    CicloDeVidaDeHospitalizacion,
    EstadoHospitalizacion,
    Hospitalizacion,
)

TIPO = "hospitalización"


class ServicioDeHospitalizacion:
    def __init__(
        self,
        fabrica: FabricaDeUnidades,
        despachador: Despachador,
        reloj: Callable[[], datetime] = ahora_utc,
        generar_id: Callable[[str], str] = nuevo_id,
    ) -> None:
        self._fabrica = fabrica
        self._despachador = despachador
        self._ciclo = CicloDeVidaDeHospitalizacion(reloj)
        self._generar_id = generar_id

    def ingresar(self, rol: Rol, comando: IngresarHospitalizacion) -> Hospitalizacion:
        exigir(rol, Permiso.INGRESAR_HOSPITALIZACION)
        with self._fabrica() as uow:
            mascota = uow.mascotas.obtener(comando.mascota_id)
            if mascota is None:
                raise NoEncontrado("mascota", comando.mascota_id)
            if comando.hospitalizacion_id and uow.hospitalizaciones.obtener(
                    comando.hospitalizacion_id):
                raise YaExiste(TIPO, comando.hospitalizacion_id)
            hospitalizacion = self._ciclo.ingresar(
                hospitalizacion_id=comando.hospitalizacion_id or self._generar_id("HOSP"),
                mascota=mascota, motivo=comando.motivo,
                hospitalizaciones_de_la_mascota=tuple(
                    uow.hospitalizaciones.listar(mascota_id=mascota.mascota_id)))
            uow.hospitalizaciones.agregar(hospitalizacion)
            eventos = hospitalizacion.extraer_eventos()
            for evento in eventos:
                uow.eventos.agregar(evento)
            uow.commit()
        self._despachador.publicar(eventos)
        return hospitalizacion

    def registrar_monitoreo(self, rol: Rol, comando: RegistrarMonitoreo) -> Hospitalizacion:
        exigir(rol, Permiso.MONITOREAR_HOSPITALIZACION)
        with self._fabrica() as uow:
            hospitalizacion = self._cargar(uow, comando.hospitalizacion_id)
            self._ciclo.registrar_monitoreo(
                hospitalizacion, observaciones=comando.observaciones,
                temperatura_c=comando.temperatura_c,
                frecuencia_cardiaca=comando.frecuencia_cardiaca)
            uow.hospitalizaciones.guardar(hospitalizacion)
            uow.commit()
        return hospitalizacion

    def dar_alta(self, rol: Rol, hospitalizacion_id: str, resumen_alta: str) -> Hospitalizacion:
        exigir(rol, Permiso.DAR_ALTA_HOSPITALIZACION)
        with self._fabrica() as uow:
            hospitalizacion = self._cargar(uow, hospitalizacion_id)
            self._ciclo.dar_alta(hospitalizacion, resumen_alta)
            uow.hospitalizaciones.guardar(hospitalizacion)
            eventos = hospitalizacion.extraer_eventos()
            for evento in eventos:
                uow.eventos.agregar(evento)
            uow.commit()
        self._despachador.publicar(eventos)
        return hospitalizacion

    def obtener(self, rol: Rol, hospitalizacion_id: str) -> Hospitalizacion:
        exigir(rol, Permiso.CONSULTAR_HOSPITALIZACION)
        with self._fabrica() as uow:
            return self._cargar(uow, hospitalizacion_id)

    def listar(
        self, rol: Rol, *, estado: EstadoHospitalizacion | None = None,
        mascota_id: str | None = None,
    ) -> list[Hospitalizacion]:
        exigir(rol, Permiso.CONSULTAR_HOSPITALIZACION)
        with self._fabrica() as uow:
            if mascota_id is not None and uow.mascotas.obtener(mascota_id) is None:
                raise NoEncontrado("mascota", mascota_id)
            return uow.hospitalizaciones.listar(estado=estado, mascota_id=mascota_id)

    @staticmethod
    def _cargar(uow: UnidadDeTrabajo, hospitalizacion_id: str) -> Hospitalizacion:
        hospitalizacion = uow.hospitalizaciones.obtener(hospitalizacion_id)
        if hospitalizacion is None:
            raise NoEncontrado(TIPO, hospitalizacion_id)
        return hospitalizacion
