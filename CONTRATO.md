# Contrato de la API de tareas

Documento de referencia para que cada parte del equipo trabaje sin pisarse.
Base: `http://localhost:8000`. Todo el cuerpo va en JSON (`application/json`).

## Modelos (definidos en `schemas.py`)

**TareaCrear** (entrada)

| Campo | Tipo | Reglas |
|---|---|---|
| `titulo` | `str` | obligatorio, `min_length=1`, `max_length=200` |
| `descripcion` | `str \| None` | opcional, por defecto `null` |

**TareaSalida** (salida)

| Campo | Tipo |
|---|---|
| `id` | `int` |
| `titulo` | `str` |
| `descripcion` | `str \| None` |
| `completada` | `bool` |
| `creada_en` | `datetime` (ISO 8601, UTC; se serializa con sufijo `Z`) |

**MensajeError** (salida de error)

| Campo | Tipo |
|---|---|
| `detalle` | `str` |

## Endpoints

### POST /tareas
Crea una tarea. La tarea nace con `completada = false`.

- Cuerpo: `TareaCrear`
- `201 Created` -> `TareaSalida`
- `422 Unprocessable Entity` -> validacion de Pydantic (titulo vacio o mayor de 200)

```json
// peticion
{"titulo": "Comprar pan", "descripcion": "Integral"}
// respuesta 201
{"id": 1, "titulo": "Comprar pan", "descripcion": "Integral",
 "completada": false, "creada_en": "2026-08-18T11:52:58.018731Z"}
```

### GET /tareas?completada=
Lista las tareas ordenadas por `id` ascendente.

- Query `completada` (opcional, `bool`): `true` solo completadas, `false` solo
  pendientes, ausente todas.
- `200 OK` -> `list[TareaSalida]` (lista vacia si no hay coincidencias)

### PATCH /tareas/{id}/completar
Marca la tarea como completada. Es idempotente: repetirlo sobre una tarea ya
completada devuelve `200` con el mismo resultado.

- `200 OK` -> `TareaSalida`
- `404 Not Found` -> `MensajeError` con `{"detalle": "Tarea no encontrada"}`

### DELETE /tareas/{id}
Borra la tarea.

- `204 No Content` -> sin cuerpo
- `404 Not Found` -> `MensajeError` con `{"detalle": "Tarea no encontrada"}`

### GET /salud
Sonda de vida del servicio, sin tocar la base de datos.

- `200 OK` -> `{"estado": "ok"}`

## Errores

Cualquier `404` responde con el modelo `MensajeError`, es decir la clave
`detalle` (no `detail`). Quien monte `app.py` debe registrar un manejador de
`HTTPException` que reescriba la respuesta a `{"detalle": ...}`.

## Reparto de ficheros

| Fichero | Contenido | Duenio |
|---|---|---|
| `schemas.py` | modelos Pydantic v2 | cimientos (hecho) |
| `db.py` | `RUTA_DB`, `get_conexion()`, `init_db(ruta)` | cimientos (hecho) |
| `repositorio.py` | CRUD puro sobre la conexion | cimientos (hecho) |
| `app.py` | rutas FastAPI sobre `repositorio` | tarea de API |
| `test_*.py` | tests con `httpx` / `pytest` | tarea de tests |
| `README.md`, diagrama | documentacion | tarea de docs |

## Capa de datos

- Tabla `tareas`: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `titulo TEXT NOT NULL`,
  `descripcion TEXT`, `completada INTEGER NOT NULL DEFAULT 0`,
  `creada_en TEXT NOT NULL` (ISO 8601 UTC).
- `db.RUTA_DB` se lee del entorno `TAREAS_DB` (default `tareas.db`); los tests
  deben apuntarlo a un fichero temporal antes de importar la app.
- `repositorio.py` recibe siempre la conexion como primer argumento y devuelve
  `dict` planos, listos para `TareaSalida.model_validate(...)`. `completar_tarea`
  y `obtener_tarea` devuelven `None` cuando el id no existe; `borrar_tarea`
  devuelve `False`. Traducir eso a `404` es responsabilidad de `app.py`.
