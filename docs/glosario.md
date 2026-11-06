# Glosario de dominio — VetCare 24

Lenguaje ubicuo del equipo (Módulo Netacad 2). La columna final indica dónde vive cada término en el código.

| # | Término | Definición | Presencia en el código |
|---|---|---|---|
| 1 | Propietario | Persona física registrada en el sistema que posee la responsabilidad legal y financiera de una o más mascotas. | `domain/propietario.py` |
| 2 | Mascota | Animal doméstico registrado bajo el perfil de un Propietario que recibe servicios médicos o estéticos en la clínica. | `domain/mascota.py` |
| 3 | Expediente | Registro histórico centralizado y digital que concentra los datos biológicos, antecedentes, notas clínicas y tratamientos de una Mascota. | `domain/mascota.py`, `domain/vacunacion.py` y `domain/nota_clinica.py` (expediente = notas de la mascota, CU-02) |
| 4 | Especie | Clasificación biológica de la Mascota que determina dosis de medicamentos y esquemas de vacunación. | Atributo de `Mascota` |
| 5 | Raza | Subcategoría fenotípica de la Mascota relevante para identificar predisposiciones genéticas o requerimientos específicos. | Atributo de `Mascota` |
| 6 | Alergia | Incompatibilidad farmacológica o restricción médica crítica registrada en el Expediente que genera alertas al prescribir. | Atributo `alergias` de `Mascota`; sin alertas al prescribir (no hay recetas) |
| 7 | Cita Médica | Reserva de un bloque de tiempo y recurso clínico en la agenda para una atención médica, estética o de vacunación. | `domain/cita.py` (agregado raíz); sin bloques de tiempo (A-11) |
| 8 | Tipo de servicio | Categorización del servicio solicitado que define la duración y tarifa de la Cita Médica. | `domain/catalogo.py` (`ServicioVeterinario`: precio, capacidad) |
| 9 | Recepción | Rol operativo encargado de la agenda, recepción de la Mascota, registro de peso inicial y cobro de servicios. | Rol `recepcion` en `application/control_de_acceso.py` |
| 10 | Emergencia | Clasificación de prioridad médica que interrumpe el flujo normal de Citas Médicas programadas para atender mascotas en estado crítico. | `domain/emergencia.py` (agregado raíz, CU-05) |
| 11 | Peso Registrado | Métrica física tomada en la Recepción previo a la Consulta, indispensable para el cálculo de posología y dosis. | Atributo `peso_kg` de `Mascota` |
| 12 | Nota Clínica | Documento generado por el Veterinario durante la Consulta que detalla la anamnesis, examen físico y diagnóstico. | `domain/nota_clinica.py` (CU-02) |
| 13 | Esquema de Vacunación | Plan de inmunización de una Mascota que especifica vacunas aplicadas, lotes, fechas y próximas dosis requeridas. | `domain/vacunacion.py` (`EsquemaDeVacunacion`, `Vacunacion`) |
| 14 | Refuerzo de Vacuna | Dosis subsiguiente de un inmunológico requerida en una fecha futura para mantener la efectividad biológica. | `domain/seguimiento_vacunacion.py` |
| 15 | Recordatorio Automatizado | Notificación enviada al Propietario sobre próximas Citas Médicas o fechas límite para el Refuerzo de Vacuna. | `GET /vacunas/proximas` (cálculo por consulta; sin envío, decisión A-05) |
| 16 | Receta | Indicación médica emitida por el Veterinario que detalla medicamentos, posología, vía de administración y duración. | `domain/documentos_clinicos.py::Receta` |
| 17 | Orden de Estudios | Solicitud de análisis de laboratorio o gabinete necesarios para complementar un Diagnóstico. | `domain/documentos_clinicos.py::OrdenDeEstudio` |
| 18 | Hospitalización | Estado en el que la Mascota permanece internada en la clínica bajo cuidado y monitoreo continuo del Personal Clínico. | `domain/hospitalizacion.py` (CU-04) |
| 19 | Hoja de Monitoreo | Registro periódico de signos vitales, administración de fármacos y evolución de la Mascota en Hospitalización. | `domain/hospitalizacion.py::LecturaDeMonitoreo` (CU-04) |
| 20 | Personal Clínico | Rol operativo compuesto por médicos veterinarios, técnicos y auxiliares encargados de la atención médica directa. | Rol `personal_clinico` (decisión A-09: técnicos y auxiliares) |
