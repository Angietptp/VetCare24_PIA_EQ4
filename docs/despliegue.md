# Despliegue

La aplicación se despliega como contenedor Docker (etapa `runtime` del `Dockerfile`) con una base PostgreSQL administrada. Al iniciar, el contenedor crea el esquema, carga los datos del paquete si la base está vacía (idempotente) y escucha en `$PORT`.

## Variables de entorno

| Variable | Valor | Quién la define |
|---|---|---|
| `DATABASE_URL` | URL de PostgreSQL (`postgresql://` o `postgres://`) | La plataforma, desde su base administrada |
| `PORT` | Puerto HTTP | La plataforma |
| `DATA_DIR` | `/app/data/alumno` (ya es el valor por defecto de la imagen) | Opcional |

No se versionan secretos: `.env` está en `.gitignore` y `.env.example` solo trae valores de desarrollo.

## Opción A: Render

1. Crear cuenta en render.com y conectar GitHub.
2. *New → PostgreSQL* (plan gratuito) y copiar la **Internal Database URL**.
3. *New → Web Service* con el repositorio; *Runtime: Docker*; no hace falta indicar target (ver la nota sobre la etapa Docker al final).
4. En *Environment* añadir `DATABASE_URL` con la URL del paso 2.
5. *Health Check Path*: `/health`.
6. Al terminar el despliegue abrir `https://<servicio>.onrender.com/docs` (Swagger UI) y copiar esa URL al README.

También se incluye `render.yaml` (Blueprint) que crea la base y el servicio juntos: *New → Blueprint* y elegir el repositorio.

## Opción B: Railway

1. *New Project → Deploy from GitHub repo*.
2. *Add → Database → PostgreSQL*.
3. En el servicio de la aplicación, variable `DATABASE_URL` = referencia a la variable de la base (`${{Postgres.DATABASE_URL}}`).
4. *Settings → Networking → Generate Domain* y abrir `/docs`.

## Opción C: Fly.io

```bash
fly launch --no-deploy            # detecta el Dockerfile
fly postgres create && fly postgres attach <app-db>   # define DATABASE_URL (postgres://, soportado)
fly deploy
```

## Verificación

```bash
curl https://<URL_DESPLEGADA>/health                       # {"status":"ok"}
curl -H "X-Rol: recepcion" https://<URL_DESPLEGADA>/servicios
```

Swagger UI queda en `/docs` y el contrato en `/openapi.json`.

## Nota sobre la etapa Docker

El `Dockerfile` define tres etapas: `runtime` (la API), `dev` (agrega pruebas; la usa el servicio `tests` de Compose) y `prod`, que es la **última** y por eso la que construyen las plataformas que no permiten elegir el *target*. Así el despliegue siempre ejecuta la API y nunca `pytest`.
