# ADR-10 — Configuración por variables de entorno y despliegue en contenedor

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | La rúbrica exige 12-factor y un despliegue funcional con Swagger UI. |
| Alternativas | Archivos de configuración versionados; variables de entorno. |
| Decisión | Toda la configuración sale del entorno (`DATABASE_URL`, `DATA_DIR`, `PORT`); `.env.example` documenta las variables y no se versionan secretos. El contenedor siembra los datos al iniciar (idempotente) y escucha en `$PORT`. Se acepta el esquema `postgres://` que entregan algunas plataformas. |
| Consecuencias | Mismo artefacto en local, CI y la nube. Costo: la plataforma debe proveer PostgreSQL y `DATABASE_URL`. |
| Trazabilidad | `infrastructure/config.py`, `Dockerfile`, `docs/despliegue.md`. |
