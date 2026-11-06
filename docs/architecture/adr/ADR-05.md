# ADR-05 — Esquema de vacunación como concepto de referencia

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | R-12 y NB-15 hablan de la frecuencia o esquema de cada vacuna, definido y validado antes de usarse. |
| Alternativas | (a) Esquema como atributo de cada Vacunación. (b) Esquema como definición de referencia consultada por el seguimiento. (c) Impedir el registro sin esquema validado. |
| Decisión | Opción (b). El registro de la vacunación nunca depende del esquema; sin esquema validado el seguimiento queda `pendiente_de_esquema`. Corrección posterior (M-05): `SeguimientoCalculable = EsquemaDefinido AND EsquemaValidado`. |
| Consecuencias | Historial siempre completo (R-11). Costo: la fórmula de la próxima aplicación es una propuesta por validar (M-04). |
| Trazabilidad | NB-14, NB-15, NB-16; R-11, R-12, R-13; US15. Código: `domain/vacunacion.py`, `reglas_vacunacion.py`, `seguimiento_vacunacion.py`. Pruebas: `test_reglas_vacunacion.py`, `test_seguimiento_vacunacion.py`. |
