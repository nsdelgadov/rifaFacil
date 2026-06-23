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


def test_tabla_muestra_fecha_de_reserva(client):
    response = client.get("/admin/tabla", auth=ADMIN)
    assert "15/01 10:30" in response.text


def test_config_refresh_persiste_valor_en_repositorio(client):
    import rifafacil.web.store as store_module
    client.post("/admin/config/refresh", data={"segundos": "30"}, auth=ADMIN)
    assert store_module.obtener_refresh_segundos() == 30


# ── Sort y búsqueda ────────────────────────────────────────────────────────

def test_ordenar_por_estado_asc_pone_reservados_antes_que_pagados(client_completo):
    response = client_completo.get("/admin/tabla?orden=estado&dir=asc", auth=ADMIN)
    text = response.text
    assert text.index("Ana") < text.index("Carlos")
    assert text.index("Bob") < text.index("Carlos")


def test_ordenar_por_estado_desc_pone_pagados_primero(client_completo):
    response = client_completo.get("/admin/tabla?orden=estado&dir=desc", auth=ADMIN)
    text = response.text
    assert text.index("Carlos") < text.index("Ana")
    assert text.index("Carlos") < text.index("Bob")


def test_ordenar_por_reservado_asc_pone_mas_antiguo_primero(client_completo):
    response = client_completo.get("/admin/tabla?orden=reservado_en&dir=asc", auth=ADMIN)
    text = response.text
    assert text.index("Ana") < text.index("Carlos") < text.index("Bob")


def test_ordenar_por_reservado_desc_pone_mas_reciente_primero(client_completo):
    response = client_completo.get("/admin/tabla?orden=reservado_en&dir=desc", auth=ADMIN)
    text = response.text
    assert text.index("Bob") < text.index("Carlos") < text.index("Ana")


def test_buscar_por_nombre_filtra_resultados(client_completo):
    response = client_completo.get("/admin/tabla?q=Ana", auth=ADMIN)
    assert "Ana" in response.text
    assert "Bob" not in response.text
    assert "Carlos" not in response.text


def test_buscar_por_numero_filtra_resultados(client_completo):
    response = client_completo.get("/admin/tabla?q=003", auth=ADMIN)
    assert "Carlos" in response.text
    assert "Ana" not in response.text
    assert "Bob" not in response.text


def test_busqueda_sin_resultados_muestra_mensaje(client_completo):
    response = client_completo.get("/admin/tabla?q=zzz", auth=ADMIN)
    assert "Sin resultados" in response.text


def test_encabezados_estado_y_reservado_son_clicables(client_completo):
    response = client_completo.get("/admin/tabla", auth=ADMIN)
    assert 'hx-get="/admin/tabla?orden=estado' in response.text
    assert 'hx-get="/admin/tabla?orden=reservado_en' in response.text


def test_tabla_tiene_input_busqueda(client_completo):
    response = client_completo.get("/admin/tabla", auth=ADMIN)
    assert 'id="admin-buscar"' in response.text
