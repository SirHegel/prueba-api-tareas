"""Fixtures compartidas por la bateria de tests: base temporal y cliente HTTP."""

import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# db.RUTA_DB se resuelve al importar db.py, asi que TAREAS_DB tiene que estar
# puesto antes de que cualquier modulo importe db o app. Esta base de import
# solo cubre esa ventana: cada test recibe luego la suya propia via tmp_path.
_BASE_IMPORT = Path(tempfile.mkdtemp(prefix="tareas-import-")) / "tareas.db"
os.environ["TAREAS_DB"] = str(_BASE_IMPORT)

import db  # noqa: E402

db.init_db(str(_BASE_IMPORT))


@pytest.fixture
def ruta_db(tmp_path, monkeypatch):
    """Apunta TAREAS_DB a un fichero temporal recien inicializado."""
    ruta = tmp_path / "tareas.db"
    monkeypatch.setenv("TAREAS_DB", str(ruta))
    # db.RUTA_DB ya se leyo del entorno al importar, hay que reescribirlo.
    monkeypatch.setattr(db, "RUTA_DB", str(ruta))
    db.init_db(str(ruta))
    return ruta


@pytest.fixture
def conexion(ruta_db):
    """Conexion sqlite abierta sobre la base temporal del test."""
    conn = db.get_conexion()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def cliente(ruta_db):
    """TestClient sobre app:app, hablando con la base temporal del test."""
    if not (RAIZ / "app.py").exists():
        pytest.skip("app.py todavia no existe")

    from fastapi.testclient import TestClient

    # Recargar por si app.py abre la conexion al importarse: asi la coge de la
    # RUTA_DB de este test y no de la base de la ventana de import.
    modulo = importlib.reload(importlib.import_module("app"))
    with TestClient(modulo.app) as c:
        yield c
