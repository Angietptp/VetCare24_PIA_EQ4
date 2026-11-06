"""Comandos: los datos que necesita cada caso de uso, sin lógica."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

Servicios = tuple[tuple[str, int], ...]  # pares (servicio_id, cantidad)


@dataclass(frozen=True)
class RegistrarPropietario:
    nombre: str
    activo: bool = True
    preferente: bool = False
    propietario_id: str | None = None


@dataclass(frozen=True)
class RegistrarMascota:
    propietario_id: str
    nombre: str
    especie: str
    raza: str | None = None
    sexo: str | None = None
    fecha_nacimiento: date | None = None
    peso_kg: Decimal | int | str | None = None
    alergias: tuple[str, ...] = ()
    mascota_id: str | None = None


@dataclass(frozen=True)
class SolicitarCita:
    propietario_id: str
    mascota_id: str
    servicios: Servicios
    fecha_solicitud: date
    autorizada: bool
    promocion_activa: bool = False
    referencia: str | None = None
    cita_id: str | None = None


@dataclass(frozen=True)
class ModificarCita:
    cita_id: str
    servicios: Servicios


@dataclass(frozen=True)
class RegistrarVacunacion:
    mascota_id: str
    vacuna: str
    fecha_aplicacion: date
    lote: str | None = None
    vacunacion_id: str | None = None



@dataclass(frozen=True)
class AtenderEmergencia:
    """CU-05 (informe: AtenderEmergenciaComando). Sin identificador de cita (R-06)."""

    motivo: str
    mascota_id: str | None = None  # P3: opcional
    datos_paciente: str | None = None
    emergencia_id: str | None = None


@dataclass(frozen=True)
class RegistrarNotaClinica:
    """CU-02: nota en el expediente; `cita_id` opcional liga la nota a una cita realizada."""

    mascota_id: str
    diagnostico: str
    indicaciones: str | None = None
    cita_id: str | None = None
    nota_id: str | None = None


@dataclass(frozen=True)
class IngresarHospitalizacion:
    """CU-04: ingresa a la mascota (O-03: una sola hospitalización ingresada)."""

    mascota_id: str
    motivo: str
    hospitalizacion_id: str | None = None


@dataclass(frozen=True)
class RegistrarMonitoreo:
    """CU-04: una lectura de la hoja de monitoreo."""

    hospitalizacion_id: str
    observaciones: str
    temperatura_c: Decimal | None = None
    frecuencia_cardiaca: int | None = None


@dataclass(frozen=True)
class MedicamentoRecetado:
    nombre: str
    dosis: str
    indicaciones: str | None = None


@dataclass(frozen=True)
class EmitirReceta:
    """US13: receta con al menos un medicamento; `cita_id` opcional (cita realizada)."""

    mascota_id: str
    medicamentos: tuple[MedicamentoRecetado, ...]
    cita_id: str | None = None
    receta_id: str | None = None


@dataclass(frozen=True)
class EmitirOrdenDeEstudio:
    """US14: orden de un estudio de laboratorio o gabinete."""

    mascota_id: str
    estudio: str
    indicaciones: str | None = None
    cita_id: str | None = None
    orden_id: str | None = None


@dataclass(frozen=True)
class RegistrarCobro:
    """US10: cobro de una cita realizada; `metodo` es efectivo, tarjeta o transferencia."""

    cita_id: str
    metodo: str
    cobro_id: str | None = None
