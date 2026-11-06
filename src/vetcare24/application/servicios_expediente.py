"""Casos de uso del expediente clínico (CU-02, NB-10..NB-13, R-02, R-03).

`registrar_nota` guarda una nota en el expediente de la mascota (solo el veterinario). Las
notas no se modifican: una corrección es una nota nueva (NB-12). Los eventos se publican
después de confirmar la transacción.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from vetcare24.application.comandos import EmitirOrdenDeEstudio, EmitirReceta, RegistrarNotaClinica
from vetcare24.application.control_de_acceso import Permiso, Rol, exigir
from vetcare24.application.despachador import Despachador
from vetcare24.application.errores import NoEncontrado, YaExiste
from vetcare24.application.puertos import UnidadDeTrabajo
from vetcare24.application.servicios import FabricaDeUnidades, nuevo_id
from vetcare24.domain.ciclo_de_vida import ahora_utc
from vetcare24.domain.documentos_clinicos import (
    EmisorDeDocumentos,
    Medicamento,
    OrdenDeEstudio,
    Receta,
)
from vetcare24.domain.eventos import EventoDeDominio
from vetcare24.domain.nota_clinica import NotaClinica, RegistroClinico

TIPO = "nota clínica"
TIPO_RECETA = "receta"
TIPO_ORDEN = "orden de estudio"


class ServicioDeExpediente:
    def __init__(
        self,
        fabrica: FabricaDeUnidades,
        despachador: Despachador,
        reloj: Callable[[], datetime] = ahora_utc,
        generar_id: Callable[[str], str] = nuevo_id,
    ) -> None:
        self._fabrica = fabrica
        self._despachador = despachador
        self._registro = RegistroClinico(reloj)
        self._emisor = EmisorDeDocumentos(reloj)
        self._generar_id = generar_id

    def registrar_nota(self, rol: Rol, comando: RegistrarNotaClinica) -> NotaClinica:
        exigir(rol, Permiso.REGISTRAR_NOTA_CLINICA)
        with self._fabrica() as uow:
            mascota = uow.mascotas.obtener(comando.mascota_id)
            if mascota is None:
                raise NoEncontrado("mascota", comando.mascota_id)
            cita = None
            if comando.cita_id is not None:
                cita = uow.citas.obtener(comando.cita_id)
                if cita is None:
                    raise NoEncontrado("cita", comando.cita_id)
            if comando.nota_id and uow.notas.obtener(comando.nota_id):
                raise YaExiste(TIPO, comando.nota_id)
            nota = self._registro.registrar(
                nota_id=comando.nota_id or self._generar_id("NOTA"), mascota=mascota,
                diagnostico=comando.diagnostico, indicaciones=comando.indicaciones, cita=cita)
            uow.notas.agregar(nota)
            eventos = nota.extraer_eventos()
            for evento in eventos:
                uow.eventos.agregar(evento)
            uow.commit()
        self._despachador.publicar(eventos)
        return nota

    @staticmethod
    def _publicar(
        uow: UnidadDeTrabajo, documento: Receta | OrdenDeEstudio
    ) -> tuple[EventoDeDominio, ...]:
        eventos = documento.extraer_eventos()
        for evento in eventos:
            uow.eventos.agregar(evento)
        uow.commit()
        return eventos

    def emitir_receta(self, rol: Rol, comando: EmitirReceta) -> Receta:
        """US13: solo el veterinario. Los medicamentos se validan en el dominio."""
        exigir(rol, Permiso.EMITIR_RECETA)
        with self._fabrica() as uow:
            mascota = uow.mascotas.obtener(comando.mascota_id)
            if mascota is None:
                raise NoEncontrado("mascota", comando.mascota_id)
            cita = None
            if comando.cita_id is not None:
                cita = uow.citas.obtener(comando.cita_id)
                if cita is None:
                    raise NoEncontrado("cita", comando.cita_id)
            if comando.receta_id and uow.recetas.obtener(comando.receta_id):
                raise YaExiste(TIPO_RECETA, comando.receta_id)
            receta = self._emisor.emitir_receta(
                receta_id=comando.receta_id or self._generar_id("REC"), mascota=mascota,
                medicamentos=tuple(
                    Medicamento(m.nombre, m.dosis, m.indicaciones) for m in comando.medicamentos),
                cita=cita)
            uow.recetas.agregar(receta)
            eventos = self._publicar(uow, receta)
        self._despachador.publicar(eventos)
        return receta

    def emitir_orden(self, rol: Rol, comando: EmitirOrdenDeEstudio) -> OrdenDeEstudio:
        """US14: solo el veterinario."""
        exigir(rol, Permiso.EMITIR_ORDEN_ESTUDIO)
        with self._fabrica() as uow:
            mascota = uow.mascotas.obtener(comando.mascota_id)
            if mascota is None:
                raise NoEncontrado("mascota", comando.mascota_id)
            cita = None
            if comando.cita_id is not None:
                cita = uow.citas.obtener(comando.cita_id)
                if cita is None:
                    raise NoEncontrado("cita", comando.cita_id)
            if comando.orden_id and uow.ordenes.obtener(comando.orden_id):
                raise YaExiste(TIPO_ORDEN, comando.orden_id)
            orden = self._emisor.emitir_orden(
                orden_id=comando.orden_id or self._generar_id("ORD"), mascota=mascota,
                estudio=comando.estudio, indicaciones=comando.indicaciones, cita=cita)
            uow.ordenes.agregar(orden)
            eventos = self._publicar(uow, orden)
        self._despachador.publicar(eventos)
        return orden

    def obtener_receta(self, rol: Rol, receta_id: str) -> Receta:
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            receta = uow.recetas.obtener(receta_id)
        if receta is None:
            raise NoEncontrado(TIPO_RECETA, receta_id)
        return receta

    def obtener_orden(self, rol: Rol, orden_id: str) -> OrdenDeEstudio:
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            orden = uow.ordenes.obtener(orden_id)
        if orden is None:
            raise NoEncontrado(TIPO_ORDEN, orden_id)
        return orden

    def recetas(self, rol: Rol, mascota_id: str) -> list[Receta]:
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            if uow.mascotas.obtener(mascota_id) is None:
                raise NoEncontrado("mascota", mascota_id)
            return uow.recetas.listar(mascota_id=mascota_id)

    def ordenes(self, rol: Rol, mascota_id: str) -> list[OrdenDeEstudio]:
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            if uow.mascotas.obtener(mascota_id) is None:
                raise NoEncontrado("mascota", mascota_id)
            return uow.ordenes.listar(mascota_id=mascota_id)

    def obtener(self, rol: Rol, nota_id: str) -> NotaClinica:
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            nota = uow.notas.obtener(nota_id)
        if nota is None:
            raise NoEncontrado(TIPO, nota_id)
        return nota

    def expediente(self, rol: Rol, mascota_id: str) -> list[NotaClinica]:
        """El expediente completo de la mascota, de la nota más antigua a la más reciente."""
        exigir(rol, Permiso.CONSULTAR_EXPEDIENTE)
        with self._fabrica() as uow:
            if uow.mascotas.obtener(mascota_id) is None:
                raise NoEncontrado("mascota", mascota_id)
            return uow.notas.listar(mascota_id=mascota_id)
