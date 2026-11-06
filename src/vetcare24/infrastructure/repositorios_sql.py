"""Repositorios y Unidad de Trabajo sobre SQL (PostgreSQL o SQLite).

Un repositorio guarda y recupera objetos del dominio: el resto del sistema no ve tablas ni SQL.
Al recuperar una cita se reconstituye con `Cita(...)`, sin volver a aplicar reglas de negocio.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from types import TracebackType
from typing import Any

from vetcare24.application.errores import NoEncontrado
from vetcare24.application.puertos import (
    RepositorioDeCitas,
    RepositorioDeCobros,
    RepositorioDeEmergencias,
    RepositorioDeEsquemas,
    RepositorioDeEventos,
    RepositorioDeHospitalizaciones,
    RepositorioDeMascotas,
    RepositorioDeNotas,
    RepositorioDeOrdenes,
    RepositorioDePropietarios,
    RepositorioDeRecetas,
    RepositorioDeServicios,
    RepositorioDeVacunaciones,
    UnidadDeTrabajo,
)
from vetcare24.domain.catalogo import ServicioVeterinario
from vetcare24.domain.cita import Cita, EstadoCita, ServicioSolicitado
from vetcare24.domain.cobro import Cobro, MetodoDePago
from vetcare24.domain.documentos_clinicos import Medicamento, OrdenDeEstudio, Receta
from vetcare24.domain.emergencia import Emergencia, EstadoEmergencia
from vetcare24.domain.eventos import EventoDeDominio
from vetcare24.domain.hospitalizacion import (
    EstadoHospitalizacion,
    Hospitalizacion,
    LecturaDeMonitoreo,
)
from vetcare24.domain.mascota import Mascota
from vetcare24.domain.money import Money
from vetcare24.domain.nota_clinica import NotaClinica
from vetcare24.domain.propietario import Propietario
from vetcare24.domain.vacunacion import EsquemaDeVacunacion, Vacunacion
from vetcare24.infrastructure.base_de_datos import Conexion, conectar


def _entero(valor: bool) -> int:
    return 1 if valor else 0


def _centavos(dinero: Money) -> int:
    return int(dinero.monto.scaleb(2))


def _dinero(centavos: int) -> Money:
    return Money(Decimal(int(centavos)).scaleb(-2))


class RepositorioDeServiciosSql(RepositorioDeServicios):
    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, servicio: ServicioVeterinario) -> None:
        self._con.ejecutar(
            "INSERT INTO servicios (servicio_id, descripcion, precio_centavos, capacidad,"
            " habilitado) VALUES (?, ?, ?, ?, ?)",
            (servicio.servicio_id, servicio.descripcion, _centavos(servicio.precio),
             servicio.capacidad, _entero(servicio.habilitado)),
        )

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> ServicioVeterinario:
        return ServicioVeterinario(
            fila[0], fila[1], _dinero(fila[2]), int(fila[3]), bool(fila[4])
        )

    def obtener(self, servicio_id: str) -> ServicioVeterinario | None:
        filas = self._con.consultar(
            "SELECT servicio_id, descripcion, precio_centavos, capacidad, habilitado"
            " FROM servicios WHERE servicio_id = ?", (servicio_id,))
        return self._de_fila(filas[0]) if filas else None

    def todos(self) -> dict[str, ServicioVeterinario]:
        filas = self._con.consultar(
            "SELECT servicio_id, descripcion, precio_centavos, capacidad, habilitado"
            " FROM servicios ORDER BY servicio_id")
        return {fila[0]: self._de_fila(fila) for fila in filas}


class RepositorioDePropietariosSql(RepositorioDePropietarios):
    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, propietario: Propietario) -> None:
        self._con.ejecutar(
            "INSERT INTO propietarios (propietario_id, nombre, activo, preferente)"
            " VALUES (?, ?, ?, ?)",
            (propietario.propietario_id, propietario.nombre, _entero(propietario.activo),
             _entero(propietario.preferente)),
        )

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> Propietario:
        return Propietario(fila[0], fila[1], bool(fila[2]), bool(fila[3]))

    def obtener(self, propietario_id: str) -> Propietario | None:
        filas = self._con.consultar(
            "SELECT propietario_id, nombre, activo, preferente FROM propietarios"
            " WHERE propietario_id = ?", (propietario_id,))
        return self._de_fila(filas[0]) if filas else None

    def todos(self) -> list[Propietario]:
        filas = self._con.consultar(
            "SELECT propietario_id, nombre, activo, preferente FROM propietarios"
            " ORDER BY propietario_id")
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeMascotasSql(RepositorioDeMascotas):
    _COLUMNAS = ("mascota_id, propietario_id, nombre, especie, raza, sexo, fecha_nacimiento,"
                 " peso_kg, alergias_json")

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, mascota: Mascota) -> None:
        nacimiento = mascota.fecha_nacimiento.isoformat() if mascota.fecha_nacimiento else None
        peso = str(mascota.peso_kg) if mascota.peso_kg is not None else None
        self._con.ejecutar(
            f"INSERT INTO mascotas ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (mascota.mascota_id, mascota.propietario_id, mascota.nombre, mascota.especie,
             mascota.raza, mascota.sexo, nacimiento, peso,
             json.dumps(list(mascota.alergias), ensure_ascii=False)),
        )

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> Mascota:
        return Mascota(
            mascota_id=fila[0], propietario_id=fila[1], nombre=fila[2], especie=fila[3],
            raza=fila[4], sexo=fila[5],
            fecha_nacimiento=date.fromisoformat(fila[6]) if fila[6] else None,
            peso_kg=Decimal(fila[7]) if fila[7] is not None else None,
            alergias=json.loads(fila[8]),
        )

    def obtener(self, mascota_id: str) -> Mascota | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM mascotas WHERE mascota_id = ?", (mascota_id,))
        return self._de_fila(filas[0]) if filas else None

    def de_propietario(self, propietario_id: str) -> list[Mascota]:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM mascotas WHERE propietario_id = ? ORDER BY mascota_id",
            (propietario_id,))
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeCitasSql(RepositorioDeCitas):
    _COLUMNAS = ("cita_id, propietario_id, mascota_id, fecha_solicitud, estado, autorizada,"
                 " promocion_activa, referencia")

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def _insertar_lineas(self, cita: Cita) -> None:
        for posicion, linea in enumerate(cita.lineas, start=1):
            self._con.ejecutar(
                "INSERT INTO cita_lineas (cita_id, posicion, servicio_id, cantidad)"
                " VALUES (?, ?, ?, ?)",
                (cita.cita_id, posicion, linea.servicio_id, linea.cantidad),
            )

    def agregar(self, cita: Cita) -> None:
        self._con.ejecutar(
            f"INSERT INTO citas ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (cita.cita_id, cita.propietario_id, cita.mascota_id,
             cita.fecha_solicitud.isoformat(), cita.estado.value, _entero(cita.autorizada),
             _entero(cita.promocion_activa), cita.referencia),
        )
        self._insertar_lineas(cita)

    def guardar(self, cita: Cita) -> None:
        if not self._con.consultar("SELECT 1 FROM citas WHERE cita_id = ?", (cita.cita_id,)):
            raise NoEncontrado("cita", cita.cita_id)
        self._con.ejecutar(
            "UPDATE citas SET estado = ?, autorizada = ?, promocion_activa = ?, referencia = ?"
            " WHERE cita_id = ?",
            (cita.estado.value, _entero(cita.autorizada), _entero(cita.promocion_activa),
             cita.referencia, cita.cita_id),
        )
        self._con.ejecutar("DELETE FROM cita_lineas WHERE cita_id = ?", (cita.cita_id,))
        self._insertar_lineas(cita)

    def _reconstituir(self, fila: tuple[Any, ...]) -> Cita:
        lineas = self._con.consultar(
            "SELECT servicio_id, cantidad FROM cita_lineas WHERE cita_id = ? ORDER BY posicion",
            (fila[0],))
        return Cita(
            cita_id=fila[0], propietario_id=fila[1], mascota_id=fila[2],
            lineas=[ServicioSolicitado(servicio, int(cantidad)) for servicio, cantidad in lineas],
            fecha_solicitud=date.fromisoformat(fila[3]), estado=EstadoCita(fila[4]),
            autorizada=bool(fila[5]), promocion_activa=bool(fila[6]), referencia=fila[7],
        )

    def obtener(self, cita_id: str) -> Cita | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM citas WHERE cita_id = ?", (cita_id,))
        return self._reconstituir(filas[0]) if filas else None

    def listar(
        self, *, estado: EstadoCita | None = None, propietario_id: str | None = None
    ) -> list[Cita]:
        condiciones: list[str] = []
        parametros: list[Any] = []
        if estado is not None:
            condiciones.append("estado = ?")
            parametros.append(estado.value)
        if propietario_id is not None:
            condiciones.append("propietario_id = ?")
            parametros.append(propietario_id)
        donde = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM citas{donde} ORDER BY cita_id", parametros)
        return [self._reconstituir(fila) for fila in filas]

    def demanda_ocupada(self) -> dict[str, int]:
        filas = self._con.consultar(
            "SELECT l.servicio_id, SUM(l.cantidad) FROM cita_lineas l"
            " JOIN citas c ON c.cita_id = l.cita_id"
            " WHERE c.estado IN ('CONFIRMADA', 'REALIZADA')"
            " GROUP BY l.servicio_id ORDER BY l.servicio_id")
        return {servicio: int(total) for servicio, total in filas}

    def contar(self) -> int:
        return int(self._con.consultar("SELECT COUNT(*) FROM citas")[0][0])


class RepositorioDeVacunacionesSql(RepositorioDeVacunaciones):
    _COLUMNAS = "vacunacion_id, mascota_id, vacuna, fecha_aplicacion, lote"

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, vacunacion: Vacunacion) -> None:
        self._con.ejecutar(
            "INSERT INTO vacunaciones (vacunacion_id, mascota_id, vacuna, vacuna_clave,"
            " fecha_aplicacion, lote) VALUES (?, ?, ?, ?, ?, ?)",
            (vacunacion.vacunacion_id, vacunacion.mascota_id, vacunacion.vacuna,
             vacunacion.clave, vacunacion.fecha_aplicacion.isoformat(), vacunacion.lote),
        )

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> Vacunacion:
        return Vacunacion(
            vacunacion_id=fila[0], mascota_id=fila[1], vacuna=fila[2],
            fecha_aplicacion=date.fromisoformat(fila[3]), lote=fila[4],
        )

    def obtener(self, vacunacion_id: str) -> Vacunacion | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM vacunaciones WHERE vacunacion_id = ?",
            (vacunacion_id,))
        return self._de_fila(filas[0]) if filas else None

    def de_mascota(self, mascota_id: str) -> list[Vacunacion]:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM vacunaciones WHERE mascota_id = ?"
            " ORDER BY fecha_aplicacion, vacunacion_id", (mascota_id,))
        return [self._de_fila(fila) for fila in filas]

    def todas(self) -> list[Vacunacion]:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM vacunaciones"
            " ORDER BY mascota_id, fecha_aplicacion, vacunacion_id")
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeEsquemasSql(RepositorioDeEsquemas):
    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, esquema: EsquemaDeVacunacion) -> None:
        self._con.ejecutar(
            "INSERT INTO esquemas_vacunacion (vacuna_clave, vacuna, frecuencia_dias,"
            " requiere_refuerzo, validado) VALUES (?, ?, ?, ?, ?)",
            (esquema.clave, esquema.vacuna, esquema.frecuencia_dias,
             _entero(esquema.requiere_refuerzo), _entero(esquema.validado)),
        )

    def todos(self) -> dict[str, EsquemaDeVacunacion]:
        filas = self._con.consultar(
            "SELECT vacuna, frecuencia_dias, requiere_refuerzo, validado"
            " FROM esquemas_vacunacion ORDER BY vacuna_clave")
        esquemas = [
            EsquemaDeVacunacion(
                vacuna=vacuna, frecuencia_dias=int(frecuencia),
                requiere_refuerzo=bool(refuerzo), validado=bool(validado))
            for vacuna, frecuencia, refuerzo, validado in filas
        ]
        return {esquema.clave: esquema for esquema in esquemas}


def _texto(momento: datetime | None) -> str | None:
    return momento.isoformat() if momento is not None else None


def _momento(texto: str | None) -> datetime | None:
    return datetime.fromisoformat(texto) if texto else None


class RepositorioDeEmergenciasSql(RepositorioDeEmergencias):
    _COLUMNAS = ("emergencia_id, mascota_id, motivo, datos_paciente, estado, identificada_en,"
                 " atendida_en")

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, emergencia: Emergencia) -> None:
        e = emergencia
        self._con.ejecutar(
            f"INSERT INTO emergencias ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (e.emergencia_id, e.mascota_id, e.motivo, e.datos_paciente, e.estado.value,
             _texto(e.identificada_en), _texto(e.atendida_en)),
        )

    def guardar(self, emergencia: Emergencia) -> None:
        e = emergencia
        if not self._con.consultar(
                "SELECT 1 FROM emergencias WHERE emergencia_id = ?", (e.emergencia_id,)):
            raise NoEncontrado("emergencia", e.emergencia_id)
        self._con.ejecutar(
            "UPDATE emergencias SET estado = ?, atendida_en = ? WHERE emergencia_id = ?",
            (e.estado.value, _texto(e.atendida_en), e.emergencia_id),
        )

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> Emergencia:
        return Emergencia(
            emergencia_id=fila[0], mascota_id=fila[1], motivo=fila[2], datos_paciente=fila[3],
            estado=EstadoEmergencia(fila[4]), identificada_en=datetime.fromisoformat(fila[5]),
            atendida_en=_momento(fila[6]),
        )

    def obtener(self, emergencia_id: str) -> Emergencia | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM emergencias WHERE emergencia_id = ?",
            (emergencia_id,))
        return self._de_fila(filas[0]) if filas else None

    def listar(
        self, *, estado: EstadoEmergencia | None = None, mascota_id: str | None = None
    ) -> list[Emergencia]:
        condiciones: list[str] = []
        parametros: list[Any] = []
        if estado is not None:
            condiciones.append("estado = ?")
            parametros.append(estado.value)
        if mascota_id is not None:
            condiciones.append("mascota_id = ?")
            parametros.append(mascota_id)
        donde = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM emergencias{donde}"
            " ORDER BY identificada_en, emergencia_id", parametros)
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeNotasSql(RepositorioDeNotas):
    _COLUMNAS = "nota_id, mascota_id, cita_id, diagnostico, indicaciones, registrada_en"

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, nota: NotaClinica) -> None:
        self._con.ejecutar(
            f"INSERT INTO notas_clinicas ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?)",
            (nota.nota_id, nota.mascota_id, nota.cita_id, nota.diagnostico, nota.indicaciones,
             _texto(nota.registrada_en)))

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> NotaClinica:
        return NotaClinica(
            nota_id=fila[0], mascota_id=fila[1], cita_id=fila[2], diagnostico=fila[3],
            indicaciones=fila[4], registrada_en=datetime.fromisoformat(fila[5]))

    def obtener(self, nota_id: str) -> NotaClinica | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM notas_clinicas WHERE nota_id = ?", (nota_id,))
        return self._de_fila(filas[0]) if filas else None

    def listar(self, *, mascota_id: str) -> list[NotaClinica]:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM notas_clinicas WHERE mascota_id = ?"
            " ORDER BY registrada_en, nota_id", (mascota_id,))
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeHospitalizacionesSql(RepositorioDeHospitalizaciones):
    _COLUMNAS = ("hospitalizacion_id, mascota_id, motivo, estado, ingresada_en, alta_en,"
                 " resumen_alta")

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, hospitalizacion: Hospitalizacion) -> None:
        h = hospitalizacion
        self._con.ejecutar(
            f"INSERT INTO hospitalizaciones ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (h.hospitalizacion_id, h.mascota_id, h.motivo, h.estado.value,
             _texto(h.ingresada_en), _texto(h.alta_en), h.resumen_alta))
        self._guardar_lecturas(h)

    def guardar(self, hospitalizacion: Hospitalizacion) -> None:
        h = hospitalizacion
        if not self._con.consultar(
                "SELECT 1 FROM hospitalizaciones WHERE hospitalizacion_id = ?",
                (h.hospitalizacion_id,)):
            raise NoEncontrado("hospitalización", h.hospitalizacion_id)
        self._con.ejecutar(
            "UPDATE hospitalizaciones SET estado = ?, alta_en = ?, resumen_alta = ?"
            " WHERE hospitalizacion_id = ?",
            (h.estado.value, _texto(h.alta_en), h.resumen_alta, h.hospitalizacion_id))
        self._con.ejecutar(
            "DELETE FROM lecturas_monitoreo WHERE hospitalizacion_id = ?",
            (h.hospitalizacion_id,))
        self._guardar_lecturas(h)

    def _guardar_lecturas(self, h: Hospitalizacion) -> None:
        for orden, lectura in enumerate(h.lecturas, start=1):
            self._con.ejecutar(
                "INSERT INTO lecturas_monitoreo (hospitalizacion_id, orden, registrada_en,"
                " observaciones, temperatura_c, frecuencia_cardiaca) VALUES (?, ?, ?, ?, ?, ?)",
                (h.hospitalizacion_id, orden, _texto(lectura.registrada_en),
                 lectura.observaciones,
                 str(lectura.temperatura_c) if lectura.temperatura_c is not None else None,
                 lectura.frecuencia_cardiaca))

    def _de_fila(self, fila: tuple[Any, ...]) -> Hospitalizacion:
        lecturas = tuple(
            LecturaDeMonitoreo(
                registrada_en=datetime.fromisoformat(registrada), observaciones=observaciones,
                temperatura_c=Decimal(temperatura) if temperatura is not None else None,
                frecuencia_cardiaca=int(frecuencia) if frecuencia is not None else None)
            for registrada, observaciones, temperatura, frecuencia in self._con.consultar(
                "SELECT registrada_en, observaciones, temperatura_c, frecuencia_cardiaca"
                " FROM lecturas_monitoreo WHERE hospitalizacion_id = ? ORDER BY orden",
                (fila[0],)))
        return Hospitalizacion(
            hospitalizacion_id=fila[0], mascota_id=fila[1], motivo=fila[2],
            estado=EstadoHospitalizacion(fila[3]), ingresada_en=datetime.fromisoformat(fila[4]),
            alta_en=_momento(fila[5]), resumen_alta=fila[6], lecturas=lecturas)

    def obtener(self, hospitalizacion_id: str) -> Hospitalizacion | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM hospitalizaciones WHERE hospitalizacion_id = ?",
            (hospitalizacion_id,))
        return self._de_fila(filas[0]) if filas else None

    def listar(
        self, *, estado: EstadoHospitalizacion | None = None, mascota_id: str | None = None
    ) -> list[Hospitalizacion]:
        condiciones: list[str] = []
        parametros: list[Any] = []
        if estado is not None:
            condiciones.append("estado = ?")
            parametros.append(estado.value)
        if mascota_id is not None:
            condiciones.append("mascota_id = ?")
            parametros.append(mascota_id)
        donde = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM hospitalizaciones{donde}"
            " ORDER BY ingresada_en, hospitalizacion_id", parametros)
        return [self._de_fila(fila) for fila in filas]


def _filtro(mascota_id: str | None, cita_id: str | None) -> tuple[str, list[Any]]:
    condiciones: list[str] = []
    parametros: list[Any] = []
    if mascota_id is not None:
        condiciones.append("mascota_id = ?")
        parametros.append(mascota_id)
    if cita_id is not None:
        condiciones.append("cita_id = ?")
        parametros.append(cita_id)
    return (f" WHERE {' AND '.join(condiciones)}" if condiciones else ""), parametros


class RepositorioDeRecetasSql(RepositorioDeRecetas):
    _COLUMNAS = "receta_id, mascota_id, cita_id, registrada_en"

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, receta: Receta) -> None:
        self._con.ejecutar(
            f"INSERT INTO recetas ({self._COLUMNAS}) VALUES (?, ?, ?, ?)",
            (receta.receta_id, receta.mascota_id, receta.cita_id, _texto(receta.registrada_en)))
        for orden, m in enumerate(receta.medicamentos, start=1):
            self._con.ejecutar(
                "INSERT INTO receta_medicamentos (receta_id, orden, nombre, dosis, indicaciones)"
                " VALUES (?, ?, ?, ?, ?)",
                (receta.receta_id, orden, m.nombre, m.dosis, m.indicaciones))

    def _de_fila(self, fila: tuple[Any, ...]) -> Receta:
        medicamentos = tuple(
            Medicamento(nombre=n, dosis=d, indicaciones=i)
            for n, d, i in self._con.consultar(
                "SELECT nombre, dosis, indicaciones FROM receta_medicamentos"
                " WHERE receta_id = ? ORDER BY orden", (fila[0],)))
        return Receta(
            receta_id=fila[0], mascota_id=fila[1], cita_id=fila[2],
            registrada_en=datetime.fromisoformat(fila[3]), medicamentos=medicamentos)

    def obtener(self, receta_id: str) -> Receta | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM recetas WHERE receta_id = ?", (receta_id,))
        return self._de_fila(filas[0]) if filas else None

    def listar(self, *, mascota_id: str | None = None, cita_id: str | None = None
               ) -> list[Receta]:
        donde, parametros = _filtro(mascota_id, cita_id)
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM recetas{donde} ORDER BY registrada_en, receta_id",
            parametros)
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeOrdenesSql(RepositorioDeOrdenes):
    _COLUMNAS = "orden_id, mascota_id, cita_id, estudio, indicaciones, registrada_en"

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, orden: OrdenDeEstudio) -> None:
        self._con.ejecutar(
            f"INSERT INTO ordenes_estudio ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?)",
            (orden.orden_id, orden.mascota_id, orden.cita_id, orden.estudio, orden.indicaciones,
             _texto(orden.registrada_en)))

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> OrdenDeEstudio:
        return OrdenDeEstudio(
            orden_id=fila[0], mascota_id=fila[1], cita_id=fila[2], estudio=fila[3],
            indicaciones=fila[4], registrada_en=datetime.fromisoformat(fila[5]))

    def obtener(self, orden_id: str) -> OrdenDeEstudio | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM ordenes_estudio WHERE orden_id = ?", (orden_id,))
        return self._de_fila(filas[0]) if filas else None

    def listar(self, *, mascota_id: str | None = None, cita_id: str | None = None
               ) -> list[OrdenDeEstudio]:
        donde, parametros = _filtro(mascota_id, cita_id)
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM ordenes_estudio{donde} ORDER BY registrada_en, orden_id",
            parametros)
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeCobrosSql(RepositorioDeCobros):
    _COLUMNAS = "cobro_id, cita_id, mascota_id, total_centavos, metodo, cobrado_en"

    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, cobro: Cobro) -> None:
        self._con.ejecutar(
            f"INSERT INTO cobros ({self._COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?)",
            (cobro.cobro_id, cobro.cita_id, cobro.mascota_id, _centavos(cobro.total),
             cobro.metodo.value, _texto(cobro.cobrado_en)))

    @staticmethod
    def _de_fila(fila: tuple[Any, ...]) -> Cobro:
        return Cobro(
            cobro_id=fila[0], cita_id=fila[1], mascota_id=fila[2], total=_dinero(fila[3]),
            metodo=MetodoDePago(fila[4]), cobrado_en=datetime.fromisoformat(fila[5]))

    def obtener(self, cobro_id: str) -> Cobro | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM cobros WHERE cobro_id = ?", (cobro_id,))
        return self._de_fila(filas[0]) if filas else None

    def de_la_cita(self, cita_id: str) -> Cobro | None:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM cobros WHERE cita_id = ?", (cita_id,))
        return self._de_fila(filas[0]) if filas else None

    def todos(self) -> list[Cobro]:
        filas = self._con.consultar(
            f"SELECT {self._COLUMNAS} FROM cobros ORDER BY cobrado_en, cobro_id")
        return [self._de_fila(fila) for fila in filas]


class RepositorioDeEventosSql(RepositorioDeEventos):
    def __init__(self, conexion: Conexion) -> None:
        self._con = conexion

    def agregar(self, evento: EventoDeDominio) -> None:
        if not evento.agregado_tipo:
            raise ValueError(f"{evento.nombre} no declara el agregado que lo emite")
        datos = evento.a_diccionario()
        self._con.ejecutar(
            "INSERT INTO eventos_dominio (evento, agregado_tipo, agregado_id, ocurrido_en,"
            " payload_json) VALUES (?, ?, ?, ?, ?)",
            (evento.nombre, evento.agregado_tipo, evento.agregado_id, datos["ocurrido_en"],
             json.dumps(datos, ensure_ascii=False)),
        )

    def todos(self) -> list[dict[str, Any]]:
        """Los eventos en orden. `cita_id` se conserva para los eventos de una cita."""
        filas = self._con.consultar(
            "SELECT secuencia, evento, agregado_tipo, agregado_id, ocurrido_en, payload_json"
            " FROM eventos_dominio ORDER BY secuencia")
        return [
            {"secuencia": int(secuencia), "evento": evento, "agregado_tipo": tipo,
             "agregado_id": agregado_id, "cita_id": agregado_id if tipo == "Cita" else None,
             "ocurrido_en": ocurrido_en, "payload": json.loads(payload)}
            for secuencia, evento, tipo, agregado_id, ocurrido_en, payload in filas
        ]


class UnidadDeTrabajoSql(UnidadDeTrabajo):
    """Abre una conexión al entrar y la cierra al salir. Sin `commit()` se deshace todo."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._conexion: Conexion | None = None

    def __enter__(self) -> UnidadDeTrabajoSql:
        conexion = conectar(self._url)
        self._conexion = conexion
        self.servicios = RepositorioDeServiciosSql(conexion)
        self.propietarios = RepositorioDePropietariosSql(conexion)
        self.mascotas = RepositorioDeMascotasSql(conexion)
        self.citas = RepositorioDeCitasSql(conexion)
        self.vacunaciones = RepositorioDeVacunacionesSql(conexion)
        self.esquemas = RepositorioDeEsquemasSql(conexion)
        self.emergencias = RepositorioDeEmergenciasSql(conexion)
        self.notas = RepositorioDeNotasSql(conexion)
        self.hospitalizaciones = RepositorioDeHospitalizacionesSql(conexion)
        self.recetas = RepositorioDeRecetasSql(conexion)
        self.ordenes = RepositorioDeOrdenesSql(conexion)
        self.cobros = RepositorioDeCobrosSql(conexion)
        self.eventos = RepositorioDeEventosSql(conexion)
        return self

    def commit(self) -> None:
        if self._conexion is None:
            raise RuntimeError("La unidad de trabajo no está abierta")
        self._conexion.commit()

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        if self._conexion is None:
            return
        try:
            self._conexion.rollback()  # si ya hubo commit, no hace nada
        finally:
            self._conexion.cerrar()
            self._conexion = None
