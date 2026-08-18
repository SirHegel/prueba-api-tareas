"""Operaciones CRUD puras sobre una conexion sqlite3 ya abierta."""

import sqlite3
from datetime import datetime, timezone


def _a_dict(fila: sqlite3.Row) -> dict:
    """Convierte una fila de 'tareas' al dict que consume TareaSalida."""
    return {
        "id": fila["id"],
        "titulo": fila["titulo"],
        "descripcion": fila["descripcion"],
        "completada": bool(fila["completada"]),
        "creada_en": fila["creada_en"],
    }


def crear_tarea(conn: sqlite3.Connection, titulo: str, descripcion: str | None) -> dict:
    """Inserta una tarea nueva (sin completar) y devuelve la tarea creada."""
    creada_en = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO tareas (titulo, descripcion, completada, creada_en)"
        " VALUES (?, ?, 0, ?)",
        (titulo, descripcion, creada_en),
    )
    conn.commit()
    return obtener_tarea(conn, cur.lastrowid)


def listar_tareas(conn: sqlite3.Connection, completada: bool | None = None) -> list[dict]:
    """Lista las tareas, opcionalmente filtrando por estado de completado."""
    if completada is None:
        filas = conn.execute("SELECT * FROM tareas ORDER BY id").fetchall()
    else:
        filas = conn.execute(
            "SELECT * FROM tareas WHERE completada = ? ORDER BY id",
            (int(completada),),
        ).fetchall()
    return [_a_dict(f) for f in filas]


def obtener_tarea(conn: sqlite3.Connection, id: int) -> dict | None:
    """Devuelve la tarea con ese id, o None si no existe."""
    fila = conn.execute("SELECT * FROM tareas WHERE id = ?", (id,)).fetchone()
    return _a_dict(fila) if fila is not None else None


def completar_tarea(conn: sqlite3.Connection, id: int) -> dict | None:
    """Marca la tarea como completada. None si el id no existe."""
    cur = conn.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (id,))
    conn.commit()
    if cur.rowcount == 0:
        return None
    return obtener_tarea(conn, id)


def borrar_tarea(conn: sqlite3.Connection, id: int) -> bool:
    """Borra la tarea. True si se borro algo, False si el id no existia."""
    cur = conn.execute("DELETE FROM tareas WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0
