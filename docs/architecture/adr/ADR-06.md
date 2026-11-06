# ADR-06 — Stack tecnológico

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | Se necesita una API verificable, con base de datos real y contenedores reproducibles. |
| Alternativas | Django, Flask, FastAPI; ORM completo o SQL explícito. |
| Decisión | Python 3.12, FastAPI (OpenAPI/Swagger automático), Pydantic v2, SQL explícito sobre PostgreSQL 16 (psycopg) con SQLite para pruebas rápidas, pytest + pytest-cov (≥ 80 %), Ruff, Docker Compose y GitHub Actions. |
| Consecuencias | OpenAPI gratis y pruebas rápidas. Costo: el SQL se mantiene a mano con un adaptador de dialectos (`?` → `%s`). |
| Trazabilidad | Rúbrica del proyecto integrador. Código: `infrastructure/base_de_datos.py`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`. |
