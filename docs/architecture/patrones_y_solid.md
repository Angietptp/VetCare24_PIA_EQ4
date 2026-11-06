# Patrones de diseño y principios SOLID aplicados

## Patrones

| Patrón | Dónde | Por qué |
|---|---|---|
| Domain Model (ADR-01) | `domain/` | Las reglas viven en los agregados `Cita`, `Mascota`, `Propietario`, `Vacunacion`, `Emergencia` |
| Aggregate Root | `Cita` (líneas de servicio), `Emergencia`, `Vacunacion` | Una operación modifica un solo agregado (ADR-02) |
| Value Object | `Money` (Decimal, 2 decimales, ROUND_HALF_UP), `ServicioSolicitado` | Igualdad por valor e inmutabilidad |
| Specification | `domain/specification.py`, `reglas_*.py` | Reglas componibles con AND/OR/NOT que explican por qué fallan (`Evaluacion.motivos`) |
| State (tabla de transiciones) | `ciclo_de_vida.py` | `TRANSICIONES` es la única fuente de verdad de los estados (ADR-07) |
| Repository | `application/puertos.py` + `infrastructure/repositorios_sql.py` | El dominio no conoce SQL |
| Unit of Work | `UnidadDeTrabajoSql` | Una transacción por caso de uso; commit o rollback completo (ADR-02) |
| Domain Events + Observer | `eventos.py`, `Despachador` | Los eventos se guardan y se publican tras el commit; un manejador que falla no detiene a los demás |
| Ports & Adapters (hexagonal) | `puertos.py` frente a `infrastructure/` | El dominio y la aplicación no dependen de FastAPI ni de la base de datos |
| Adapter | `adaptador_paquete.py`, `BandejaDeAvisos` | Aísla el formato de los CSV y el canal de notificación |
| Factory | `CicloDeVidaDeCita.agendar`, `CicloDeVidaDeEmergencia.identificar` | Una emergencia o cita nueva se crea cumpliendo invariantes; el constructor solo reconstituye |
| Dependency Injection | `create_app`, fábrica de unidades de trabajo, reloj y generador de ids inyectables | Pruebas deterministas |

## SOLID

- **S (responsabilidad única).** Cada módulo tiene un motivo de cambio: `reglas_cita.py` (reglas), `ciclo_de_vida.py` (transiciones), `disponibilidad.py` (capacidad), `control_de_acceso.py` (permisos), `errores_http.py` (traducción a HTTP).
- **O (abierto/cerrado).** Una regla nueva se añade componiendo Specifications sin tocar las existentes; un permiso nuevo es una entrada en `Permiso` y en la matriz rol→permisos.
- **L (sustitución de Liskov).** Los repositorios SQL funcionan igual sobre SQLite y PostgreSQL (las mismas pruebas corren en ambos), y `BandejaDeAvisos` cumple el puerto `NotificadorDeVeterinario`; las pruebas lo sustituyen por un notificador que falla.
- **I (segregación de interfaces).** Puertos pequeños y específicos: un repositorio por agregado, `NotificadorDeVeterinario` con un solo método.
- **D (inversión de dependencias).** Los servicios de aplicación dependen de los puertos de `puertos.py`; la implementación concreta se inyecta en `main.py`.

## Principios adicionales

12-factor (configuración por entorno, `.env.example`, logs a stdout), errores de dominio tipados con códigos estables, y trazabilidad de cada regla a su prueba (ver `trazabilidad.md`).
