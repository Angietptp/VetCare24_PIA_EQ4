# ADR-09 — Alcance implementado: los cinco casos de uso (CU-01 a CU-05)

| Campo | Contenido |
|---|---|
| Estado | Aceptada (revisada en la Etapa 11; sustituye a la versión que dejaba CU-02 y CU-04 fuera) |
| Contexto | El diseño de la Unidad 3 modela cinco casos de uso. La primera versión de esta decisión implementó tres con profundidad (CU-01, CU-03, CU-05) y dejó CU-02 y CU-04 como diseño. Al revisar el informe se vio que dejar dos casos de uso sin código volvía difícil justificar el alcance. |
| Alternativas | (a) Mantener tres casos de uso y justificar la ausencia. (b) Implementar CU-02 y CU-04 con el mismo nivel de los demás: dominio, base de datos, API, pruebas y documentación. |
| Decisión | Opción (b). CU-02 (`NotaClinica`, `RegistroClinico`, `ServicioDeExpediente`) y CU-04 (`Hospitalizacion`, `CicloDeVidaDeHospitalizacion`, `ServicioDeHospitalizacion`) siguen los mismos patrones que los tres anteriores: agregados con constructor validante, tabla de transiciones, servicios de dominio con reloj inyectado, eventos publicados después del commit, repositorios SQL explícitos y errores con el contrato D-13. Las decisiones concretas están en `decisiones.md`, sección O. |
| Consecuencias | Los cinco casos de uso tienen código y pruebas. Después se cerraron también las tareas que el BPMN dejaba sin código: recetas y órdenes de estudio (US13, US14), cobro y entrega de documentación (US10) y el reporte de operación (NB-21). Siguen fuera de alcance la factura fiscal (A-02), los envíos reales de recordatorios y la autenticación; el informe los declara como limitaciones. |
| Trazabilidad | Ver `docs/alcance_implementado.md` y `docs/architecture/trazabilidad.md`. |
