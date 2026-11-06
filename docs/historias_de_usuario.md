# Historias de usuario y criterios de aceptación (Gherkin)

Fuente: documento *User Stories* del Equipo 4 (Módulo Netacad 2). Cada historia incluye su prioridad y sus escenarios en Gherkin.

## US01 — Registrar mascota

**Rol:** Propietario · **Prioridad:** Alta

> Como Propietario, quiero registrar una mascota, para que pueda recibir servicios de la clínica.

```gherkin
# language: es
Característica: Registro de mascota

  Escenario: Registrar una mascota
  Dado que el propietario desea registrar una mascota
  Cuando proporciona los datos de la mascota
  Entonces la mascota debe quedar registrada en el sistema
```

## US02 — Registrar múltiples mascotas

**Rol:** Propietario · **Prioridad:** Alta

> Como Propietario, quiero registrar varias mascotas, para tenerlas asociadas a mi perfil.

```gherkin
# language: es
Característica: Registro de múltiples mascotas

  Escenario: Registrar varias mascotas
  Dado que el propietario ya tiene una mascota registrada
  Cuando registra los datos de otra mascota
  Entonces la nueva mascota debe quedar asociada al propietario
```

## US03 — Consultar expediente

**Rol:** Propietario · **Prioridad:** Alta

> Como Propietario, quiero consultar el expediente de mi mascota, para conocer su información registrada.

```gherkin
# language: es
Característica: Consulta del expediente

  Escenario: Consultar información de la mascota
  Dado que la mascota cuenta con un expediente registrado
  Cuando el propietario consulta la información de su mascota
  Entonces el sistema debe mostrar la información disponible del expediente
```

## US04 — Solicitar cita

**Rol:** Propietario · **Prioridad:** Alta

> Como Propietario, quiero solicitar una cita, para que mi mascota reciba atención.

```gherkin
# language: es
Característica: Solicitud de cita

  Escenario: Solicitar una cita
  Dado que el propietario desea llevar a su mascota a la clínica
  Cuando solicita una cita
  Entonces debe poder seleccionar el tipo de servicio
  Y elegir una fecha y hora
```

## US05 — Recibir recordatorio

**Rol:** Propietario · **Prioridad:** Alta

> Como Propietario, quiero recibir recordatorios de mis citas y vacunas, para no olvidar fechas importantes.

```gherkin
# language: es
Característica: Recordatorio automatizado

  Escenario: Generar recordatorio
  Dado que existe una cita o seguimiento registrado
  Cuando se genera el recordatorio automatizado
  Entonces el sistema debe registrar el recordatorio en la programación de
recordatorios
```

## US06 — Registrar datos en recepción

**Rol:** Recepción · **Prioridad:** Alta

> Como Recepción, quiero registrar los datos de la mascota, para disponer de su información durante la atención.

```gherkin
# language: es
Característica: Registro de llegada

  Escenario: Registrar llegada de la mascota
  Dado que el propietario llega a la clínica con su mascota
  Cuando Recepción registra la llegada
  Entonces la mascota debe quedar registrada como llegada
```

## US07 — Consultar citas programadas

**Rol:** Recepción · **Prioridad:** Alta

> Como Recepción, quiero consultar las citas programadas, para organizar la atención de las mascotas.

```gherkin
# language: es
Característica: Gestión de agenda

  Escenario: Agendar una cita confirmada
  Dado que el propietario confirmó una cita
  Cuando Recepción recibe la información de la cita
  Entonces debe poder agendarla en la agenda
```

## US08 — Registrar peso

**Rol:** Recepción · **Prioridad:** Alta

> Como Recepción, quiero registrar el peso de la mascota, para que el veterinario tenga el dato actualizado.

```gherkin
# language: es
Característica: Registro de peso

  Escenario: Tomar peso de la mascota
  Dado que Recepción ha registrado la llegada de la mascota
  Cuando toma el peso registrado
  Entonces el peso debe quedar registrado junto con el motivo de la atención
```

## US09 — Registrar motivo de consulta

**Rol:** Recepción · **Prioridad:** Alta

> Como Recepción, quiero registrar el motivo de consulta, para informar al veterinario sobre la razón de la visita.

```gherkin
# language: es
Característica: Registro del motivo

  Escenario: Registrar motivo de consulta
  Dado que la mascota ha llegado a la clínica
  Cuando Recepción registra el motivo de la atención
  Entonces el motivo debe quedar registrado junto con el peso de la mascota
```

## US10 — Facturar y cobrar

**Rol:** Recepción · **Prioridad:** Media

> Como Recepción, quiero facturar y cobrar los servicios, para registrar el pago de la atención.

```gherkin
# language: es
Característica: Facturación y cobro

  Escenario: Facturar y cobrar los servicios
  Dado que la mascota recibió atención
  Cuando Recepción factura y cobra los servicios
  Entonces debe registrarse el cobro
  Y debe entregarse la documentación al propietario
```

## US11 — Consultar expediente como veterinario

**Rol:** Veterinario · **Prioridad:** Alta

> Como Veterinario, quiero consultar el expediente de la mascota, para conocer sus antecedentes antes de atenderla.

```gherkin
# language: es
Característica: Consulta del expediente veterinario

  Escenario: Consultar información antes de la consulta
  Dado que la mascota se encuentra lista para ser atendida
  Cuando el veterinario inicia la consulta
  Entonces debe poder consultar la información disponible de la mascota
```

## US12 — Generar nota clínica

**Rol:** Veterinario · **Prioridad:** Alta

> Como Veterinario, quiero generar una nota clínica, para registrar los resultados de la consulta.

```gherkin
# language: es
Característica: Generación de nota clínica

  Escenario: Generar nota clínica
  Dado que el veterinario está realizando la consulta
  Cuando registra la información clínica de la mascota
  Entonces debe generarse la nota clínica
```

## US13 — Generar receta

**Rol:** Veterinario · **Prioridad:** Alta

> Como Veterinario, quiero generar una receta, para indicar el tratamiento de la mascota.

```gherkin
# language: es
Característica: Generación de receta

  Escenario: La mascota requiere medicamento
  Dado que el veterinario realizó la consulta
  Cuando determina que la mascota requiere medicamento
  Entonces debe generar una receta
  Y continuar con el plan de seguimiento
```

## US14 — Generar orden de estudios

**Rol:** Veterinario · **Prioridad:** Media

> Como Veterinario, quiero generar una orden de estudios, para solicitar pruebas necesarias para la atención.

```gherkin
# language: es
Característica: Orden de estudio

  Escenario: La mascota requiere estudios
  Dado que el veterinario realizó la consulta
  Cuando determina que se requieren estudios
  Entonces debe generar una orden de estudio
  Y continuar con el plan de seguimiento
```

## US15 — Registrar vacunación

**Rol:** Veterinario · **Prioridad:** Alta

> Como Veterinario, quiero registrar la vacunación de la mascota, para mantener actualizado su esquema de vacunación.

```gherkin
# language: es
Característica: Registro de vacunación

  Escenario: Registrar una vacunación
  Dado que el veterinario está atendiendo a la mascota
  Cuando registra la vacunación correspondiente
  Entonces la vacunación debe quedar registrada
  Y debe poder generarse el seguimiento correspondiente
```

## US16 — Consultar alergias

**Rol:** Veterinario · **Prioridad:** Alta

> Como Veterinario, quiero consultar las alergias de la mascota, para considerarlas durante la atención.

```gherkin
# language: es
Característica: Información de alergias

  Escenario: Consultar las alergias de la mascota
  Dado que existen datos de alergias de la mascota
  Cuando el veterinario realiza la consulta
  Entonces debe poder consultar la información de alergias disponible
```

## US17 — Registrar hospitalización

**Rol:** Personal Clínico · **Prioridad:** Alta

> Como Personal Clínico, quiero registrar la hospitalización de una mascota, para iniciar su atención y monitoreo.

```gherkin
# language: es
Característica: Hospitalización

  Escenario: La mascota requiere hospitalización
  Dado que el veterinario realizó la consulta
  Cuando determina que la mascota requiere hospitalización
  Entonces debe emitirse la orden de hospitalización
  Y el personal clínico debe iniciar la hospitalización y monitoreo
```

## US18 — Registrar hoja de monitoreo

**Rol:** Personal Clínico · **Prioridad:** Alta

> Como Personal Clínico, quiero registrar la hoja de monitoreo, para llevar el seguimiento de la mascota hospitalizada.

```gherkin
# language: es
Característica: Hoja de monitoreo

  Escenario: Registrar hoja de monitoreo
  Dado que la mascota inició su hospitalización y monitoreo
  Cuando el personal clínico registra la hoja de monitoreo
  Entonces la hoja de monitoreo debe quedar registrada
```

## US19 — Registrar evolución

**Rol:** Personal Clínico · **Prioridad:** Alta

> Como Personal Clínico, quiero registrar la evolución de la mascota hospitalizada, para mantener actualizado su seguimiento.

```gherkin
# language: es
Característica: Evolución de la mascota

  Escenario: Registrar evolución durante el monitoreo
  Dado que la mascota se encuentra hospitalizada
  Cuando el personal clínico realiza el seguimiento
  Entonces debe actualizar la información correspondiente en la hoja de monitoreo
```

## US20 — Atender una emergencia

**Rol:** Personal Clínico · **Prioridad:** Alta

> Como Personal Clínico, quiero atender una mascota identificada como emergencia, para darle prioridad dentro del proceso de atención.

```gherkin
# language: es
Característica: Atención de emergencia

  Escenario: Identificar una emergencia
  Dado que la mascota ha llegado a la clínica
  Cuando Recepción determina que es una emergencia
  Entonces debe activarse el protocolo de emergencia
  Y debe notificarse al veterinario
```
