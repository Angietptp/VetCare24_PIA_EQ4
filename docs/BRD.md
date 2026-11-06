# Business Requirements Document (BRD) — VetCare 24

**Equipo 4** · García Cerda Randal Guillermo (2112493), Sarmiento Hernández Cesar Martín (2119427), Torres Pasillas Angela Susana (2101844)
**Curso:** Componentes de Lógica de Negocios · **Profesor:** Miguel Ángel Gómez Marroquín

> Este documento reproduce el BRD elaborado en el Módulo 2 (levantamiento con el cliente, contexto, problemas, alcance, necesidades, restricciones, supuestos y criterios de éxito). Se añadió la columna **Estado de implementación** en las necesidades de negocio para reflejar el alcance del código entregado (ver [`alcance_implementado.md`](alcance_implementado.md)). Las decisiones que corrigen o precisan el BRD están en [`architecture/decisiones.md`](architecture/decisiones.md).

## 1. Contexto

| Elemento | Descripción |
|---|---|
| Nombre del negocio | VetCare 24 |
| Giro | Clínica veterinaria |
| Servicios principales | Consultas, vacunas, cirugías, estética, estudios y hospitalización |
| Procesos involucrados | Gestión de citas, recepción, atención veterinaria, expediente clínico, vacunación, hospitalización y emergencias |

VetCare 24 es una clínica veterinaria que brinda diferentes servicios para mascotas, como consultas, vacunación, cirugías, estudios, estética y hospitalización. La operación involucra principalmente al propietario, la mascota, recepción, los veterinarios y el personal clínico. El proceso comienza con el registro del propietario y su mascota y la programación de una cita, para posteriormente realizar la recepción y atención veterinaria. Durante la atención se genera y actualiza el expediente clínico, mientras que en casos de vacunación, hospitalización o emergencia se requieren procesos adicionales de seguimiento y registro. Actualmente, parte de la información se maneja en papel, lo que dificulta su consulta y seguimiento, especialmente en los antecedentes clínicos y las vacunas.

## 2. Problemas

| ID | Problema | Descripción |
|---|---|---|
| P-01 | Expedientes en papel | Parte de la información clínica se mantiene en papel, lo que dificulta su consulta y seguimiento. |
| P-02 | Expedientes duplicados | Existe el riesgo de registrar una misma mascota más de una vez, generando información duplicada. |
| P-03 | Consulta lenta del historial | Es difícil consultar rápidamente los antecedentes clínicos de una mascota cuando se necesita información previa. |
| P-04 | Recordatorios de vacunas deficientes | Los recordatorios actuales no siempre permiten dar un seguimiento adecuado a las vacunas próximas o a los refuerzos. |
| P-05 | Información clínica dispersa | La información necesaria para la atención puede encontrarse en diferentes registros, dificultando su consulta. |
| P-06 | Seguimiento de hospitalización | Los pacientes hospitalizados requieren seguimiento continuo y registro de su evolución. |
| P-07 | Registro de emergencias | Las emergencias pueden presentarse fuera del flujo normal de citas, por lo que se requiere registrar la atención sin una cita previa. |

## 3. Oportunidades

| ID | Oportunidad | Descripción |
|---|---|---|
| O-01 | Centralizar los expedientes | Contar con un registro organizado por mascota que facilite consultar su información clínica. |
| O-02 | Reducir registros duplicados | Asociar correctamente cada mascota con su propietario y mantener un expediente individual. |
| O-03 | Facilitar la consulta del historial | Permitir que el personal autorizado consulte rápidamente los antecedentes y notas clínicas. |
| O-04 | Mejorar el seguimiento de vacunas | Registrar las vacunas aplicadas, sus fechas, próximas aplicaciones y refuerzos según el esquema correspondiente. |
| O-05 | Mejorar los recordatorios | Facilitar la identificación de vacunas próximas para generar o enviar recordatorios a los propietarios. |
| O-06 | Mejorar el control de citas | Organizar las citas considerando el servicio solicitado y el tiempo requerido para cada atención. |
| O-07 | Mejorar el seguimiento de hospitalizados | Mantener registrada la evolución de las mascotas hospitalizadas y las indicaciones del veterinario. |
| O-08 | Registrar emergencias de forma adecuada | Permitir documentar la atención de mascotas que llegan sin una cita programada. |
| O-09 | Controlar los permisos | Definir el acceso y las operaciones disponibles para recepción, veterinarios y personal clínico según sus responsabilidades. |
| O-10 | Facilitar la supervisión | Generar información sobre citas, pacientes atendidos, vacunas próximas y mascotas hospitalizadas para apoyar la supervisión de la clínica. |

## 4. Stakeholders

| Stakeholder | Rol dentro de VetCare 24 | Interés o participación |
|---|---|---|
| Propietario | Persona responsable de la mascota | Solicita citas, proporciona información de la mascota y recibe información sobre su atención y vacunas |
| Mascota / Paciente | Animal que recibe los servicios veterinarios | Es el centro de los procesos de consulta, vacunación, hospitalización, estudios y demás servicios |
| Recepción | Personal encargado de la atención administrativa | Registra propietarios y mascotas, gestiona citas, confirma llegadas y actualiza información administrativa |
| Veterinario | Profesional responsable de la atención médica | Consulta y actualiza información clínica, registra notas, indica medicamentos, estudios, vacunas y seguimiento |
| Personal clínico | Personal que participa en la atención y seguimiento de los pacientes | Consulta la información necesaria para la atención y da seguimiento a mascotas hospitalizadas |
| Responsable de la clínica | Encargado de supervisar la operación de VetCare 24 | Consulta información y reportes que permitan supervisar las actividades de la clínica |

## 5. Alcance del negocio

| ID | Elemento incluido |
|---|---|
| A-01 | Registro de propietarios. |
| A-02 | Registro y asociación de mascotas con sus propietarios. |
| A-03 | Gestión de datos de las mascotas. |
| A-04 | Gestión de citas. |
| A-05 | Modificación y cancelación de citas. |
| A-06 | Registro de llegada, peso y motivo de consulta. |
| A-07 | Gestión y consulta del expediente clínico. |
| A-08 | Registro de notas clínicas. |
| A-09 | Registro de medicamentos, estudios, vacunas e indicaciones. |
| A-10 | Gestión del historial de vacunas. |
| A-11 | Gestión de frecuencia, próximas aplicaciones y refuerzos de vacunas. |
| A-12 | Recordatorios de vacunación. |
| A-13 | Gestión y seguimiento de hospitalizaciones. |
| A-14 | Registro de emergencias. |
| A-15 | Gestión de permisos según el rol. |
| A-16 | Generación de reportes de la operación. |

## 6. Necesidades del negocio

| ID | Necesidad del negocio | Estado de implementación |
|---|---|---|
| NB-01 | Mantener un registro de los propietarios de las mascotas. | Implementada |
| NB-02 | Permitir asociar varias mascotas a un mismo propietario. | Implementada |
| NB-03 | Mantener un registro individual para cada mascota. | Implementada |
| NB-04 | Registrar los datos relevantes de cada mascota, como especie, raza, sexo, fecha de nacimiento y peso. | Implementada |
| NB-05 | Mantener registrada la información relevante para la atención, como alergias y cambios de peso. | Parcial (alergias y peso como atributos de la mascota) |
| NB-06 | Gestionar las citas de acuerdo con el servicio veterinario solicitado. | Implementada |
| NB-07 | Considerar la duración requerida por los diferentes tipos de servicio al gestionar las citas. | Diferida (sin horarios ni duraciones en los datos) |
| NB-08 | Permitir modificar o cancelar las citas cuando el propietario lo solicite. | Implementada |
| NB-09 | Registrar la llegada de la mascota y su motivo de consulta. | Parcial (confirmación de la cita; peso y motivo de consulta no se capturan como flujo propio) |
| NB-10 | Mantener un expediente clínico actualizado para cada mascota. | Implementada (CU-02) |
| NB-11 | Facilitar al personal autorizado la consulta de los antecedentes clínicos de una mascota. | Implementada (CU-02) |
| NB-12 | Registrar las notas clínicas generadas durante la atención veterinaria. | Implementada (CU-02) |
| NB-13 | Registrar los medicamentos, estudios, vacunas o indicaciones de seguimiento determinadas por el veterinario. | Implementada (CU-02: nota con indicaciones, recetas y órdenes de estudio) |
| NB-14 | Mantener un historial de las vacunas aplicadas a cada mascota. | Implementada |
| NB-15 | Gestionar la frecuencia o esquema de aplicación de las vacunas y determinar las próximas aplicaciones. | Implementada |
| NB-16 | Identificar las vacunas que requieren refuerzo y darles el seguimiento correspondiente. | Implementada |
| NB-17 | Mejorar los recordatorios de vacunas próximas para los propietarios. | Implementada (consulta de próximas; sin envío) |
| NB-18 | Registrar y dar seguimiento a las mascotas que se encuentren hospitalizadas. | Implementada (CU-04) |
| NB-19 | Permitir registrar y gestionar emergencias que ocurran sin una cita previamente programada. | Implementada |
| NB-20 | Controlar los permisos de los usuarios de acuerdo con su rol. | Implementada |
| NB-21 | Generar reportes que permitan supervisar la operación de la clínica. | Implementada (`GET /reportes/operacion`) |

## 7. Restricciones

| ID | Restricción |
|---|---|
| R-01 | Recepción administra las citas y los datos administrativos de propietarios y mascotas. |
| R-02 | El veterinario es quien registra la información clínica correspondiente a la atención. |
| R-03 | Las notas clínicas realizadas por el veterinario no deben ser modificadas por recepción. |
| R-04 | El personal clínico necesita acceso a la información necesaria para realizar el seguimiento de pacientes hospitalizados. |
| R-05 | Las citas deben considerar el tipo de servicio solicitado, debido a que los servicios pueden requerir diferentes tiempos. |
| R-06 | Las emergencias pueden presentarse sin una cita previamente programada. |
| R-07 | La información sobre alergias y peso debe estar disponible porque puede ser relevante para la atención. |
| R-08 | Las mascotas hospitalizadas requieren seguimiento continuo. |
| R-09 | Los permisos deben estar relacionados con las responsabilidades de cada rol. |
| R-10 | Cada mascota debe contar con un expediente clínico propio y estar asociada al propietario correspondiente. |
| R-11 | La información de las vacunas debe conservar su historial para poder identificar aplicaciones anteriores y próximas. |
| R-12 | La frecuencia o esquema de aplicación de cada vacuna debe estar definido y validado antes de utilizarse para determinar próximas aplicaciones. |
| R-13 | Las vacunas que requieran refuerzo deben poder identificarse y recibir el seguimiento correspondiente. |
| R-14 | La información clínica debe estar disponible únicamente para el personal autorizado de acuerdo con su rol. |

## 8. Supuestos

| ID | Supuesto |
|---|---|
| S-01 | Se asume que un propietario puede tener una o varias mascotas registradas en la clínica. |
| S-02 | Se asume que cada mascota cuenta con un expediente clínico propio. |
| S-03 | Se asume que recepción se encarga de gestionar la información administrativa de propietarios, mascotas y citas. |
| S-04 | Se asume que el veterinario es responsable de registrar la información clínica de la atención. |
| S-05 | Se asume que el personal clínico participa en el seguimiento de las mascotas durante su hospitalización. |
| S-06 | Se asume que las vacunas aplicadas a una mascota deben registrarse en su expediente. |
| S-07 | Se asume que algunas vacunas pueden requerir aplicaciones de refuerzo. |
| S-08 | Se asume que pueden presentarse emergencias sin que exista una cita previamente programada. |
| S-09 | Se asume que las alergias y el peso de la mascota son datos relevantes para su atención y deben mantenerse disponibles. |
| S-10 | Se asume que la información clínica debe estar disponible para el personal autorizado que la necesite para realizar sus funciones. |

## 9. Criterios de éxito

| ID | Criterio |
|---|---|
| CR-1 | El personal pueda encontrar rápidamente el expediente correcto de una mascota. |
| CR-2 | Se reduzca la existencia de expedientes duplicados. |
| CR-3 | La información clínica esté disponible para el personal autorizado. |
| CR-4 | Se pueda consultar el historial de vacunas de cada mascota. |
| CR-5 | Se puedan identificar las vacunas próximas y los refuerzos. |
| CR-6 | Mejoren los recordatorios de vacunación. |
| CR-7 | Se pueda realizar un seguimiento adecuado de las mascotas hospitalizadas. |
| CR-8 | Las emergencias puedan registrarse y gestionarse aunque no exista una cita. |
| CR-9 | Cada usuario pueda realizar únicamente las operaciones correspondientes a su rol. |
| CR-10 | El responsable de la clínica pueda consultar reportes útiles para supervisar la operación. |

## 10. Historias de usuario, glosario y procesos

- Historias de usuario con criterios de aceptación en Gherkin: [`historias_de_usuario.md`](historias_de_usuario.md)
- Glosario del dominio: [`glosario.md`](glosario.md)
- Procesos de negocio (BPMN): [`bpmn/`](bpmn/README.md)

## Anexo A. Levantamiento con el cliente (preguntas y respuestas)

**1. ¿Cómo inicia normalmente el proceso de atención de una mascota?**  
El proceso normalmente inicia cuando el propietario solicita una cita en la recepción. Se registran los datos del propietario y de la mascota, y se identifica el servicio que necesita, como consulta, vacunación, estudios u otro servicio disponible.

**2. ¿Qué datos necesitan para registrar a una mascota?**  
Se registra el nombre, especie, raza, sexo, fecha de nacimiento, peso y datos relevantes para su atención, como alergias. También se relaciona la mascota con su propietario, ya que un propietario puede tener varias mascotas.

**3. ¿Cómo se programan las citas?**  
Recepción es quien registra las citas. El tiempo de la cita depende del servicio solicitado, ya que una vacunación puede requerir menos tiempo que una consulta especializada. Antes de asignarla se revisa la disponibilidad correspondiente.

**4. ¿Quién puede cancelar o modificar una cita?**  
El propietario puede solicitar la cancelación o modificación de su cita a través de recepción. Recepción es quien realiza el cambio en el registro de la cita.

**5. ¿Qué sucede cuando una mascota llega a su cita?**  
Recepción confirma la llegada y se registra el peso actual de la mascota y el motivo de consulta. Después se pasa con el veterinario para realizar la atención.

**6. ¿Qué información registra el veterinario durante la consulta?**  
El veterinario genera una nota clínica con la información de la atención. Dependiendo de lo que encuentre, puede indicar medicamentos, estudios, vacunas o seguimiento.

**7. ¿Cómo se consulta el expediente clínico de una mascota?**  
El personal clínico y los veterinarios necesitan consultar el expediente para revisar los antecedentes antes o durante la atención. Actualmente parte de esa información se encuentra en papel, por lo que no siempre es rápido encontrar los antecedentes.

**8. ¿Quién puede modificar la información del expediente?**  
El veterinario puede agregar la información correspondiente a la atención clínica. Recepción puede actualizar los datos administrativos de la mascota y del propietario, pero no debe modificar las notas clínicas realizadas por el veterinario.

**9. ¿Cómo se lleva el control de las vacunas?**  
En el expediente se registran las vacunas que ya recibió la mascota. También se debe identificar cuándo corresponde una próxima aplicación. Algunas vacunas requieren refuerzo, por lo que es importante conservar el historial.

**10. ¿Con qué frecuencia debe aplicarse cada vacuna y cómo se determina la siguiente aplicación?**  
La frecuencia depende del tipo de vacuna. Se debe registrar la fecha de aplicación y utilizar el esquema correspondiente para determinar cuándo corresponde la siguiente aplicación. Cuando una vacuna requiere refuerzo, también debe registrarse y darse el seguimiento correspondiente.

**11. ¿Cómo se informa al propietario que una vacuna está próxima?**  
Actualmente los recordatorios no siempre se realizan de manera adecuada. Se necesita identificar las vacunas próximas y facilitar el envío o generación de recordatorios para los propietarios.

**12. ¿Qué sucede cuando una mascota necesita hospitalización?**  
El veterinario determina si la mascota necesita hospitalización. Cuando ingresa, el personal clínico debe darle seguimiento durante su estancia y registrar la información relevante de su evolución.

**13. ¿Qué información se registra durante la hospitalización?**  
Se registra la evolución de la mascota y la información necesaria para que el personal clínico pueda darle seguimiento. También deben mantenerse disponibles las indicaciones realizadas por el veterinario.

**14. ¿Cómo se atienden las emergencias?**  
Las emergencias pueden llegar sin una cita programada. En esos casos se prioriza la atención de la mascota y posteriormente se registra la información necesaria en su expediente.

**15. ¿Qué ocurre si una mascota tiene alergias o cambios importantes de peso?**  
Esa información debe quedar registrada y disponible para el veterinario, porque puede ser relevante para decidir cómo atender a la mascota o qué tratamiento indicar.

**16. ¿Qué permisos deben tener los diferentes usuarios del sistema?**  
Recepción debe poder gestionar propietarios, mascotas y citas. Los veterinarios deben poder consultar y actualizar la información clínica correspondiente. El personal clínico necesita consultar la información necesaria para realizar el seguimiento de los pacientes hospitalizados.

**17. ¿Qué reportes necesita actualmente la clínica?**  
Se necesita consultar información sobre citas, pacientes atendidos, vacunas pendientes o próximas y mascotas hospitalizadas. También sería útil contar con información sobre la actividad de la clínica para facilitar la supervisión.

**18. ¿Cuáles son los principales problemas que desean solucionar?**  
Principalmente se quiere reducir el uso de expedientes en papel, evitar que se creen expedientes duplicados, facilitar la consulta de antecedentes y mejorar los recordatorios de vacunas.

**19. ¿Qué información consideran prioritaria para mejorar la operación?**  
Lo más importante es tener expedientes completos y fáciles de consultar, controlar correctamente las citas, mantener actualizado el historial de vacunas y contar con información de hospitalización y emergencias.

**20. ¿Cómo sabrían que el nuevo sistema está funcionando correctamente?**  
Se consideraría que funciona correctamente si el personal puede encontrar rápidamente el expediente correcto de cada mascota, se reducen los expedientes duplicados, mejora el seguimiento de vacunas y el personal puede consultar la información necesaria para atender a los pacientes y dar seguimiento a los hospitalizados.

