# VetCare 24 — Proyecto Integrador · Componentes de Lógica de Negocios

Lógica de negocio de una clínica veterinaria (citas, vacunación y emergencias) construida con **DDD**, arquitectura por capas, **FastAPI**, **PostgreSQL**, pruebas automatizadas y CI/CD.

| | |
|---|---|
| **Repositorio** | https://github.com/Angietptp/VetCare24_PIA_EQ4 |
| **Despliegue (Swagger UI)** | https://vetcare24-production.up.railway.app/docs |
| **Equipo 4** | García Cerda Randal Guillermo (2112493) · Sarmiento Hernández Cesar Martín (2119427) · Torres Pasillas Angela Susana (2101844) |
| **Curso / profesor** | Componentes de Lógica de Negocios · Miguel Ángel Gómez Marroquín |

## Alcance

Los cinco casos de uso están implementados de punta a punta (dominio, base de datos, API y pruebas): **CU-01 Solicitar cita**, **CU-02 Generar nota clínica (expediente)**, **CU-03 Registrar vacunación**, **CU-04 Registrar hospitalización** y **CU-05 Atender una emergencia**. También están implementados las recetas y órdenes de estudio, el cobro con entrega de documentación y el reporte de operación. Quedan fuera la factura fiscal, el envío real de recordatorios y la autenticación. Detalle: [`docs/alcance_implementado.md`](docs/alcance_implementado.md) y ADR-09.

## Documentación

| Tema | Ubicación |
|---|---|
| BRD, historias de usuario (20, con Gherkin), glosario, BPMN | [`docs/BRD.md`](docs/BRD.md) · [`docs/historias_de_usuario.md`](docs/historias_de_usuario.md) · [`docs/glosario.md`](docs/glosario.md) · [`docs/bpmn/`](docs/bpmn/README.md) |
| Arquitectura: diagramas (DDD, UML, secuencia, estados, ER, despliegue) | [`docs/architecture/diagrams/`](docs/architecture/diagrams/README.md) |
| ADR (10) y registro de decisiones | [`docs/architecture/adr/`](docs/architecture/adr/README.md) · [`docs/architecture/decisiones.md`](docs/architecture/decisiones.md) |
| Patrones y SOLID | [`docs/architecture/patrones_y_solid.md`](docs/architecture/patrones_y_solid.md) |
| **Trazabilidad** BRD → arquitectura → código → pruebas | [`docs/architecture/trazabilidad.md`](docs/architecture/trazabilidad.md) |
| Contrato OpenAPI | [`docs/api/openapi.json`](docs/api/openapi.json) (también en `/docs` del despliegue) |
| Evidencia (oráculo, escenarios por HTTP) | [`docs/evidencia/`](docs/evidencia/) |
| Despliegue | [`docs/despliegue.md`](docs/despliegue.md) |
| Reporte final (PDF) y presentación | [`docs/entrega/`](docs/entrega/) |
| Capturas de evidencia | [`docs/evidencias/`](docs/evidencias/README.md) |

## Estructura

```
src/vetcare24/
  domain/          reglas de negocio puras (agregados, Specifications, máquinas de estado, eventos)
  application/     casos de uso, comandos, permisos por rol, despachador de eventos
  infrastructure/  PostgreSQL/SQLite, repositorios SQL, importador de CSV, notificador, configuración
  api/             FastAPI + OpenAPI
tests/             pruebas (unitarias, de integración y de API)
docs/              BRD, arquitectura, ADR, API, evidencia, despliegue
.github/workflows/ CI/CD (lint, pruebas con cobertura >= 80 %, imagen Docker)
docker-compose.yml servicios db, app y tests
.env.example       variables de entorno (12-factor)
```

## Ejecutar con Docker Compose

```bash
cp .env.example .env
docker compose up --build                        # API + PostgreSQL; carga los datos al iniciar
# Swagger UI: http://localhost:8000/docs
docker compose --profile tests run --rm tests    # pruebas + cobertura (falla por debajo de 80 %)
```

Cada solicitud indica el rol en el encabezado `X-Rol` (`recepcion`, `veterinario`, `personal_clinico`, `responsable`). `X-Rol` modela los permisos por rol (ADR-04); **no es autenticación real**, que queda fuera de alcance.

## Calidad

Última medición completa: 584 pruebas, 98.81 % de cobertura (umbral exigido: 80 %), en SQLite y PostgreSQL 16; después se añadieron 2 pruebas para la normalización de la URL de la base. CI en cada pull request: `ruff`, `pytest` con PostgreSQL, evidencia (120 casos, 20 transiciones y 20 escenarios de emergencias) y construcción de la imagen.

## Ejecutar sin Docker
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
ruff check .
```

## Oráculo (Etapa 2)
Genera los resultados esperados de los 120 casos y las 20 transiciones en `docs/evidencia/`:
```bash
docker compose --profile tests run --rm tests python -m tests.oraculo
```
Sin Docker (PowerShell): `$env:PYTHONPATH="src"; python -m tests.oraculo`

## Evidencia de eventos (Etapa 6)
```bash
docker compose --profile tests run --rm tests python -m tests.evidencia_eventos
```
Sin Docker (PowerShell): `$env:PYTHONPATH="src"; python -m tests.evidencia_eventos`

## Base de datos (Etapa 7)
Cargar los CSV en la base de datos de la aplicación (crea el esquema si falta):
```bash
docker compose up -d db
docker compose run --rm app python -m vetcare24.infrastructure.sembrado
```
Las pruebas de persistencia corren en SQLite y, dentro de Docker Compose, también en PostgreSQL.

## API REST (Etapa 7)
Con `docker compose up --build` la documentación interactiva queda en http://localhost:8000/docs.
Cada solicitud indica el rol en el encabezado `X-Rol` (`recepcion`, `veterinario`, `personal_clinico`, `responsable`).
```bash
docker compose run --rm app python -m vetcare24.infrastructure.sembrado   # datos del paquete
curl -H "X-Rol: recepcion" http://localhost:8000/servicios
curl -H "X-Rol: recepcion" "http://localhost:8000/citas?estado=SOLICITADA"
curl -X POST -H "X-Rol: recepcion" http://localhost:8000/citas/CITA-XXXX/confirmar
```
Códigos de error: 400 solicitud mal formada, 401 falta rol, 403 sin permiso, 404 no existe, 409 transición inválida o capacidad insuficiente, 422 regla de negocio no cumplida (ver K en `docs/decisiones.md`).


## Evidencia de la API (Etapa 8)
```bash
docker compose --profile tests run --rm tests python -m tests.evidencia_api
docker compose --profile tests run --rm tests python -m vetcare24.api.exportar_openapi docs/evidencia/openapi.json
```
Genera `docs/evidencia/api_casos.csv`, `api_transiciones.csv` y `openapi.json`.
Las evaluaciones por HTTP: `GET /citas/{id}/evaluaciones/procesamiento` y `/beneficio`.

## Vacunación (Etapa 9)
Si tu base de desarrollo es de la versión anterior, reiníciala (la tabla de eventos cambió):
```bash
docker compose down -v
docker compose up -d db
docker compose run --rm app python -m vetcare24.infrastructure.sembrado
```
Endpoints: `POST/GET /mascotas/{id}/vacunaciones`, `GET /mascotas/{id}/vacunaciones/seguimiento`,
`GET /vacunas/proximas`, `GET /esquemas-vacunacion`.

## Emergencias (Etapa 10)
No hace falta reiniciar la base: al arrancar, la aplicación crea la tabla `emergencias` que falte.
Endpoints: `POST /emergencias` (Recepción), `POST /emergencias/{id}/iniciar-atencion` (personal clínico),
`GET /emergencias`, `GET /emergencias/{id}`, `GET /mascotas/{id}/evaluaciones/atencion`, `GET /avisos-veterinario`.
Evidencia (20 escenarios por HTTP):
```bash
docker compose --profile tests run --rm tests python -m tests.evidencia_emergencias
```
Sin Docker (PowerShell): `$env:PYTHONPATH="src"; python -m tests.evidencia_emergencias`

