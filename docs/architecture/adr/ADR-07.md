# ADR-07 — Máquina de estados de Cita y momento de consumo de capacidad

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | El paquete del profesor proponía un flujo literal que contradice el BPMN y NB-08. |
| Alternativas | Consumir capacidad al solicitar, al confirmar o al realizar. |
| Decisión | SOLICITADA → CONFIRMADA → REALIZADA; cancelar desde SOLICITADA o CONFIRMADA; REALIZADA y CANCELADA son terminales. La capacidad se verifica y consume al confirmar; cancelar la libera (D-07, D-08, D-12). La tabla `TRANSICIONES` es la única fuente de verdad. |
| Consecuencias | Transiciones inválidas responden 409. Costo: D-08 es una interpretación aislada en un servicio de dominio (cambiarla es barato). |
| Trazabilidad | NB-08; D-07, D-08, D-12. Código: `domain/ciclo_de_vida.py`, `disponibilidad.py`. Pruebas: `test_ciclo_de_vida.py`, `test_disponibilidad.py`. Diagrama: `diagrams/08_estados_cita.png`. |
