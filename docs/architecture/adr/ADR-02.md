# ADR-02 — Referencias por identidad y una transacción por caso de uso

| Campo | Contenido |
|---|---|
| Estado | Aceptada |
| Contexto | Mascota es el ancla de citas, vacunación y emergencias, que la referencian por identidad (R-10, S-02). |
| Alternativas | (a) Mascota contiene colecciones de citas y vacunas: cargas y bloqueos grandes. (b) Cada agregado referencia a la mascota por su identidad y cada operación modifica un solo agregado. |
| Decisión | Opción (b), con `UnidadDeTrabajo` que abre tras autorizar y confirma o revierte la operación completa. |
| Consecuencias | Agregados pequeños y transacciones simples. Costo: la consistencia entre agregados no es transaccional; la existencia de la mascota se verifica al inicio del caso de uso. El criterio para evitar mascotas duplicadas (P-02, CR-2) sigue sin definirse. |
| Trazabilidad | R-10, S-01, S-02; NB-03; CR-1, CR-2. Código: `application/puertos.py`, `infrastructure/repositorios_sql.py`. Pruebas: `test_servicios_de_aplicacion.py`, `test_repositorios_sql.py`. |
