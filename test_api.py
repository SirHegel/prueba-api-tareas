"""Tests de los endpoints HTTP definidos en CONTRATO.md."""


def crear(cliente, titulo="Comprar pan", descripcion=None):
    """Atajo: crea una tarea via API y devuelve su cuerpo JSON."""
    respuesta = cliente.post(
        "/tareas", json={"titulo": titulo, "descripcion": descripcion}
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_salud(cliente):
    respuesta = cliente.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_crear_tarea_devuelve_201(cliente):
    respuesta = cliente.post(
        "/tareas", json={"titulo": "Comprar pan", "descripcion": "Integral"}
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["titulo"] == "Comprar pan"
    assert cuerpo["descripcion"] == "Integral"
    assert cuerpo["completada"] is False
    assert cuerpo["creada_en"]


def test_crear_tarea_sin_descripcion(cliente):
    respuesta = cliente.post("/tareas", json={"titulo": "Solo titulo"})

    assert respuesta.status_code == 201
    assert respuesta.json()["descripcion"] is None


def test_crear_tarea_titulo_vacio_devuelve_422(cliente):
    respuesta = cliente.post("/tareas", json={"titulo": "", "descripcion": None})

    assert respuesta.status_code == 422


def test_crear_tarea_sin_titulo_devuelve_422(cliente):
    respuesta = cliente.post("/tareas", json={"descripcion": "Huerfana"})

    assert respuesta.status_code == 422


def test_crear_tarea_titulo_demasiado_largo_devuelve_422(cliente):
    respuesta = cliente.post("/tareas", json={"titulo": "x" * 201})

    assert respuesta.status_code == 422


def test_listar_tareas_vacio(cliente):
    respuesta = cliente.get("/tareas")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_tareas_devuelve_lo_creado(cliente):
    primera = crear(cliente, "Primera")
    segunda = crear(cliente, "Segunda")

    respuesta = cliente.get("/tareas")

    assert respuesta.status_code == 200
    assert [t["id"] for t in respuesta.json()] == [primera["id"], segunda["id"]]


def test_listar_tareas_filtra_por_completada(cliente):
    pendiente = crear(cliente, "Pendiente")
    hecha = crear(cliente, "Hecha")
    cliente.patch(f"/tareas/{hecha['id']}/completar")

    completadas = cliente.get("/tareas", params={"completada": "true"})
    pendientes = cliente.get("/tareas", params={"completada": "false"})

    assert completadas.status_code == 200
    assert [t["id"] for t in completadas.json()] == [hecha["id"]]
    assert pendientes.status_code == 200
    assert [t["id"] for t in pendientes.json()] == [pendiente["id"]]


def test_completar_tarea_devuelve_200(cliente):
    creada = crear(cliente, "Regar las plantas")

    respuesta = cliente.patch(f"/tareas/{creada['id']}/completar")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creada["id"]
    assert cuerpo["completada"] is True


def test_completar_tarea_es_idempotente(cliente):
    creada = crear(cliente, "Regar las plantas")
    primera = cliente.patch(f"/tareas/{creada['id']}/completar")

    segunda = cliente.patch(f"/tareas/{creada['id']}/completar")

    assert segunda.status_code == 200
    assert segunda.json() == primera.json()


def test_completar_tarea_inexistente_devuelve_404(cliente):
    respuesta = cliente.patch("/tareas/9999/completar")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": "Tarea no encontrada"}


def test_borrar_tarea_devuelve_204(cliente):
    creada = crear(cliente, "Tirar la basura")

    respuesta = cliente.delete(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get("/tareas").json() == []


def test_borrar_dos_veces_devuelve_404(cliente):
    creada = crear(cliente, "Tirar la basura")
    cliente.delete(f"/tareas/{creada['id']}")

    respuesta = cliente.delete(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detalle": "Tarea no encontrada"}


def test_cada_test_arranca_con_base_limpia(cliente):
    # Guardia del aislamiento: si la fixture no cambiara de base temporal,
    # las tareas de los tests anteriores apareceria aqui.
    assert cliente.get("/tareas").json() == []
