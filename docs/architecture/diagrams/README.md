# Diagramas

| # | Diagrama | Archivo | Fuente |
|---|---|---|---|
| 01 | Mapa de dominio (DDD) con alcance marcado | `01_mapa_de_dominio_marcado.png` | Unidad 3, marcado |
| 02 | Diagrama de clases UML con alcance marcado | `02_diagrama_de_clases_marcado.png` | Unidad 3, marcado |
| 03 | Secuencia CU-01 Solicitar cita (implementado) | `03_secuencia_cu01_implementada.png` | Unidad 3 |
| 04 | Secuencia CU-02 Generar nota clínica (implementado) | `04_secuencia_cu02_implementada.png` | Unidad 3 |
| 05 | BPMN con alcance marcado | `../../bpmn/bpmn_marcado.png` | Unidad 2 |
| 06 | Arquitectura por capas | `06_arquitectura_capas.png/.mmd` | Mermaid |
| 07 | Despliegue y CI/CD | `07_despliegue.png/.mmd` | Mermaid |
| 08 | Máquina de estados de Cita | `08_estados_cita.png/.mmd` | Mermaid |
| 09 | Máquina de estados de Emergencia | `09_estados_emergencia.png/.mmd` | Mermaid |
| 10 | Secuencia CU-05 Atender una emergencia | `10_secuencia_cu05.png/.mmd` | Mermaid |
| 11 | Modelo entidad-relación | `11_er.png/.mmd` | Mermaid |
| 12 | Specifications | `12_specifications.png/.mmd` | Mermaid |
| 13 | Alcance implementado | `13_alcance.png/.mmd` | Mermaid |
| 14 | Máquina de estados de Hospitalización | `14_estados_hospitalizacion.png/.mmd` | Mermaid |
| 15 | Secuencia CU-04 Hospitalización, monitoreo y alta | `15_secuencia_cu04.png/.mmd` | Mermaid |

Regenerar: `mmdc -i NN_nombre.mmd -o NN_nombre.png -s 2 -b white`.
Verde = implementado. Rojo (solo en el diagrama 13) = fuera del alcance: factura fiscal, envío real de recordatorios y autenticación.
