# ADR-01 — Selección de Domain Model como patrón de lógica de negocio

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | La atención combina reglas que cruzan conceptos: la cita depende del servicio y la disponibilidad (NB-06, NB-07, R-05); el historial y el esquema validado gobiernan el seguimiento de vacunas (R-11, R-12); la emergencia puede existir sin cita (R-06). |
| Alternativas | Transaction Script (simple, pero repite reglas); Table Module (útil para reportes, débil para invariantes); Domain Model (reglas junto a los objetos, a cambio de más diseño). |
| Decisión | Domain Model. Cada regla vive en el objeto que la protege (`domain/`), sin dependencias de FastAPI ni de la base de datos. Implementado para CU-01, CU-03 y CU-05 (ver ADR-09). |
| Consecuencias | Reglas únicas y verificables con el negocio. Costos: más clases, Repository y Unit of Work, y riesgo de sobrediseño en datos administrativos. |
| Trazabilidad | NB-06, NB-07, NB-14, NB-15, NB-19; R-05, R-06, R-11, R-12; US04, US15, US20. Código: `domain/`. Pruebas: `test_dominio.py`, `test_reglas_cita.py`, `test_ciclo_de_vida.py`. |
