"""API de CU-02 (expediente clínico) y CU-04 (hospitalización), SQLite y PostgreSQL si hay."""

import pytest
from fastapi.testclient import TestClient

from tests.bd import BACKENDS, preparar, sembrar_basico
from vetcare24.api.main import create_app

RECEPCION = {"X-Rol": "recepcion"}
VET = {"X-Rol": "veterinario"}
CLINICO = {"X-Rol": "personal_clinico"}
RESP = {"X-Rol": "responsable"}


def _cliente(backend, tmp_path):
    url = preparar(backend, tmp_path)
    sembrar_basico(url)
    return TestClient(create_app(url, preparar_esquema=False))


def _codigo(respuesta):
    return respuesta.json()["error"]["codigo"]


# --- CU-02 ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_nota_clinica_y_expediente(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET, json={
        "diagnostico": "  Otitis  externa ", "indicaciones": "Limpieza diaria"})
    assert r.status_code == 201, r.text
    nota = r.json()
    assert (nota["diagnostico"], nota["mascota_id"], nota["cita_id"]) == (
        "Otitis externa", "M1", None)
    assert nota["nota_id"].startswith("NOTA-")
    assert c.get(f"/notas-clinicas/{nota['nota_id']}", headers=CLINICO).json() == nota
    c.post("/mascotas/M1/notas-clinicas", headers=VET, json={"diagnostico": "Control"})
    expediente = c.get("/mascotas/M1/expediente", headers=RESP).json()
    assert expediente["mascota_id"] == "M1"
    assert [n["diagnostico"] for n in expediente["notas"]] == ["Otitis externa", "Control"]


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_del_expediente(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    cuerpo = {"diagnostico": "X"}
    assert c.post("/mascotas/M1/notas-clinicas", json=cuerpo).status_code == 401
    r = c.post("/mascotas/M1/notas-clinicas", headers=RECEPCION, json=cuerpo)
    assert (r.status_code, _codigo(r)) == (403, "ACCESO_DENEGADO")
    assert c.get("/mascotas/M1/expediente", headers=RECEPCION).status_code == 403
    r = c.post("/mascotas/NOPE/notas-clinicas", headers=VET, json=cuerpo)
    assert (r.status_code, _codigo(r)) == (404, "NO_ENCONTRADO")
    assert c.get("/mascotas/NOPE/expediente", headers=VET).status_code == 404
    assert c.get("/notas-clinicas/NOPE", headers=VET).status_code == 404
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET, json={"diagnostico": "  "})
    assert (r.status_code, _codigo(r)) == (422, "DIAGNOSTICO_VACIO")
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET, json={})
    assert (r.status_code, _codigo(r)) == (400, "SOLICITUD_INVALIDA")
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET, json={**cuerpo, "cita_id": "NOPE"})
    assert r.status_code == 404
    c.post("/mascotas/M1/notas-clinicas", headers=VET, json={**cuerpo, "nota_id": "N-1"})
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET, json={**cuerpo, "nota_id": "N-1"})
    assert (r.status_code, _codigo(r)) == (409, "YA_EXISTE")


@pytest.mark.parametrize("backend", BACKENDS)
def test_nota_con_cita_no_realizada_responde_422(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    r = c.post("/citas", headers=RECEPCION, json={
        "propietario_id": "P1", "mascota_id": "M1", "servicios": [{"servicio_id": "S1",
                                                                  "cantidad": 1}],
        "fecha_solicitud": "2026-10-02", "autorizada": True, "cita_id": "C1"})
    assert r.status_code == 201, r.text
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET,
               json={"diagnostico": "X", "cita_id": "C1"})
    assert (r.status_code, _codigo(r)) == (422, "PRECONDICION_NO_CUMPLIDA")
    assert r.json()["error"]["motivos"] == ["CITA_NO_REALIZADA"]
    c.post("/citas/C1/confirmar", headers=RECEPCION)
    c.post("/citas/C1/realizar", headers=VET)
    r = c.post("/mascotas/M1/notas-clinicas", headers=VET,
               json={"diagnostico": "X", "cita_id": "C1"})
    assert r.status_code == 201 and r.json()["cita_id"] == "C1"


# --- CU-04 ---

@pytest.mark.parametrize("backend", BACKENDS)
def test_ciclo_de_hospitalizacion_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    r = c.post("/hospitalizaciones", headers=VET,
               json={"mascota_id": "M1", "motivo": "Deshidratación"})
    assert r.status_code == 201, r.text
    h = r.json()
    assert (h["estado"], h["hoja_de_monitoreo"], h["alta_en"]) == ("INGRESADA", [], None)
    ruta = f"/hospitalizaciones/{h['hospitalizacion_id']}"
    r = c.post(f"{ruta}/monitoreo", headers=CLINICO, json={
        "observaciones": "Estable", "temperatura_c": "38.6", "frecuencia_cardiaca": 110})
    assert r.status_code == 201, r.text
    (lectura,) = r.json()["hoja_de_monitoreo"]
    assert (lectura["temperatura_c"], lectura["frecuencia_cardiaca"]) == ("38.6", 110)
    r = c.post(f"{ruta}/alta", headers=VET, json={"resumen_alta": "Recuperada"})
    assert r.status_code == 200 and r.json()["estado"] == "ALTA"
    assert c.get(ruta, headers=RESP).json()["resumen_alta"] == "Recuperada"
    assert [x["estado"] for x in c.get(
        "/hospitalizaciones?mascota_id=M1", headers=VET).json()] == ["ALTA"]
    assert c.get("/hospitalizaciones?estado=INGRESADA", headers=VET).json() == []


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_de_hospitalizacion(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    cuerpo = {"mascota_id": "M1", "motivo": "x"}
    assert c.post("/hospitalizaciones", json=cuerpo).status_code == 401
    for cabecera in (RECEPCION, RESP):
        assert c.post("/hospitalizaciones", headers=cabecera, json=cuerpo).status_code == 403
    r = c.post("/hospitalizaciones", headers=VET, json={"mascota_id": "NOPE", "motivo": "x"})
    assert r.status_code == 404
    r = c.post("/hospitalizaciones", headers=VET, json={"mascota_id": "M1"})
    assert r.status_code == 400
    h = c.post("/hospitalizaciones", headers=VET, json={**cuerpo, "hospitalizacion_id": "H-1"})
    assert h.status_code == 201
    r = c.post("/hospitalizaciones", headers=VET, json={**cuerpo, "hospitalizacion_id": "H-1"})
    assert (r.status_code, _codigo(r)) == (409, "YA_EXISTE")
    r = c.post("/hospitalizaciones", headers=VET, json=cuerpo)
    assert (r.status_code, _codigo(r)) == (422, "PRECONDICION_NO_CUMPLIDA")
    assert r.json()["error"]["motivos"] == ["MASCOTA_YA_HOSPITALIZADA"]
    r = c.post("/hospitalizaciones/H-1/monitoreo", headers=VET,
               json={"observaciones": "x", "temperatura_c": "60"})
    assert (r.status_code, _codigo(r)) == (422, "TEMPERATURA_INVALIDA")
    r = c.post("/hospitalizaciones/H-1/monitoreo", headers=RECEPCION,
               json={"observaciones": "x"})
    assert r.status_code == 403
    r = c.post("/hospitalizaciones/H-1/alta", headers=VET, json={"resumen_alta": " "})
    assert (r.status_code, _codigo(r)) == (422, "RESUMEN_ALTA_VACIO")
    r = c.post("/hospitalizaciones/H-1/alta", headers=CLINICO, json={"resumen_alta": "ok"})
    assert r.status_code == 403
    assert c.post("/hospitalizaciones/H-1/alta", headers=VET,
                  json={"resumen_alta": "ok"}).status_code == 200
    r = c.post("/hospitalizaciones/H-1/alta", headers=VET, json={"resumen_alta": "ok"})
    assert (r.status_code, _codigo(r)) == (409, "TRANSICION_INVALIDA")
    assert "dada de alta" in r.json()["error"]["mensaje"]
    r = c.post("/hospitalizaciones/H-1/monitoreo", headers=VET, json={"observaciones": "x"})
    assert (r.status_code, _codigo(r)) == (409, "TRANSICION_INVALIDA")
    assert c.get("/hospitalizaciones/NOPE", headers=VET).status_code == 404
    assert c.get("/hospitalizaciones", headers=RECEPCION).status_code == 403


def test_el_contrato_openapi_documenta_expediente_y_hospitalizacion(tmp_path):
    contrato = create_app(f"sqlite:///{tmp_path / 'c.db'}").openapi()
    rutas = contrato["paths"]
    esperadas = {
        "/mascotas/{mascota_id}/notas-clinicas", "/mascotas/{mascota_id}/expediente",
        "/notas-clinicas/{nota_id}", "/hospitalizaciones",
        "/hospitalizaciones/{hospitalizacion_id}",
        "/hospitalizaciones/{hospitalizacion_id}/monitoreo",
        "/hospitalizaciones/{hospitalizacion_id}/alta"}
    assert esperadas <= set(rutas)
    assert rutas["/hospitalizaciones"]["post"]["tags"] == ["Hospitalización"]
    assert rutas["/mascotas/{mascota_id}/notas-clinicas"]["post"]["tags"] == [
        "Expediente clínico"]


# --- US10, US13, US14 ---

def _cita_realizada(c):
    r = c.post("/citas", headers=RECEPCION, json={
        "propietario_id": "P1", "mascota_id": "M1", "fecha_solicitud": "2026-10-02",
        "autorizada": True, "servicios": [{"servicio_id": "S1", "cantidad": 3}],
        "cita_id": "C1"})
    assert r.status_code == 201, r.text
    c.post("/citas/C1/confirmar", headers=RECEPCION)
    c.post("/citas/C1/realizar", headers=VET)


@pytest.mark.parametrize("backend", BACKENDS)
def test_recetas_y_ordenes_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    r = c.post("/mascotas/M1/recetas", headers=VET, json={
        "medicamentos": [{"nombre": "Amoxicilina", "dosis": "250 mg", "indicaciones": "7 días"}]})
    assert r.status_code == 201, r.text
    receta = r.json()
    assert receta["medicamentos"][0]["nombre"] == "Amoxicilina"
    assert c.get(f"/recetas/{receta['receta_id']}", headers=RESP).json() == receta
    r = c.post("/mascotas/M1/ordenes-estudio", headers=VET, json={"estudio": "Rayos X"})
    assert r.status_code == 201, r.text
    orden = r.json()
    assert c.get(f"/ordenes-estudio/{orden['orden_id']}", headers=CLINICO).json() == orden
    exp = c.get("/mascotas/M1/expediente", headers=VET).json()
    assert [x["receta_id"] for x in exp["recetas"]] == [receta["receta_id"]]
    assert [x["orden_id"] for x in exp["ordenes_de_estudio"]] == [orden["orden_id"]]


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_de_recetas_y_ordenes_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    cuerpo = {"medicamentos": [{"nombre": "A", "dosis": "1"}]}
    assert c.post("/mascotas/M1/recetas", headers=RECEPCION, json=cuerpo).status_code == 403
    assert c.post("/mascotas/NOPE/recetas", headers=VET, json=cuerpo).status_code == 404
    r = c.post("/mascotas/M1/recetas", headers=VET, json={"medicamentos": []})
    assert (r.status_code, _codigo(r)) == (422, "RECETA_SIN_MEDICAMENTOS")
    r = c.post("/mascotas/M1/recetas", headers=VET, json={})
    assert r.status_code == 400
    r = c.post("/mascotas/M1/ordenes-estudio", headers=VET, json={"estudio": " "})
    assert (r.status_code, _codigo(r)) == (422, "ESTUDIO_VACIO")
    assert c.post("/mascotas/M1/ordenes-estudio", headers=CLINICO,
                  json={"estudio": "x"}).status_code == 403
    assert c.get("/recetas/NOPE", headers=VET).status_code == 404
    assert c.get("/ordenes-estudio/NOPE", headers=VET).status_code == 404


@pytest.mark.parametrize("backend", BACKENDS)
def test_cobro_y_entrega_de_documentacion_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    r = c.post("/citas", headers=RECEPCION, json={
        "propietario_id": "P1", "mascota_id": "M1", "fecha_solicitud": "2026-10-02",
        "autorizada": True, "servicios": [{"servicio_id": "S1", "cantidad": 3}],
        "cita_id": "C1"})
    assert r.status_code == 201, r.text
    r = c.post("/citas/C1/cobro", headers=RECEPCION, json={"metodo": "tarjeta"})
    assert (r.status_code, _codigo(r)) == (422, "PRECONDICION_NO_CUMPLIDA")  # aún no realizada
    c.post("/citas/C1/confirmar", headers=RECEPCION)
    c.post("/citas/C1/realizar", headers=VET)
    r = c.post("/citas/C1/documentacion", headers=RECEPCION)
    assert r.status_code == 422 and r.json()["error"]["motivos"] == ["CITA_SIN_COBRO"]
    r = c.post("/citas/C1/cobro", headers=RECEPCION, json={"metodo": "tarjeta"})
    assert r.status_code == 201, r.text
    assert (r.json()["total_mxn"], r.json()["metodo"]) == ("900.00", "tarjeta")
    assert c.get("/citas/C1/cobro", headers=RESP).json()["cobro_id"] == r.json()["cobro_id"]
    r2 = c.post("/citas/C1/cobro", headers=RECEPCION, json={"metodo": "efectivo"})
    assert r2.status_code == 422 and r2.json()["error"]["motivos"] == ["CITA_YA_COBRADA"]
    c.post("/mascotas/M1/notas-clinicas", headers=VET,
           json={"diagnostico": "Otitis", "cita_id": "C1"})
    c.post("/mascotas/M1/recetas", headers=VET, json={
        "medicamentos": [{"nombre": "A", "dosis": "1"}], "cita_id": "C1"})
    d = c.post("/citas/C1/documentacion", headers=RECEPCION)
    assert d.status_code == 200, d.text
    cuerpo = d.json()
    assert cuerpo["cobro"]["total_mxn"] == "900.00"
    assert (len(cuerpo["notas"]), len(cuerpo["recetas"]), len(cuerpo["ordenes_de_estudio"])) == (
        1, 1, 0)


@pytest.mark.parametrize("backend", BACKENDS)
def test_errores_del_cobro_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    _cita_realizada(c)
    assert c.post("/citas/C1/cobro", headers=VET, json={"metodo": "efectivo"}).status_code == 403
    assert c.post("/citas/C1/documentacion", headers=VET).status_code == 403
    assert c.get("/citas/C1/cobro", headers=CLINICO).status_code == 403
    r = c.post("/citas/C1/cobro", headers=RECEPCION, json={"metodo": "oro"})
    assert (r.status_code, _codigo(r)) == (422, "METODO_INVALIDO")
    assert c.post("/citas/C1/cobro", headers=RECEPCION, json={}).status_code == 400
    assert c.post("/citas/NOPE/cobro", headers=RECEPCION,
                  json={"metodo": "efectivo"}).status_code == 404
    assert c.get("/citas/C1/cobro", headers=RECEPCION).status_code == 404
    assert c.post("/citas/NOPE/documentacion", headers=RECEPCION).status_code == 404


@pytest.mark.parametrize("backend", BACKENDS)
def test_reporte_de_operacion_por_http(backend, tmp_path):
    c = _cliente(backend, tmp_path)
    _cita_realizada(c)
    c.post("/citas/C1/cobro", headers=RECEPCION, json={"metodo": "efectivo"})
    r = c.get("/reportes/operacion", headers=RESP)
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert cuerpo["citas_por_estado"]["REALIZADA"] == 1
    assert (cuerpo["cobros_registrados"], cuerpo["ingresos_mxn"]) == (1, "900.00")
    assert cuerpo["ingresos_por_metodo"] == {"efectivo": "900.00"}
    for cabecera in (RECEPCION, VET, CLINICO):
        assert c.get("/reportes/operacion", headers=cabecera).status_code == 403
    assert c.get("/reportes/operacion").status_code == 401
