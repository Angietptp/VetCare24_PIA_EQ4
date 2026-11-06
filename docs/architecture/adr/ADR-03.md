# ADR-03 — CQRS básico: comandos en Application Services y consultas con puertos de lectura

| Campo | Contenido |
|---|---|
| Estado | Aceptada con alcance reducido |
| Contexto | El personal necesita encontrar rápido antecedentes y citas (NB-11, CR-1; P-03; US07). |
| Alternativas | (a) Los Application Services devuelven agregados para consultar. (b) Un bus de comandos y consultas. (c) Comandos en Application Services y consultas en Query Handlers con View Models. |
| Decisión | Opción (c) a nivel de diseño. En el código entregado, cada servicio de aplicación separa métodos de comando (que abren una transacción y publican eventos) de métodos de consulta (`obtener`, `listar`, `evaluar_*`) que no cambian estado; no existen Query Handlers ni puertos de lectura independientes (se difirieron junto con CU-02). No se introduce un bus. |
| Consecuencias | Las consultas no modifican el estado y respetan los permisos. Costo: el modelo de lectura aún no diverge del de escritura. |
| Trazabilidad | NB-11, NB-06; R-14; US07; CR-1. Código: `application/servicios*.py`. |
