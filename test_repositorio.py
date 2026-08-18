"""Tests del CRUD de repositorio.py contra una conexion sqlite temporal."""

from datetime import datetime

import repositorio as repo


def test_crear_tarea_devuelve_la_tarea_creada(conexion):
    tarea = repo.crear_tarea(conexion, "Comprar pan", "Integral")

    assert isinstance(tarea["id"], int)
    assert tarea["titulo"] == "Comprar pan"
    assert tarea["descripcion"] == "Integral"
    assert tarea["completada"] is False
    # creada_en se guarda en ISO 8601 y tiene que ser parseable.
    assert datetime.fromisoformat(tarea["creada_en"])


def test_crear_tarea_acepta_descripcion_nula(conexion):
    tarea = repo.crear_tarea(conexion, "Sin descripcion", None)

    assert tarea["descripcion"] is None


def test_listar_tareas_vacio(conexion):
    assert repo.listar_tareas(conexion) == []


def test_listar_tareas_ordena_por_id(conexion):
    repo.crear_tarea(conexion, "Primera", None)
    repo.crear_tarea(conexion, "Segunda", None)
    repo.crear_tarea(conexion, "Tercera", None)

    titulos = [t["titulo"] for t in repo.listar_tareas(conexion)]

    assert titulos == ["Primera", "Segunda", "Tercera"]


def test_listar_tareas_filtra_por_completada(conexion):
    pendiente = repo.crear_tarea(conexion, "Pendiente", None)
    hecha = repo.crear_tarea(conexion, "Hecha", None)
    repo.completar_tarea(conexion, hecha["id"])

    completadas = repo.listar_tareas(conexion, completada=True)
    pendientes = repo.listar_tareas(conexion, completada=False)

    assert [t["id"] for t in completadas] == [hecha["id"]]
    assert [t["id"] for t in pendientes] == [pendiente["id"]]
    assert len(repo.listar_tareas(conexion)) == 2


def test_obtener_tarea_existente(conexion):
    creada = repo.crear_tarea(conexion, "Leer", "Un rato")

    assert repo.obtener_tarea(conexion, creada["id"]) == creada


def test_obtener_tarea_inexistente_devuelve_none(conexion):
    assert repo.obtener_tarea(conexion, 9999) is None


def test_completar_tarea_marca_completada(conexion):
    creada = repo.crear_tarea(conexion, "Regar", None)

    completada = repo.completar_tarea(conexion, creada["id"])

    assert completada["completada"] is True
    assert completada["id"] == creada["id"]
    # y el cambio queda persistido, no solo en el dict devuelto
    assert repo.obtener_tarea(conexion, creada["id"])["completada"] is True


def test_completar_tarea_es_idempotente(conexion):
    creada = repo.crear_tarea(conexion, "Regar", None)
    primera = repo.completar_tarea(conexion, creada["id"])

    segunda = repo.completar_tarea(conexion, creada["id"])

    assert segunda == primera


def test_completar_tarea_inexistente_devuelve_none(conexion):
    assert repo.completar_tarea(conexion, 9999) is None


def test_borrar_tarea_existente(conexion):
    creada = repo.crear_tarea(conexion, "Tirar basura", None)

    assert repo.borrar_tarea(conexion, creada["id"]) is True
    assert repo.obtener_tarea(conexion, creada["id"]) is None
    assert repo.listar_tareas(conexion) == []


def test_borrar_tarea_inexistente_devuelve_false(conexion):
    assert repo.borrar_tarea(conexion, 9999) is False
