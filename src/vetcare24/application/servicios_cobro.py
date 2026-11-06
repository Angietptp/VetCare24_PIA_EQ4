"""Casos de uso de cobro y entrega de documentación (US10, BPMN carril de Recepción).

`cobrar` registra el pago de una cita REALIZADA, una sola vez, por su total vigente.
`entregar_documentacion` reúne y entrega al propietario el comprobante de cobro, las notas, las
recetas y las órdenes de estudio de la cita; solo procede si la cita ya fue cobrada.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from vetcare24.application.comandos import RegistrarCobro
from vetcare24.application.control_de_acceso import Permiso, Rol, exigir
from vetcare24.application.despachador import Despachador
from vetcare24.application.errores import NoEncontrado, YaExiste
from vetcare24.application.servicios import FabricaDeUnidades, nuevo_id
from vetcare24.domain.ciclo_de_vida import ahora_utc
from vetcare24.domain.cobro import Cobro, MetodoDePago, RegistroDeCobros
from vetcare24.domain.documentos_clinicos import OrdenDeEstudio, Receta
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida
from vetcare24.domain.eventos import DocumentacionEntregada
from vetcare24.domain.nota_clinica import NotaClinica

TIPO = "cobro"


@dataclass(frozen=True)
class Documentacion:
    """Lo que se entrega al propietario al terminar la atención de una cita."""

    cita_id: str
    propietario_id: str
    mascota_id: str
    cobro: Cobro
    notas: tuple[NotaClinica, ...]
    recetas: tuple[Receta, ...]
    ordenes: tuple[OrdenDeEstudio, ...]


class ServicioDeCobro:
    def __init__(
        self,
        fabrica: FabricaDeUnidades,
        despachador: Despachador,
        reloj: Callable[[], datetime] = ahora_utc,
        generar_id: Callable[[str], str] = nuevo_id,
    ) -> None:
        self._fabrica = fabrica
        self._despachador = despachador
        self._reloj = reloj
        self._registro = RegistroDeCobros(reloj)
        self._generar_id = generar_id

    def cobrar(self, rol: Rol, comando: RegistrarCobro) -> Cobro:
        exigir(rol, Permiso.REGISTRAR_COBRO)
        try:
            metodo = MetodoDePago(comando.metodo)
        except ValueError as error:
            raise InvarianteViolada(
                "METODO_INVALIDO", f"Método de pago desconocido: {comando.metodo!r}") from error
        with self._fabrica() as uow:
            cita = uow.citas.obtener(comando.cita_id)
            if cita is None:
                raise NoEncontrado("cita", comando.cita_id)
            if comando.cobro_id and uow.cobros.obtener(comando.cobro_id):
                raise YaExiste(TIPO, comando.cobro_id)
            cobro = self._registro.cobrar(
                cobro_id=comando.cobro_id or self._generar_id("COB"), cita=cita,
                catalogo=uow.servicios.todos(), metodo=metodo,
                cobro_existente=uow.cobros.de_la_cita(cita.cita_id))
            uow.cobros.agregar(cobro)
            eventos = cobro.extraer_eventos()
            for evento in eventos:
                uow.eventos.agregar(evento)
            uow.commit()
        self._despachador.publicar(eventos)
        return cobro

    def obtener_de_la_cita(self, rol: Rol, cita_id: str) -> Cobro:
        exigir(rol, Permiso.CONSULTAR_COBRO)
        with self._fabrica() as uow:
            if uow.citas.obtener(cita_id) is None:
                raise NoEncontrado("cita", cita_id)
            cobro = uow.cobros.de_la_cita(cita_id)
        if cobro is None:
            raise NoEncontrado(TIPO, f"de la cita {cita_id}")
        return cobro

    def entregar_documentacion(self, rol: Rol, cita_id: str) -> Documentacion:
        exigir(rol, Permiso.ENTREGAR_DOCUMENTACION)
        with self._fabrica() as uow:
            cita = uow.citas.obtener(cita_id)
            if cita is None:
                raise NoEncontrado("cita", cita_id)
            cobro = uow.cobros.de_la_cita(cita_id)
            if cobro is None:
                raise PrecondicionNoCumplida("entregar", ("CITA_SIN_COBRO",), "documentación")
            notas = tuple(n for n in uow.notas.listar(mascota_id=cita.mascota_id)
                          if n.cita_id == cita_id)
            documentacion = Documentacion(
                cita_id=cita_id, propietario_id=cita.propietario_id, mascota_id=cita.mascota_id,
                cobro=cobro, notas=notas,
                recetas=tuple(uow.recetas.listar(cita_id=cita_id)),
                ordenes=tuple(uow.ordenes.listar(cita_id=cita_id)))
            evento = DocumentacionEntregada(
                ocurrido_en=self._reloj(), cita_id=cita_id,
                propietario_id=cita.propietario_id, mascota_id=cita.mascota_id)
            uow.eventos.agregar(evento)
            uow.commit()
        self._despachador.publicar((evento,))
        return documentacion
