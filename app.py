"""Rutas FastAPI de la API de tareas, montadas sobre repositorio.py."""

import sqlite3
from collections.abc import Iterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse

import db
import repositorio
from schemas import MensajeError, TareaCrear, TareaSalida

# Respuestas de error declaradas en el contrato, para que salgan en /docs.
RESPUESTA_404 = {404: {"model": MensajeError, "description": "Tarea no encontrada"}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea el esquema de la base antes de aceptar peticiones."""
    db.init_db(db.RUTA_DB)
    yield


app = FastAPI(title="API Tareas", version="1.0.0", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def manejador_http(request, exc: HTTPException) -> JSONResponse:
    """Reescribe los errores al modelo MensajeError: clave 'detalle', no 'detail'."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detalle": exc.detail},
        headers=getattr(exc, "headers", None),
    )


def get_db() -> Iterator[sqlite3.Connection]:
    """Abre una conexion por peticion y la cierra al terminar."""
    conn = db.get_conexion()
    try:
        yield conn
    finally:
        conn.close()


def _no_encontrada() -> HTTPException:
    return HTTPException(status_code=404, detail="Tarea no encontrada")


@app.get("/salud")
def salud() -> dict[str, str]:
    """Sonda de vida: no toca la base de datos."""
    return {"estado": "ok"}


@app.post("/tareas", response_model=TareaSalida, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    datos: TareaCrear,
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Crea una tarea nueva, siempre con completada = false."""
    return repositorio.crear_tarea(conn, datos.titulo, datos.descripcion)


@app.get("/tareas", response_model=list[TareaSalida])
def listar_tareas(
    completada: bool | None = Query(
        default=None,
        description="true solo completadas, false solo pendientes, ausente todas",
    ),
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    """Lista las tareas por id ascendente, con filtro opcional por estado."""
    return repositorio.listar_tareas(conn, completada)


@app.patch(
    "/tareas/{tarea_id}/completar",
    response_model=TareaSalida,
    responses=RESPUESTA_404,
)
def completar_tarea(
    tarea_id: int,
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Marca la tarea como completada. Idempotente: repetirlo devuelve 200."""
    tarea = repositorio.completar_tarea(conn, tarea_id)
    if tarea is None:
        raise _no_encontrada()
    return tarea


@app.delete(
    "/tareas/{tarea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPUESTA_404,
)
def borrar_tarea(
    tarea_id: int,
    conn: sqlite3.Connection = Depends(get_db),
) -> Response:
    """Borra la tarea y responde 204 sin cuerpo."""
    if not repositorio.borrar_tarea(conn, tarea_id):
        raise _no_encontrada()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
