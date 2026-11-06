"""CU-02: nota clínica y expediente (dominio, servicio y persistencia), SQLite y PostgreSQL."""

from datetime import UTC, date, datetime

import pytest

from tests.bd import BACKENDS, HORA, armar, preparar, sembrar_basico
from vetcare24.application.comandos import RegistrarNotaClinica, SolicitarCita
from vetcare24.application.control_de_acceso import Rol
from vetcare24.application.errores import AccesoDenegado, NoEncontrado, YaExiste
from vetcare24.domain.errors import InvarianteViolada, PrecondicionNoCumplida
from vetcare24.domain.eventos import NotaClinicaRegistrada
from vetcare24.domain.mascota import Mascota
from vetcare24.domain.nota_clinica import NotaClinica, RegistroClinico

VET, RECEPCION, CLINICO, RESP = (
    Rol.VETERINARIO, Rol.RECEPCION, Rol.PERSONAL_CLINICO, Rol.RESPONSABLE)


def _entorno(backend, tmp_path):
    url = preparar(backend, tmp_path)
    sembrar_basico(url)
    return armar(url)


def _cita_realizada(entorno):
    entorno.citas.solicitar(RECEPCION, SolicitarCita(
        propietario_id="P1", mascota_id="M1", servicios=(("S1", 1),),
        fecha_solicitud=date(2026, 10, 2), autorizada=True, cita_id="C1"))
    entorno.citas.confirmar(RECEPCION, "C1")
    entorno.citas.realizar(VET, "C1")


# --- dominio ---

def test_la_nota_se_normaliza_y_emite_su_evento():
    mascota = Mascota(mascota_id="M1", propietario_id="P1", nombre="Rex", especie="Perro")
    nota = RegistroClinico(lambda: HORA).registrar(
        nota_id="N1", mascota=mascota, diagnostico="  Otitis   externa ")
    assert (nota.diagnostico, nota.indicaciones, nota.cita_id) == ("Otitis externa", None, None)
    (evento,) = nota.extraer_eventos()
    assert isinstance(evento, NotaClinicaRegistrada)
    assert (evento.nota_id, evento.mascota_id, evento.agregado_id) == ("N1", "M1", "N1")
    assert nota.extraer_eventos() == ()


@pytest.mark.parametrize("campos,codigo", [
    ({"nota_id": " "}, "ID_VACIO"),
    ({"mascota_id": ""}, "MASCOTA_REQUERIDA"),
    ({"diagnostico": "  "}, "DIAGNOSTICO_VACIO"),
    ({"indicaciones": " "}, "INDICACIONES_VACIAS"),
    ({"cita_id": ""}, "CITA_REQUERIDA"),
    ({"registrada_en": datetime(2026, 1, 1)}, "FECHA_HORA_SIN_ZONA"),  # noqa: DTZ001
])
def test_la_nota_rechaza_datos_invalidos(campos, codigo):
    base = {"nota_id": "N1", "mascota_id": "M1", "diagnostico": "Sano",
            "registrada_en": datetime(2026, 1, 1, tzinfo=UTC)}
    with pytest.raises(InvarianteViolada) as error:
        NotaClinica(**{**base, **campos})
    assert error.value.codigo == codigo


def test_igualdad_y_repr_de_la_nota():
    a = NotaClinica(nota_id="N1", mascota_id="M1", diagnostico="A", registrada_en=HORA)
    b = NotaClinica(nota_id="N1", mascota_id="M2", diagnostico="B", registrada_en=HORA)
    assert a == b and hash(a) == hash(b) and a != "N1"
    assert "N1" in repr(a)


# --- servicio y persistencia ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_registrar_nota_la_guarda_y_publica_el_evento(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    nota = entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(
        mascota_id="M1", diagnostico="Otitis", indicaciones="Limpieza diaria"))
    guardada = entorno.expediente.obtener(CLINICO, nota.nota_id)
    assert (guardada.diagnostico, guardada.indicaciones, guardada.registrada_en) == (
        "Otitis", "Limpieza diaria", HORA)
    (registrado,) = entorno.eventos.registrados
    assert isinstance(registrado.evento, NotaClinicaRegistrada)
    with entorno.fabrica() as uow:
        assert [e["evento"] for e in uow.eventos.todos()] == ["NotaClinicaRegistrada"]


@pytest.mark.parametrize("backend", BACKENDS)
def test_el_expediente_lista_las_notas_en_orden_cronologico(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    for diagnostico in ("Primera", "Segunda", "Tercera"):
        entorno.expediente.registrar_nota(
            VET, RegistrarNotaClinica(mascota_id="M1", diagnostico=diagnostico))
        entorno.reloj.avanzar(hours=1)
    notas = entorno.expediente.expediente(RESP, "M1")
    assert [n.diagnostico for n in notas] == ["Primera", "Segunda", "Tercera"]
    assert entorno.expediente.expediente(VET, "M1")[0].registrada_en == HORA


@pytest.mark.parametrize("backend", BACKENDS)
def test_nota_ligada_a_una_cita_realizada(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita_realizada(entorno)
    nota = entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(
        mascota_id="M1", diagnostico="Revisión", cita_id="C1"))
    assert entorno.expediente.obtener(VET, nota.nota_id).cita_id == "C1"


@pytest.mark.parametrize("backend", BACKENDS)
def test_nota_con_cita_no_realizada_se_rechaza(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    entorno.citas.solicitar(RECEPCION, SolicitarCita(
        propietario_id="P1", mascota_id="M1", servicios=(("S1", 1),),
        fecha_solicitud=date(2026, 10, 2), autorizada=True, cita_id="C1"))
    with pytest.raises(PrecondicionNoCumplida) as error:
        entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(
            mascota_id="M1", diagnostico="X", cita_id="C1"))
    assert error.value.motivos == ("CITA_NO_REALIZADA",)
    assert entorno.expediente.expediente(VET, "M1") == []


@pytest.mark.parametrize("backend", BACKENDS)
def test_nota_con_cita_de_otra_mascota_se_rechaza(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    _cita_realizada(entorno)
    with entorno.fabrica() as uow:
        uow.mascotas.agregar(Mascota(
            mascota_id="M2", propietario_id="P1", nombre="Luna", especie="Gato"))
        uow.commit()
    with pytest.raises(PrecondicionNoCumplida) as error:
        entorno.expediente.registrar_nota(VET, RegistrarNotaClinica(
            mascota_id="M2", diagnostico="X", cita_id="C1"))
    assert error.value.motivos == ("CITA_DE_OTRA_MASCOTA",)


@pytest.mark.parametrize("backend", BACKENDS)
def test_referencias_inexistentes_y_duplicados(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    servicio = entorno.expediente
    with pytest.raises(NoEncontrado):
        servicio.registrar_nota(VET, RegistrarNotaClinica(mascota_id="NOPE", diagnostico="X"))
    with pytest.raises(NoEncontrado):
        servicio.registrar_nota(VET, RegistrarNotaClinica(
            mascota_id="M1", diagnostico="X", cita_id="NOPE"))
    with pytest.raises(NoEncontrado):
        servicio.obtener(VET, "NOPE")
    with pytest.raises(NoEncontrado):
        servicio.expediente(VET, "NOPE")
    servicio.registrar_nota(VET, RegistrarNotaClinica(
        mascota_id="M1", diagnostico="X", nota_id="N-9"))
    with pytest.raises(YaExiste):
        servicio.registrar_nota(VET, RegistrarNotaClinica(
            mascota_id="M1", diagnostico="Y", nota_id="N-9"))


@pytest.mark.parametrize("backend", BACKENDS)
def test_permisos_del_expediente(backend, tmp_path):
    entorno = _entorno(backend, tmp_path)
    servicio = entorno.expediente
    comando = RegistrarNotaClinica(mascota_id="M1", diagnostico="X")
    for rol in (RECEPCION, CLINICO, RESP):
        with pytest.raises(AccesoDenegado):
            servicio.registrar_nota(rol, comando)
    with pytest.raises(AccesoDenegado):
        servicio.expediente(RECEPCION, "M1")
    with pytest.raises(AccesoDenegado):
        servicio.obtener(RECEPCION, "N1")
    servicio.registrar_nota(VET, comando)
    for rol in (VET, CLINICO, RESP):
        assert len(servicio.expediente(rol, "M1")) == 1
