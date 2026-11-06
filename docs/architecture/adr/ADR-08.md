# ADR-08 — Adaptador del paquete de pruebas del profesor

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | Los CSV (60 operaciones, 120 casos, 20 transiciones) son un modelo de pruebas, no el dominio. |
| Alternativas | Importar directo al dominio; usar los CSV solo como fixtures sueltos. |
| Decisión | El paquete entra por `infrastructure/adaptador_paquete.py` y `csv_loader.py`; el dominio no conoce los CSV. Un oráculo independiente (`tests/oraculo.py`) evalúa el texto de cada regla sobre las filas del CSV (D-15). |
| Consecuencias | El dominio queda limpio y los 120 casos y 20 transiciones se verifican por API. Costo: interpretaciones como D-11 deben confirmarse con el profesor. |
| Trazabilidad | D-01 a D-15. Pruebas: `test_adaptador_paquete.py`, `test_oraculo.py`, `test_api_paquete.py`, `test_u5_matriz.py`. |
