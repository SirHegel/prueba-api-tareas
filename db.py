"""Acceso a SQLite: ruta de la base, conexion y creacion del esquema."""

import os
import sqlite3

# Ruta del fichero SQLite. Configurable con la variable de entorno TAREAS_DB.
RUTA_DB: str = os.environ.get("TAREAS_DB", "tareas.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    completada INTEGER NOT NULL DEFAULT 0,
    creada_en TEXT NOT NULL
)
"""


def get_conexion() -> sqlite3.Connection:
    """Abre una conexion a RUTA_DB con filas accesibles por nombre de columna."""
    conn = sqlite3.connect(RUTA_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(ruta: str = "tareas.db") -> None:
    """Crea la tabla 'tareas' en `ruta` si aun no existe."""
    conn = sqlite3.connect(ruta)
    try:
        conn.execute(ESQUEMA)
        conn.commit()
    finally:
        conn.close()
