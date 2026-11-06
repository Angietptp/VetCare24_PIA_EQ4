# ADR-04 — Dónde se verifican los permisos por rol

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | Recepción administra citas y datos administrativos (R-01); los permisos siguen las responsabilidades de cada rol (R-09, R-14, NB-20). La autenticación queda fuera del dominio. |
| Alternativas | (a) Todo en el dominio: acopla agregados a usuarios. (b) Todo en la aplicación: R-03 podría eludirse. (c) Mixto. |
| Decisión | Opción (c): `exigir(rol, Permiso)` es el primer paso de cada caso de uso (antes de abrir la transacción); el rol llega en el encabezado `X-Rol`. Matriz rol→permisos en `application/control_de_acceso.py`. La invariante de autoría de notas clínicas (R-03) queda diseñada pero no implementada (CU-02 fuera de alcance). |
| Consecuencias | Dominio libre de autenticación. Costo: el encabezado `X-Rol` no es autenticación real; se documenta como límite (ver README). |
| Trazabilidad | R-01, R-09, R-14; NB-20; A-15. Pruebas: `test_control_de_acceso.py`, `test_api.py` (401/403). |
