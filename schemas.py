"""Modelos Pydantic v2 compartidos por toda la API de tareas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TareaCrear(BaseModel):
    """Cuerpo aceptado por POST /tareas."""

    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str | None = None


class TareaSalida(BaseModel):
    """Representacion publica de una tarea."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descripcion: str | None
    completada: bool
    creada_en: datetime


class MensajeError(BaseModel):
    """Cuerpo de las respuestas de error (404 y similares)."""

    detalle: str
