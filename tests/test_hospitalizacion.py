"""CU-04: hospitalización con hoja de monitoreo (dominio, servicio y persistencia)."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tests.bd import BACKENDS, HORA, armar, preparar, sembrar_basico
from vetcare24.application.comandos import IngresarHospitalizacion, RegistrarMonitoreo
from vetcare24.application.control_de_acceso import Rol
from vetcare24.application.errores import AccesoDenegado, NoEncontrado, YaExiste
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida, TransicionInvalida
from vetcare24.domain.eventos import HospitalizacionFinalizada, HospitalizacionIniciada
from vetcare24.domain.hospitalizacion import (
    CicloDeVidaDeHospitalizacion,
    EstadoHospitalizacion,
    Hospitalizacion,
    LecturaDeMonitoreo,
)
from vetcare24.domain.mascota import Mascota

VET, RECEPCION, CLINICO, RESP = (
    Rol.VETERINARIO, Rol.RECEPCION, Rol.PERSONAL_CLINICO, Rol.RESPONSABLE)
MASCOTA = Mascota(mascota_id="M1", propietario_id="P1", nombre="Rex", especie="Perro")


def _entorno(backend, tmp_path):
    url = preparar(backend, tmp_path)
    sembrar_basico(url)
    return armar(url)


def _ingresar(entorno, **extra):
    return entorno.hospitalizacion.ingresar(VET, IngresarHospitalizacion(
        mascota_id="M1", motivo="Deshidratación", **extra))


# --- dominio ---

def test_ciclo_completo_en_el_dominio():
    ciclo = CicloDeVidaDeHospitalizacion(lambda: HORA)
    h = ciclo.ingresar(hospitalizacion_id="H1", mascota=MASCOTA, motivo=" Fractura  de pata ")
    assert (h.estado, h.motivo, h.esta_ingresada) == (
        EstadoHospitalizacion.INGRESADA, "Fractura de pata", True)
    ciclo.registrar_monitoreo(h, observaciones="Estable", temperatura_c=Decimal("38.5"),
                              frecuencia_cardiaca=100)
    ciclo.dar_alta(h, "Recuperada")
    assert (h.estado, h.resumen_alta, h.alta_en, len(h.lecturas)) == (
        EstadoHospitalizacion.ALTA, "Recuperada", HORA, 1)
    iniciada, finalizada = h.extraer_eventos()
    assert isinstance(iniciada, HospitalizacionIniciada)
    assert isinstance(finalizada, HospitalizacionFinalizada) and finalizada.lecturas == 1
    assert h.extraer_eventos() == ()


def test_una_sola_hospitalizacion_ingresada_por_mascota():
    ciclo = CicloDeVidaDeHospitalizacion(lambda: HORA)
    activa = ciclo.ingresar(hospitalizacion_id="H1", mascota=MASCOTA, motivo="A")
    with pytest.raises(PrecondicionNoCumplida) as error:
        ciclo.ingresar(hospitalizacion_id="H2", mascota=MASCOTA, motivo="B",
                       hospitalizaciones_de_la_mascota=(activa,))
    assert error.value.motivos == ("MASCOTA_YA_HOSPITALIZADA",)
    ciclo.dar_alta(activa, "Alta")  # tras el alta puede volver a ingresar
    ciclo.ingresar(hospitalizacion_id="H2", mascota=MASCOTA, motivo="B",
                   hospitalizaciones_de_la_mascota=(activa,))


def test_transiciones_invalidas_tras_el_alta():
    ciclo = CicloDeVidaDeHospitalizacion(lambda: HORA)
    h = ciclo.ingresar(hospitalizacion_id="H1", mascota=MASCOTA, motivo="A")
    ciclo.dar_alta(h, "Alta")
    with pytest.raises(TransicionInvalida) as error:
        ciclo.registrar_monitoreo(h, observaciones="Tarde")
    assert (error.value.estado, error.value.accion, error.value.entidad) == (
        "ALTA", "registrar_monitoreo", "hospitalización")
    with pytest.raises(TransicionInvalida):
        ciclo.dar_alta(h, "Otra vez")
    assert len(h.lecturas) == 0 and h.resumen_alta == "Alta"


def test_alta_sin_resumen_no_cambia_el_estado():
    ciclo = CicloDeVidaDeHospitalizacion(lambda: HORA)
    h = ciclo.ingresar(hospitalizacion_id="H1", mascota=MASCOTA, motivo="A")
    with pytest.raises(InvarianteViolada) as error:
        ciclo.dar_alta(h, "  ")
    assert error.value.codigo == "RESUMEN_ALTA_VACIO"
    assert h.estado is EstadoHospitalizacion.INGRESADA and h.alta_en is None


@pytest.mark.parametrize("campos,codigo", [
    ({"observaciones": " "}, "OBSERVACIONES_VACIAS"),
    ({"temperatura_c": Decimal("50")}, "TEMPERATURA_INVALIDA"),
    ({"temperatura_c": Decimal("10")}, "TEMPERATURA_INVALIDA"),
    ({"frecuencia_cardiaca": 0}, "FRECUENCIA_INVALIDA"),
    ({"frecuencia_cardiaca": 500}, "FRECUENCIA_INVALIDA"),
    ({"frecuencia_cardiaca": True}, "FRECUENCIA_INVALIDA"),
    ({"registrada_en": datetime(2026, 1, 1)}, "FECHA_HORA_SIN_ZONA"),  # noqa: DTZ001
])
def test_lectura_invalida(campos, codigo):
    base = {"registrada_en": HORA, "observaciones": "ok"}
    with pytest.raises(InvarianteViolada) as error:
        LecturaDeMonitoreo(**{**base, **campos})
    assert error.value.codigo == codigo


@pytest.mark.parametrize("campos,codigo", [
    ({"hospitalizacion_id": ""}, "ID_VACIO"),
    ({"mascota_id": ""}, "MASCOTA_REQUERIDA"),
    ({"motivo": " "}, "MOTIVO_VACIO"),
    ({"ingresada_en": datetime(2026, 1, 1)}, "FECHA_HORA_SIN_ZONA"),  # noqa: DTZ001
    ({"estado": "X"}, "ESTADO_INVALIDO"),
    ({"estado": EstadoHospitalizacion.ALTA}, "ESTADO_INCONSISTENTE"),
    ({"alta_en": HORA, "resumen_alta": "x"}, "ESTADO_INCONSISTENTE"),
    ({"alta_en": datetime(2020, 1, 1, tzinfo=UTC), "resumen_alta": "x",
      "estado": EstadoHospitalizacion.ALTA}, "ALTA_ANTES_DE_INGRESO"),
    ({"resumen_alta": " "}, "RESUMEN_ALTA_VACIO"),
    ({"lecturas": (LecturaDeMonitoreo(datetime(2020, 1, 1, tzinfo=UTC), "x"),)},
     "LECTURA_ANTES_DE_INGRESO"),
])
def test_hospitalizacion_invalida(campos, codigo):
    base = {"hospitalizacion_id": "H1", "mascota_id": "M1", "motivo": "A", "ingresada_en": HORA}
    with pytest.raises(InvarianteViolada) as error:
        Hospitalizacion(**{**base, **campos})
    assert error.value.codigo == codigo


def test_igualdad_y_repr():
    a = Hospitalizacion(hospitalizacion_id="H1", mascota_id="M1", motivo="A", ingresada_en=HORA)
    b = Hospitalizacion(hospitalizacion_id="H1", mascota_id="M2", motivo="B", ingresada_en=HORA)
    assert a == b and hash(a) == hash(b) and a != "H1" and "H1" in repr(a)


def test_lectura_anterior_al_ingreso_se_rechaza_en_el_agregado():
    ciclo = CicloDeVidaDeHospitalizacion(lambda: datetime(2020, 1, 1, tzinfo=UTC))
    h = Hospitalizacion(hospitalizacion_id="H1", mascota_id="M1", motivo="A", ingresada_en=HORA)
    with pytest.raises(InvarianteViolada):
        ciclo.registrar_monitoreo(h, observaciones="x")


# --- servicio y persistencia ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_ingresar_guarda_y_publica(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    h = _ingresar(entorno)
    guardada = entorno.hospitalizacion.obtener(RESP, h.hospitalizacion_id)
    assert (guardada.estado, guardada.ingresada_en, guardada.lecturas) == (
        EstadoHospitalizacion.INGRESADA, HORA, ())
    (registrado,) = entorno.eventos.registrados
    assert isinstance(registrado.evento, HospitalizacionIniciada)


@pytest.mark.parametrize("backend", BACKENDS)
def test_hoja_de_monitoreo_y_alta_se_conservan(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    h = _ingresar(entorno)
    for obs, temp, fc in (("Estable", "38.4", 100), ("Mejora", None, None), ("Come", "38.9", 90)):
        entorno.reloj.avanzar(hours=2)
        entorno.hospitalizacion.registrar_monitoreo(CLINICO, RegistrarMonitoreo(
            hospitalizacion_id=h.hospitalizacion_id, observaciones=obs,
            temperatura_c=Decimal(temp) if temp else None, frecuencia_cardiaca=fc))
    entorno.hospitalizacion.dar_alta(VET, h.hospitalizacion_id, "Recuperada")
    g = entorno.hospitalizacion.obtener(VET, h.hospitalizacion_id)
    assert g.estado is EstadoHospitalizacion.ALTA and g.resumen_alta == "Recuperada"
    assert [(x.observaciones, x.temperatura_c, x.frecuencia_cardiaca) for x in g.lecturas] == [
        ("Estable", Decimal("38.4"), 100), ("Mejora", None, None), ("Come", Decimal("38.9"), 90)]
    assert g.lecturas[0].registrada_en < g.lecturas[2].registrada_en
    with entorno.fabrica() as uow:
        assert [e["evento"] for e in uow.eventos.todos()] == [
            "HospitalizacionIniciada", "HospitalizacionFinalizada"]


@pytest.mark.parametrize("backend", BACKENDS)
def test_segunda_hospitalizacion_activa_se_rechaza_y_tras_el_alta_se_permite(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    h = _ingresar(entorno)
    with pytest.raises(PrecondicionNoCumplida):
        _ingresar(entorno)
    entorno.hospitalizacion.dar_alta(VET, h.hospitalizacion_id, "Alta")
    _ingresar(entorno)
    assert len(entorno.hospitalizacion.listar(VET, mascota_id="M1")) == 2
    activas = entorno.hospitalizacion.listar(VET, estado=EstadoHospitalizacion.INGRESADA)
    assert len(activas) == 1


@pytest.mark.parametrize("backend", BACKENDS)
def test_monitoreo_o_alta_tras_el_alta_se_rechazan_sin_cambiar_nada(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    h = _ingresar(entorno)
    entorno.hospitalizacion.dar_alta(VET, h.hospitalizacion_id, "Alta")
    with pytest.raises(TransicionInvalida):
        entorno.hospitalizacion.registrar_monitoreo(VET, RegistrarMonitoreo(
            hospitalizacion_id=h.hospitalizacion_id, observaciones="Tarde"))
    with pytest.raises(TransicionInvalida):
        entorno.hospitalizacion.dar_alta(VET, h.hospitalizacion_id, "Otra")
    g = entorno.hospitalizacion.obtener(VET, h.hospitalizacion_id)
    assert g.resumen_alta == "Alta" and g.lecturas == ()


@pytest.mark.parametrize("backend", BACKENDS)
def test_inexistentes_y_duplicados(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    servicio = entorno.hospitalizacion
    with pytest.raises(NoEncontrado):
        servicio.ingresar(VET, IngresarHospitalizacion(mascota_id="NOPE", motivo="x"))
    with pytest.raises(NoEncontrado):
        servicio.obtener(VET, "NOPE")
    with pytest.raises(NoEncontrado):
        servicio.dar_alta(VET, "NOPE", "x")
    with pytest.raises(NoEncontrado):
        servicio.registrar_monitoreo(VET, RegistrarMonitoreo(
            hospitalizacion_id="NOPE", observaciones="x"))
    with pytest.raises(NoEncontrado):
        servicio.listar(VET, mascota_id="NOPE")
    _ingresar(entorno, hospitalizacion_id="H-9")
    with pytest.raises(YaExiste):
        _ingresar(entorno, hospitalizacion_id="H-9")


@pytest.mark.parametrize("backend", BACKENDS)
def test_permisos_de_hospitalizacion(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    servicio = entorno.hospitalizacion
    for rol in (RECEPCION, RESP):
        with pytest.raises(AccesoDenegado):
            servicio.ingresar(rol, IngresarHospitalizacion(mascota_id="M1", motivo="x"))
    h = servicio.ingresar(CLINICO, IngresarHospitalizacion(mascota_id="M1", motivo="x"))
    for rol in (RECEPCION, RESP):
        with pytest.raises(AccesoDenegado):
            servicio.registrar_monitoreo(rol, RegistrarMonitoreo(
                hospitalizacion_id=h.hospitalizacion_id, observaciones="x"))
    for rol in (RECEPCION, CLINICO, RESP):
        with pytest.raises(AccesoDenegado):
            servicio.dar_alta(rol, h.hospitalizacion_id, "x")
    with pytest.raises(AccesoDenegado):
        servicio.obtener(RECEPCION, h.hospitalizacion_id)
    with pytest.raises(AccesoDenegado):
        servicio.listar(RECEPCION)
    assert len(servicio.listar(RESP)) == 1


@pytest.mark.parametrize("backend", BACKENDS)
def test_guardar_una_hospitalizacion_inexistente_falla(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    fantasma = Hospitalizacion(
        hospitalizacion_id="X", mascota_id="M1", motivo="a", ingresada_en=HORA)
    with entorno.fabrica() as uow, pytest.raises(NoEncontrado):
        uow.hospitalizaciones.guardar(fantasma)
