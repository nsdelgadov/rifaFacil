from rifafacil.domain.estado_boleto import EstadoBoleto

ADMIN = ("admin", "secret")
WRONG = ("admin", "wrong")


def test_admin_sin_credenciales_retorna_401(client):
    response = client.get("/admin")
    assert response.status_code == 401


def test_admin_con_credenciales_incorrectas_retorna_401(client):
    response = client.get("/admin", auth=WRONG)
    assert response.status_code == 401


def test_admin_con_credenciales_correctas_retorna_200(client):
    response = client.get("/admin", auth=ADMIN)
    assert response.status_code == 200


def test_confirmar_pago_cambia_estado_a_pagado(client):
    response = client.post("/admin/boletos/1/confirmar", auth=ADMIN)
    assert response.status_code == 200
    assert "pagado" in response.text.lower()


def test_liberar_boleto_reservado_lo_deja_disponible(client):
    response = client.post("/admin/boletos/1/liberar", auth=ADMIN)
    assert response.status_code == 200
    assert "disponible" in response.text.lower()


def test_confirmar_sin_credenciales_retorna_401(client):
    response = client.post("/admin/boletos/1/confirmar")
    assert response.status_code == 401


def test_liberar_sin_credenciales_retorna_401(client):
    response = client.post("/admin/boletos/1/liberar")
    assert response.status_code == 401


def test_admin_tabla_sin_credenciales_retorna_401(client):
    response = client.get("/admin/tabla")
    assert response.status_code == 401


def test_admin_tabla_con_credenciales_retorna_200(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert response.status_code == 200


def test_admin_tabla_muestra_boletos_ocupados(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert "reservado" in response.text.lower()


def test_admin_tabla_incluye_polling_htmx(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert 'hx-get="/admin/tabla"' in response.text
    assert "hx-trigger" in response.text


def test_botones_accion_deshabilitan_ambos_botones(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert "btn-confirmar-1" in response.text
    assert "btn-liberar-1" in response.text
    assert response.text.count('hx-disabled-elt="#btn-confirmar-1, #btn-liberar-1"') == 2


def test_botones_accion_muestran_texto_cargando(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert "Cargando" in response.text
