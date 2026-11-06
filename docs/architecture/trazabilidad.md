# Matriz de trazabilidad: análisis → arquitectura → código → pruebas

Cada fila une una necesidad o regla del BRD con sus historias de usuario, el componente de diseño, el código que la cumple y las pruebas que la verifican. Las rutas de código son relativas a `src/vetcare24/` y las de pruebas a `tests/`. Las pruebas de API se ejecutan con SQLite y PostgreSQL 16.

| BRD (necesidad / regla) | Historias | CU | Componentes (diseño y código) | Pruebas | ADR | Estado |
|---|---|---|---|---|---|---|
| NB-01, NB-02, NB-03, R-10, S-01 | US01, US02, US06 | — | `ServicioDeRegistro`, `Propietario`, `Mascota`, `repositorios_sql` | `test_servicios_de_aplicacion.py::test_registrar_propietario_y_mascota`, `::test_registro_rechaza_duplicados_y_referencias_rotas`, `test_dominio.py`, `test_repositorios_sql.py` | ADR-01, ADR-02 | Implementada |
| NB-04, NB-05, R-07 | US08 (peso), US16 (alergias) | — | Atributos `peso_kg` y `alergias` de `Mascota` | `test_repositorios_sql.py::test_mascotas_conservan_peso_alergias_y_acentos`, `test_dominio.py` | ADR-02 | Parcial (atributos; sin flujo clínico propio) |
| NB-06, R-05 | US04, US07 | CU-01 | `ServicioDeCitas`, `Cita`, `ServicioSolicitado`, `reglas_cita` (`PuedeProcesarse`) | `test_reglas_cita.py`, `test_servicios_de_aplicacion.py`, `test_api.py`, `test_u5_matriz.py` | ADR-01, ADR-07 | Implementada |
| NB-08 (confirmar, modificar, cancelar) | US04 | CU-01 | `CicloDeVidaDeCita`, `Disponibilidad`, `PUT /citas/{id}/servicios`, `POST /citas/{id}/cancelar` | `test_ciclo_de_vida.py`, `test_disponibilidad.py`, `test_api.py::test_cancelar_y_modificar`, matriz CP-01 a CP-03 | ADR-07 | Implementada |
| NB-07 | US04 | CU-01 | `PeriodoDeCita` (diseño) | — | ADR-01 | Diferida: los datos no traen horarios ni duraciones (A-11) |
| NB-20, R-01, R-09, R-14 | Transversal | Todos | `control_de_acceso` (`Rol`, `Permiso`), encabezado `X-Rol` | `test_control_de_acceso.py`, `test_api.py::test_sin_rol_responde_401_y_con_rol_desconocido_400`, `test_api_errores.py` | ADR-04 | Implementada |
| NB-14, R-11 | US15 | CU-03 | `ServicioDeVacunacion`, `Vacunacion`, `repositorios_sql` | `test_servicios_vacunacion.py::test_el_historial_se_conserva_y_el_seguimiento_usa_la_ultima`, `test_vacunacion.py`, `test_repositorios_vacunacion.py` | ADR-02, ADR-05 | Implementada |
| NB-15, R-12 | US15 | CU-03 | `EsquemaDeVacunacion`, `reglas_vacunacion`, `seguimiento_vacunacion` | `test_reglas_vacunacion.py::test_seguimiento_calculable_exige_esquema_definido_y_validado`, `test_seguimiento_vacunacion.py`, `test_servicios_vacunacion.py::test_registrar_no_depende_del_esquema` | ADR-05 | Implementada |
| NB-16, R-13 | US15 | CU-03 | `seguimiento_vacunacion` (`es_refuerzo`) | `test_seguimiento_vacunacion.py::test_identifica_si_la_siguiente_aplicacion_es_un_refuerzo`, `test_reglas_vacunacion.py::test_requerir_refuerzo_no_condiciona_el_seguimiento` | ADR-05 | Implementada |
| NB-17 | US05 (vacunas) | CU-03 | `GET /vacunas/proximas` | `test_servicios_vacunacion.py::test_proximas_incluye_vencidas_y_las_de_la_ventana`, `test_api.py::test_vacunas_proximas_para_recordatorios` | ADR-05 | Implementada (cálculo por consulta; sin envío, A-05) |
| NB-19, R-06, S-08, CR-8 | US20 | CU-05 | `ServicioDeEmergencias.atender_emergencia`, `Emergencia`, `CicloDeVidaDeEmergencia` | `test_servicios_emergencias.py::test_emergencia_sin_cita_se_registra`, `test_emergencia.py`, `test_api_emergencias.py::test_los_20_escenarios_del_recorrido_coinciden` | ADR-01, ADR-02 | Implementada |
| NB-19 (notificar al veterinario) | US20 | CU-05 | Puerto `NotificadorDeVeterinario`, `BandejaDeAvisos` | `test_servicios_emergencias.py::test_notifica_veterinario_tras_confirmar`, `::test_si_la_notificacion_falla_el_registro_se_conserva` | ADR-02 | Implementada |
| R-06 (atención permitida) | US20 | CU-05 | `atencion_permitida = TieneCitaConfirmada OR TieneEmergenciaActiva`, `GET /mascotas/{id}/evaluaciones/atencion` | `test_specification.py::test_or_exige_al_menos_una`, `test_servicios_emergencias.py` | ADR-01 | Implementada |
| Eventos de dominio (D-14) | Transversal | CU-01, CU-03, CU-05 | `eventos`, `Despachador`, tabla `eventos_dominio` | `test_eventos.py`, `test_despachador.py`, `test_eventos_ciclo.py` | ADR-02 | Implementada (eventos de Cita, Vacunación y Emergencia) |
| Una transacción por caso de uso | Transversal | Todos | `UnidadDeTrabajoSql` | `test_servicios_de_aplicacion.py`, `test_base_de_datos.py` | ADR-02 | Implementada |
| Contrato de errores HTTP (D-13) | Transversal | Todos | `errores_http`, `main.py` | `test_api_errores.py`, `test_api.py` | ADR-06 | Implementada |
| Paquete del profesor: 60 operaciones, 120 casos, 20 transiciones | — | CU-01 | `csv_loader`, `adaptador_paquete`, `sembrado`, oráculo independiente | `test_csv_loader.py`, `test_adaptador_paquete.py`, `test_oraculo.py`, `test_api_paquete.py`, `test_u5_matriz.py` | ADR-08 | Implementada |
| NB-10, NB-11, NB-12, NB-13, R-02, R-03 | US03, US11, US12, US13, US14, US16 | CU-02 | `ExpedienteClinico`, `NotaClinica` (diseño) | — | ADR-04, ADR-09 | **Fuera del alcance implementado** |
| NB-18, R-04, R-08 | US17, US18, US19 | CU-04 | `Hospitalizacion` (diseño) | — | ADR-09 | **Fuera del alcance implementado** |
| NB-21 | — | — | Reportes | — | ADR-09 | **Fuera del alcance implementado** |
| Cobro de servicios | US10 | — | Solo se calcula el total (`Money`, D-02); el cobro y la facturación fiscal quedan fuera (A-02) | `test_money.py` | — | Parcial (total calculado) |

## Estado por historia de usuario

| US | Historia | Estado | Dónde |
|---|---|---|---|
| US01 | Registrar mascota | Implementada | `POST /mascotas` |
| US02 | Registrar múltiples mascotas | Implementada | `POST /mascotas` (varias por propietario) |
| US03 | Consultar expediente (propietario) | Parcial | `GET /mascotas/{id}`, `GET /mascotas/{id}/vacunaciones` |
| US04 | Solicitar cita | Implementada | `POST /citas` y ciclo completo |
| US05 | Recordatorios | Parcial (solo vacunas, sin envío) | `GET /vacunas/proximas` |
| US06 | Recepción registra datos de mascota | Implementada (alta) | `POST /mascotas` |
| US07 | Consultar citas programadas | Implementada | `GET /citas` |
| US08 | Registrar peso al llegar | Parcial (peso como dato de la mascota) | `Mascota.peso_kg` |
| US09 | Registrar motivo de consulta | Fuera del alcance implementado (el motivo existe solo en emergencias) | — |
| US10 | Registrar cobro | Fuera del alcance implementado (total calculado) | `Money` |
| US11 | Veterinario consulta expediente | Parcial (mascota y vacunas) | `GET /mascotas/{id}` |
| US12 | Registrar nota clínica | **Fuera del alcance implementado (CU-02)** | — |
| US13 | Registrar receta | Fuera del alcance implementado | — |
| US14 | Órdenes de estudios | Fuera del alcance implementado | — |
| US15 | Registrar vacunas | Implementada | `POST /mascotas/{id}/vacunaciones` |
| US16 | Consultar alergias | Parcial (atributo de la mascota) | `Mascota.alergias` |
| US17 | Ingreso a hospitalización | **Fuera del alcance implementado (CU-04)** | — |
| US18 | Hoja de monitoreo | **Fuera del alcance implementado (CU-04)** | — |
| US19 | Evolución del hospitalizado | **Fuera del alcance implementado (CU-04)** | — |
| US20 | Atender una emergencia | Implementada | `POST /emergencias` |
