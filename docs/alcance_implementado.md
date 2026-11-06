# Alcance implementado

![Alcance](architecture/diagrams/13_alcance.png)

## Resumen

| Caso de uso | Historias | Estado | Evidencia |
|---|---|---|---|
| CU-01 Solicitar cita | US04, US01, US02, US07 | **Implementado** (dominio, base de datos, API, pruebas) | 120 casos y 20 transiciones del paquete, 33+ pruebas de API |
| CU-03 Registrar vacunación | US15, US05 (vacunas) | **Implementado** | `test_servicios_vacunacion.py`, `test_seguimiento_vacunacion.py` |
| CU-05 Atender una emergencia | US20 | **Implementado** | 20 escenarios HTTP (`tests/api_emergencias.py`) |
| CU-02 Generar nota clínica (expediente) | US03, US11, US12 | **Implementado** | `test_expediente.py`, `test_api_clinica.py` |
| CU-04 Registrar hospitalización | US17, US18, US19 | **Implementado** | `test_hospitalizacion.py`, `test_api_clinica.py` |
| Cobro, documentación, recetas, órdenes y reportes | US10, US13, US14, NB-21 | **Implementado** | `test_cobro_y_documentos.py`, `test_api_clinica.py` |

## Complementos de los casos de uso

Para cerrar todas las tareas del BPMN se implementaron además: recetas y órdenes de estudio (US13, US14, dentro de CU-02), cobro de citas y entrega de documentación (US10, carril de Recepción) y el reporte de operación (NB-21, para el responsable). Decisiones O-10 a O-14 en `architecture/decisiones.md`.

## Qué sigue fuera del alcance

La factura fiscal (A-02), el cobro parcial o por abonos, el envío real de recordatorios, la autenticación real y la captura del motivo de consulta como flujo propio (US09, parcial). Son limitaciones declaradas.

## Diagramas y su relación con el código

Los diagramas de la Unidad 3 (mapa de dominio, clases y secuencias) se conservan; los nombres del diseño están en inglés/CamelCase y el código usa equivalentes en español:

| Diseño (Unidad 3) | Código |
|---|---|
| `CitasApplicationService` | `application/servicios.py::ServicioDeCitas` |
| `VacunacionApplicationService` | `application/servicios_vacunacion.py::ServicioDeVacunacion` |
| `EmergenciasApplicationService` | `application/servicios_emergencias.py::ServicioDeEmergencias` |
| `ExpedienteApplicationService` | `application/servicios_expediente.py::ServicioDeExpediente` |
| `HospitalizacionApplicationService` | `application/servicios_hospitalizacion.py::ServicioDeHospitalizacion` |
| `ExpedienteClinico` / `NotaClinica` | `domain/nota_clinica.py::NotaClinica` (el expediente es la lista de notas de la mascota) |
| `Hospitalizacion` / hoja de monitoreo | `domain/hospitalizacion.py::Hospitalizacion` y `LecturaDeMonitoreo` |
| `UnitOfWork` / `UnitOfWorkImpl` | `application/puertos.py::UnidadDeTrabajo` / `infrastructure/repositorios_sql.py::UnidadDeTrabajoSql` |
| `ControlDeAcceso` | `application/control_de_acceso.py` |
| `ServicioDeProgramacionDeCitas` | `domain/ciclo_de_vida.py` + `domain/disponibilidad.py` |
| `ServicioDeSeguimientoDeVacunacion` | `domain/seguimiento_vacunacion.py` |
| `NotificadorDeVeterinario` | `application/puertos.py` / `infrastructure/notificador.py::BandejaDeAvisos` |

Diagramas nuevos (fuente Mermaid en `architecture/diagrams/*.mmd`): arquitectura por capas, despliegue, máquinas de estado de Cita, Emergencia y Hospitalización, secuencias de CU-05 y CU-04, modelo entidad-relación y Specifications.
