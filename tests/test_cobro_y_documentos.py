"""US10 (cobro y entrega de documentación), US13 (recetas) y US14 (órdenes de estudio)."""

from datetime import date
from decimal import Decimal

import pytest

from tests.bd import BACKENDS, HORA, armar, preparar, sembrar_basico
from vetcare24.application.comandos import (
    AtenderEmergencia,
    EmitirOrdenDeEstudio,
    EmitirReceta,
    IngresarHospitalizacion,
    MedicamentoRecetado,
    RegistrarCobro,
    RegistrarNotaClinica,
    SolicitarCita,
)
from vetcare24.application.control_de_acceso import Rol
from vetcare24.application.errores import AccesoDenegado, NoEncontrado, YaExiste
from vetcare24.domain.cobro import Cobro, MetodoDePago
from vetcare24.domain.documentos_clinicos import (
    EmisorDeDocumentos,
    Medicamento,
    OrdenDeEstudio,
    Receta,
)
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida
from vetcare24.domain.eventos import (
    CobroRegistrado,
    DocumentacionEntregada,
    OrdenDeEstudioEmitida,
    RecetaEmitida,
)
from vetcare24.domain.mascota import Mascota
from vetcare24.domain.money import Money

VET, RECEPCION, CLINICO, RESP = (
    Rol.VETERINARIO, Rol.RECEPCION, Rol.PERSONAL_CLINICO, Rol.RESPONSABLE)
MASCOTA = Mascota(mascota_id="M1", propietario_id="P1", nombre="Rex", especie="Perro")
AMOX = MedicamentoRecetado("Amoxicilina", "250 mg cada 12 h", "7 días")


def _entorno(backend, tmp_path):
    url = preparar(backend, tmp_path)
    sembrar_basico(url)
    return armar(url)


def _cita(entorno, realizada=True):
    entorno.citas.solicitar(RECEPCION, SolicitarCita(
        propietario_id="P1", mascota_id="M1", servicios=(("S1", 3),),
        fecha_solicitud=date(2026, 10, 2), autorizada=True, cita_id="C1"))
    entorno.citas.confirmar(RECEPCION, "C1")
    if realizada:
        entorno.citas.realizar(VET, "C1")


# --- dominio: documentos ---

def test_el_emisor_crea_receta_y_orden_con_su_evento():
    emisor = EmisorDeDocumentos(lambda: HORA)
    receta = emisor.emitir_receta(
        receta_id="R1", mascota=MASCOTA, medicamentos=(Medicamento(" Amoxicilina ", " 1  tab"),))
    assert (receta.medicamentos[0].nombre, receta.medicamentos[0].dosis) == ("Amoxicilina", "1 tab")
    (evento,) = receta.extraer_eventos()
    assert isinstance(evento, RecetaEmitida) and evento.medicamentos == 1
    orden = emisor.emitir_orden(orden_id="O1", mascota=MASCOTA, estudio=" Biometría  hemática ")
    assert orden.estudio == "Biometría hemática" and orden.indicaciones is None
    (evento,) = orden.extraer_eventos()
    assert isinstance(evento, OrdenDeEstudioEmitida)
    assert receta == Receta(receta_id="R1", mascota_id="X", registrada_en=HORA,
                            medicamentos=(Medicamento("a", "b"),)) and hash(receta)
    assert orden == OrdenDeEstudio(orden_id="O1", mascota_id="X", estudio="y",
                                   registrada_en=HORA) and hash(orden)


@pytest.mark.parametrize("construir,codigo", [
    (lambda: Medicamento("", "1"), "MEDICAMENTO_VACIO"),
    (lambda: Medicamento("a", " "), "DOSIS_VACIA"),
    (lambda: Medicamento("a", "1", " "), "INDICACIONES_VACIAS"),
    (lambda: Receta(receta_id="R", mascota_id="M", medicamentos=(), registrada_en=HORA),
     "RECETA_SIN_MEDICAMENTOS"),
    (lambda: Receta(receta_id="", mascota_id="M", medicamentos=(Medicamento("a", "b"),),
                    registrada_en=HORA), "ID_VACIO"),
    (lambda: Receta(receta_id="R", mascota_id="M", medicamentos=(Medicamento("a", "b"),),
                    registrada_en=HORA, cita_id=" "), "CITA_REQUERIDA"),
    (lambda: OrdenDeEstudio(orden_id="O", mascota_id="M", estudio=" ", registrada_en=HORA),
     "ESTUDIO_VACIO"),
    (lambda: OrdenDeEstudio(orden_id="O", mascota_id="M", estudio="e", registrada_en=HORA,
                            indicaciones=" "), "INDICACIONES_VACIAS"),
    (lambda: OrdenDeEstudio(orden_id="", mascota_id="M", estudio="e", registrada_en=HORA),
     "ID_VACIO"),
    (lambda: OrdenDeEstudio(orden_id="O", mascota_id="", estudio="e", registrada_en=HORA),
     "MASCOTA_REQUERIDA"),
])
def test_documentos_invalidos(construir, codigo):
    with pytest.raises(InvarianteViolada) as error:
        construir()
    assert error.value.codigo == codigo


# --- dominio: cobro ---

def test_el_cobro_valida_sus_datos():
    base = {"cobro_id": "C", "cita_id": "X", "mascota_id": "M", "total": Money.mxn("10"),
            "metodo": MetodoDePago.EFECTIVO, "cobrado_en": HORA}
    assert Cobro(**base) == Cobro(**{**base, "mascota_id": "Z"})
    casos = (
        ({"cobro_id": ""}, "ID_VACIO"), ({"cita_id": ""}, "CITA_REQUERIDA"),
        ({"mascota_id": ""}, "MASCOTA_REQUERIDA"), ({"total": 10}, "MONTO_INVALIDO"),
        ({"metodo": "oro"}, "METODO_INVALIDO"))
    for campos, codigo in casos:
        with pytest.raises(InvarianteViolada) as error:
            Cobro(**{**base, **campos})
        assert error.value.codigo == codigo
    with pytest.raises(InvarianteViolada):
        Cobro(**{**base, "cobrado_en": HORA.replace(tzinfo=None)})
    assert hash(Cobro(**base))


# --- servicios: recetas y órdenes ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_receta_y_orden_se_guardan_y_aparecen_en_el_expediente(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    receta = entorno.expediente.emitir_receta(VET, EmitirReceta(
        mascota_id="M1", medicamentos=(AMOX, MedicamentoRecetado("Meloxicam", "0.1 mg/kg"))))
    orden = entorno.expediente.emitir_orden(VET, EmitirOrdenDeEstudio(
        mascota_id="M1", estudio="Radiografía", indicaciones="Ayuno"))
    g = entorno.expediente.obtener_receta(RESP, receta.receta_id)
    assert [(m.nombre, m.indicaciones) for m in g.medicamentos] == [
        ("Amoxicilina", "7 días"), ("Meloxicam", None)]
    assert entorno.expediente.obtener_orden(CLINICO, orden.orden_id).estudio == "Radiografía"
    assert len(entorno.expediente.recetas(VET, "M1")) == 1
    assert len(entorno.expediente.ordenes(VET, "M1")) == 1
    with entorno.fabrica() as uow:
        assert [e["evento"] for e in uow.eventos.todos()] == [
            "RecetaEmitida", "OrdenDeEstudioEmitida"]


@pytest.mark.parametrize("backend", BACKENDS)
def test_receta_y_orden_ligadas_a_una_cita_realizada(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita(entorno, realizada=False)
    comando = EmitirReceta(mascota_id="M1", medicamentos=(AMOX,), cita_id="C1")
    with pytest.raises(PrecondicionNoCumplida) as error:
        entorno.expediente.emitir_receta(VET, comando)
    assert error.value.motivos == ("CITA_NO_REALIZADA",)
    entorno.citas.realizar(VET, "C1")
    assert entorno.expediente.emitir_receta(VET, comando).cita_id == "C1"
    orden = entorno.expediente.emitir_orden(VET, EmitirOrdenDeEstudio(
        mascota_id="M1", estudio="Rayos X", cita_id="C1"))
    assert orden.cita_id == "C1"


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_de_recetas_y_ordenes(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    s = entorno.expediente
    for rol in (RECEPCION, CLINICO, RESP):
        with pytest.raises(AccesoDenegado):
            s.emitir_receta(rol, EmitirReceta(mascota_id="M1", medicamentos=(AMOX,)))
        with pytest.raises(AccesoDenegado):
            s.emitir_orden(rol, EmitirOrdenDeEstudio(mascota_id="M1", estudio="x"))
    with pytest.raises(AccesoDenegado):
        s.obtener_receta(RECEPCION, "R")
    with pytest.raises(NoEncontrado):
        s.emitir_receta(VET, EmitirReceta(mascota_id="NOPE", medicamentos=(AMOX,)))
    with pytest.raises(NoEncontrado):
        s.emitir_receta(VET, EmitirReceta(mascota_id="M1", medicamentos=(AMOX,), cita_id="NO"))
    with pytest.raises(NoEncontrado):
        s.emitir_orden(VET, EmitirOrdenDeEstudio(mascota_id="NOPE", estudio="x"))
    with pytest.raises(NoEncontrado):
        s.emitir_orden(VET, EmitirOrdenDeEstudio(mascota_id="M1", estudio="x", cita_id="NO"))
    for llamada in (lambda: s.obtener_receta(VET, "NO"), lambda: s.obtener_orden(VET, "NO"),
                    lambda: s.recetas(VET, "NO"), lambda: s.ordenes(VET, "NO")):
        with pytest.raises(NoEncontrado):
            llamada()
    with pytest.raises(InvarianteViolada):
        s.emitir_receta(VET, EmitirReceta(mascota_id="M1", medicamentos=()))
    s.emitir_receta(VET, EmitirReceta(mascota_id="M1", medicamentos=(AMOX,), receta_id="R-9"))
    s.emitir_orden(VET, EmitirOrdenDeEstudio(mascota_id="M1", estudio="x", orden_id="O-9"))
    with pytest.raises(YaExiste):
        s.emitir_receta(VET, EmitirReceta(mascota_id="M1", medicamentos=(AMOX,), receta_id="R-9"))
    with pytest.raises(YaExiste):
        s.emitir_orden(VET, EmitirOrdenDeEstudio(mascota_id="M1", estudio="x", orden_id="O-9"))


# --- servicios: cobro y documentación ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_cobrar_una_cita_realizada_usa_el_total_vigente(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita(entorno)
    cobro = entorno.cobro.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="tarjeta"))
    assert (cobro.total.monto, cobro.metodo, cobro.cobrado_en) == (
        Decimal("900.00"), MetodoDePago.TARJETA, HORA)  # 3 x 300
    guardado = entorno.cobro.obtener_de_la_cita(RESP, "C1")
    assert (guardado.cobro_id, guardado.total) == (cobro.cobro_id, Money.mxn("900"))
    assert isinstance(entorno.eventos.registrados[-1].evento, CobroRegistrado)


@pytest.mark.parametrize("backend", BACKENDS)
def test_no_se_cobra_una_cita_no_realizada_ni_dos_veces(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita(entorno, realizada=False)
    comando = RegistrarCobro(cita_id="C1", metodo="efectivo")
    with pytest.raises(PrecondicionNoCumplida) as error:
        entorno.cobro.cobrar(RECEPCION, comando)
    assert error.value.motivos == ("CITA_NO_REALIZADA",)
    entorno.citas.realizar(VET, "C1")
    entorno.cobro.cobrar(RECEPCION, comando)
    with pytest.raises(PrecondicionNoCumplida) as error:
        entorno.cobro.cobrar(RECEPCION, comando)
    assert error.value.motivos == ("CITA_YA_COBRADA",)


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_del_cobro(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    s = entorno.cobro
    _cita(entorno)
    for rol in (VET, CLINICO, RESP):
        with pytest.raises(AccesoDenegado):
            s.cobrar(rol, RegistrarCobro(cita_id="C1", metodo="efectivo"))
        with pytest.raises(AccesoDenegado):
            s.entregar_documentacion(rol, "C1")
    with pytest.raises(AccesoDenegado):
        s.obtener_de_la_cita(CLINICO, "C1")
    with pytest.raises(InvarianteViolada) as error:
        s.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="oro"))
    assert error.value.codigo == "METODO_INVALIDO"
    with pytest.raises(NoEncontrado):
        s.cobrar(RECEPCION, RegistrarCobro(cita_id="NO", metodo="efectivo"))
    with pytest.raises(NoEncontrado):
        s.obtener_de_la_cita(RECEPCION, "NO")
    with pytest.raises(NoEncontrado):
        s.obtener_de_la_cita(RECEPCION, "C1")  # aún sin cobro
    with pytest.raises(NoEncontrado):
        s.entregar_documentacion(RECEPCION, "NO")
    s.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="efectivo", cobro_id="COB-9"))
    with pytest.raises(YaExiste):
        s.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="efectivo", cobro_id="COB-9"))


@pytest.mark.parametrize("backend", BACKENDS)
def test_entregar_documentacion_reune_cobro_notas_recetas_y_ordenes(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita(entorno)
    with pytest.raises(PrecondicionNoCumplida) as error:  # todavía sin cobro
        entorno.cobro.entregar_documentacion(RECEPCION, "C1")
    assert error.value.motivos == ("CITA_SIN_COBRO",)
    entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(
        mascota_id="M1", diagnostico="Otitis", cita_id="C1"))
    entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(  # otra nota, sin cita
        mascota_id="M1", diagnostico="Aparte"))
    entorno.expediente.emitir_receta(VET, EmitirReceta(
        mascota_id="M1", medicamentos=(AMOX,), cita_id="C1"))
    entorno.expediente.emitir_orden(VET, EmitirOrdenDeEstudio(
        mascota_id="M1", estudio="Cultivo", cita_id="C1"))
    entorno.cobro.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="transferencia"))
    d = entorno.cobro.entregar_documentacion(RECEPCION, "C1")
    assert (d.propietario_id, d.mascota_id, d.cobro.total.monto) == ("P1", "M1", Decimal("900.00"))
    assert [n.diagnostico for n in d.notas] == ["Otitis"]
    assert (len(d.recetas), len(d.ordenes)) == (1, 1)
    assert isinstance(entorno.eventos.registrados[-1].evento, DocumentacionEntregada)
    with entorno.fabrica() as uow:
        assert uow.eventos.todos()[-1]["evento"] == "DocumentacionEntregada"


# --- reportes (NB-21) ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_reporte_de_operacion_cuenta_lo_registrado(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    vacio = entorno.reportes.operacion(RESP)
    assert vacio.cobros_registrados == 0 and vacio.ingresos_mxn == Money.cero()
    assert vacio.citas_por_estado["CONFIRMADA"] == 0 and vacio.generado_en == HORA
    _cita(entorno)
    entorno.cobro.cobrar(RECEPCION, RegistrarCobro(cita_id="C1", metodo="tarjeta"))
    entorno.expediente.emitir_receta(VET, EmitirReceta(mascota_id="M1", medicamentos=(AMOX,)))
    entorno.expediente.emitir_orden(VET, EmitirOrdenDeEstudio(mascota_id="M1", estudio="x"))
    entorno.emergencias.atender_emergencia(
        RECEPCION, AtenderEmergencia(motivo="Golpe", mascota_id="M1"))
    entorno.hospitalizacion.ingresar(VET, IngresarHospitalizacion(mascota_id="M1", motivo="x"))
    r = entorno.reportes.operacion(RESP)
    assert r.citas_por_estado["REALIZADA"] == 1
    assert r.emergencias_por_estado["IDENTIFICADA"] == 1
    assert r.hospitalizaciones_por_estado["INGRESADA"] == 1
    assert (r.cobros_registrados, r.ingresos_mxn.monto) == (1, Decimal("900.00"))
    assert r.ingresos_por_metodo == {"tarjeta": Money.mxn("900")}
    assert (r.recetas_emitidas, r.ordenes_de_estudio_emitidas) == (1, 1)


@pytest.mark.parametrize("backend", BACKENDS)
def test_solo_el_responsable_consulta_los_reportes(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    for rol in (RECEPCION, VET, CLINICO):
        with pytest.raises(AccesoDenegado):
            entorno.reportes.operacion(rol)
