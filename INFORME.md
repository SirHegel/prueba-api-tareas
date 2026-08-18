# INFORME de revision — api-tareas

Revision de coherencia y ejecucion de tests del proyecto
`api-tareas/`, realizada el 2026-08-18.

---

## 1. Resumen del estado

**El proyecto esta coherente y funcionando.** Los 27 tests pasan, `app.py`
implementa exactamente los 5 endpoints y los codigos de estado de
`CONTRATO.md`, y los 7 ejemplos de `curl` del `README.md` se verificaron
**contra un servidor real** (no solo leyendo el codigo): todos devuelven la
ruta, el codigo de estado y el cuerpo documentados.

Se encontraron **6 incidencias**, todas de documentacion o empaquetado —
ninguna afecta al comportamiento de la API. Se corrigieron 5; queda 1
pendiente por requerir instalar herramienta externa.

| Comprobacion pedida | Resultado |
|---|---|
| `pytest -q` | 27 passed |
| `app.py` implementa los endpoints y codigos de `CONTRATO.md` | Correcto, sin desviaciones |
| Ejemplos de `curl` del README coinciden con la realidad | Correcto tras corregir el formato de `creada_en` |
| Existen `arquitectura.png` y `arquitectura.md` | Existen; el `.png` no era un PNG (corregido) |
| El README los referencia bien | El `.md` no se referenciaba (corregido) |
| Sin imports rotos ni ficheros duplicados, todo en una carpeta | Correcto |
| `requirements.txt` cubre lo que se importa | Correcto |

---

## 2. Salida de pytest

Ejecutado con el interprete del entorno del proyecto
(`./.venv/bin/python -m pytest -q`):

```
...........................                                              [100%]
=============================== warnings summary ===============================
test_api.py::test_salud
  .venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
27 passed, 1 warning in 0.33s
```

Codigo de salida: `0`. Reparto: 15 tests de API (`test_api.py`) + 12 tests de
repositorio (`test_repositorio.py`).

> Nota: antes de la correccion #5, este mismo comando **no mostraba la linea
> `27 passed`** (ver incidencias).

---

## 3. Verificacion de los ejemplos de curl contra servidor real

Se arranco `uvicorn app:app` sobre una base temporal y se ejecutaron los
ejemplos del README uno a uno. Resultado observado:

| # | Peticion | Codigo real | Esperado en README | OK |
|---|---|---|---|---|
| 1 | `POST /tareas` | 201 | 201 | Si |
| 2 | `GET /tareas` | 200 | 200 | Si |
| 3 | `GET /tareas?completada=true` | 200 `[]` | 200 `[]` | Si |
| 4 | `GET /tareas?completada=false` | 200 con la tarea | idem | Si |
| 5 | `PATCH /tareas/1/completar` | 200 `completada:true` | idem | Si |
| 6 | `DELETE /tareas/1` | 204 sin cuerpo | 204 sin cuerpo | Si |
| 7 | `DELETE /tareas/1` (repetido) | 404 `{"detalle":...}` | 404 `{"detalle":...}` | Si |
| 8 | `GET /salud` | 200 `{"estado":"ok"}` | 200 `{"estado":"ok"}` | Si |
| 9 | `POST /tareas` titulo vacio | 422 | 422 | Si |

Las rutas y los codigos de estado coincidian ya al 100%. La unica desviacion
estaba en el valor de ejemplo de `creada_en` (incidencia #1).

---

## 4. Incidencias encontradas

### Corregidas

**#1 — El `creada_en` de los ejemplos no era el formato real.**
`README.md` (4 apariciones) y `CONTRATO.md` (1) mostraban
`"2026-08-18T06:48:00+00:00"`, pero la API serializa con microsegundos y
sufijo `Z`: `"2026-08-18T11:52:58.018731Z"` (Pydantic v2 normaliza asi el UTC).
Ambos son ISO 8601 valido, asi que la regla del contrato se cumplia, pero
quien copiara el ejemplo esperaria un texto que nunca llega.
*Corregido:* ejemplos actualizados al valor realmente observado, mas una nota
explicita del formato en el README y una aclaracion en la tabla de modelos de
`CONTRATO.md`.

**#2 — `arquitectura.png` no era un PNG.**
El fichero tenia extension `.png` pero su contenido era JPEG
(`JPEG image data, JFIF standard 1.01, 1376x768`). Los navegadores lo
renderizaban igual por sniffing, pero cualquier herramienta que valide por
extension o cabecera fallaba.
*Corregido:* reconvertido a PNG real con ImageMagick
(`PNG image data, 1376 x 768, 8-bit/color RGB`), mismas dimensiones y diagrama
intacto (verificado visualmente).

**#3 — El README no referenciaba `arquitectura.md`.**
Solo enlazaba la imagen; la fuente Mermaid editable no aparecia por ningun
lado, ni en el arbol de ficheros ni en la seccion de arquitectura.
*Corregido:* la seccion "Arquitectura" ahora enlaza `arquitectura.md` como
fuente editable del diagrama.

**#4 — El arbol de ficheros del README estaba incompleto.**
Faltaban 4 ficheros que si existen: `pytest.ini`, `conftest.py`,
`test_repositorio.py` y `arquitectura.md`. Ademas describia `test_api.py` como
"Tests con httpx / pytest" sin distinguirlo del otro fichero de tests.
*Corregido:* arbol completo y descripciones ajustadas.

**#5 — `pytest -q` ocultaba el resultado.**
`pytest.ini` traia `addopts = -q`, asi que el comando documentado y el pedido
en esta revision (`pytest -q`) se resolvian como `-qq`, modo en el que pytest
**suprime la linea de resumen**: no se veia ni `27 passed` ni el recuento de
fallos. Un fallo se habria notado, pero el exito no dejaba constancia legible.
*Corregido:* eliminado `addopts = -q` de `pytest.ini`. `testpaths = .` se
mantiene. Ahora tanto `pytest` como `pytest -q` muestran el resumen.

### Pendientes

**#6 — El diagrama no incluye `GET /salud`.**
Tanto `arquitectura.md` como `arquitectura.png` listan solo los 4 endpoints de
tareas (`POST /tareas`, `GET /tareas`, `PATCH /tareas/{id}/completar`,
`DELETE /tareas/{id}`) y omiten la sonda de vida `GET /salud`, que si esta en
el contrato, en el README y en `app.py`.
*No corregido a proposito:* editar solo `arquitectura.md` dejaria la fuente
Mermaid y la imagen contando cosas distintas, que es peor que la omision
actual. Regenerar el `.png` requiere `@mermaid-js/mermaid-cli`, que no esta
instalado y arrastra una descarga de red mas un Chromium headless — fuera del
alcance de "arreglar desajustes pequenos".
*Para cerrarlo:* anadir la linea `GET /salud` al bloque `B[...]` de
`arquitectura.md` y re-renderizar con
`npx @mermaid-js/mermaid-cli -i arquitectura.md -o arquitectura.png`.

### Observaciones menores (sin accion)

- **Aviso de deprecacion:** `starlette.testclient` avisa de que `httpx` esta
  deprecado a favor de `httpx2`. Los 27 tests pasan igualmente. Cambiar la
  dependencia es una decision de mantenimiento, no un desajuste de coherencia,
  asi que `requirements.txt` se deja como esta.
- **Sin `.gitignore`:** conviven `__pycache__/`, `.pytest_cache/` y `.venv/`
  con el codigo. No molesta al funcionamiento; solo lo notaria un `git add .`.

---

## 5. Comprobaciones que salieron limpias

- **Endpoints y codigos vs `CONTRATO.md`:** los 5 endpoints coinciden uno a
  uno, incluidos `201`, `200`, `204`, `404` y `422`, el filtro opcional
  `?completada=`, la idempotencia del `PATCH` y el manejador de `HTTPException`
  que reescribe los errores a `{"detalle": ...}` en lugar de `detail`.
- **Imports:** los 5 modulos (`db`, `schemas`, `repositorio`, `app`, `main`)
  importan sin error. No hay imports rotos ni circulares.
- **Ficheros duplicados:** ninguno (comprobado por hash de contenido).
- **Una sola carpeta:** los 15 ficheros del proyecto viven en
  `api-tareas/`, sin subcarpetas ni proyectos paralelos.
- **`requirements.txt`:** cubre las 5 dependencias externas que se importan
  (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, esta ultima necesaria
  para `fastapi.testclient`). El resto de imports son de la libreria estandar.
- **Sin bases de datos sueltas** en el repositorio tras ejecutar tests y
  servidor: los dos usan ficheros temporales.
