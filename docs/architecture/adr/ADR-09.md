# ADR-09 — Alcance implementado: CU-01, CU-03 y CU-05; CU-02 y CU-04 fuera

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | El diseño de la Unidad 3 modela cinco casos de uso. El tiempo del proyecto permitió implementar con profundidad tres de ellos (dominio, base de datos, API, pruebas y CI). |
| Alternativas | (a) Implementar los cinco con poca profundidad. (b) Implementar tres con profundidad completa y documentar los otros dos como diseño. |
| Decisión | Opción (b). CU-02 (Generar nota clínica, expediente) y CU-04 (Hospitalización) se conservan como diseño y quedan marcados como *no implementados* en los diagramas y en la matriz de trazabilidad. El código no los menciona ni los simula. |
| Consecuencias | Cobertura de 98.8 % sobre lo que existe y trazabilidad honesta. Costo: NB-10 a NB-13, NB-18 y NB-21 quedan sin implementar; son el trabajo siguiente natural. |
| Trazabilidad | Ver `docs/alcance_implementado.md` y `docs/architecture/trazabilidad.md`. |
