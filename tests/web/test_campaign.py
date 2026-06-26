import pytest
from rifafacil.web.store import ImagenMeta, imagen_principal

ADMIN = ("admin", "secret")


# ── Lógica pura ────────────────────────────────────────────────────────────

def test_imagen_principal_lista_vacia_retorna_none():
    assert imagen_principal([]) is None


def test_imagen_principal_sin_marcada_retorna_primera():
    imgs = [ImagenMeta(filename="a.jpg"), ImagenMeta(filename="b.jpg")]
    assert imagen_principal(imgs).filename == "a.jpg"


def test_imagen_principal_con_marcada_retorna_la_correcta():
    imgs = [ImagenMeta(filename="a.jpg"), ImagenMeta(filename="b.jpg", principal=True)]
    assert imagen_principal(imgs).filename == "b.jpg"


# ── Store: campaign link ───────────────────────────────────────────────────

def test_campaign_link_vacio_por_defecto(client):
    import rifafacil.web.store as store_module
    assert store_module.obtener_campaign_link() == ""


def test_guardar_campaign_link_persiste(client):
    import rifafacil.web.store as store_module
    store_module.guardar_campaign_link("https://instagram.com/rifafacil")
    assert store_module.obtener_campaign_link() == "https://instagram.com/rifafacil"


# ── Store: imágenes ────────────────────────────────────────────────────────

def test_obtener_imagenes_vacio_por_defecto(client):
    import rifafacil.web.store as store_module
    assert store_module.obtener_imagenes() == []


def test_guardar_y_obtener_imagenes(client):
    import rifafacil.web.store as store_module
    imgs = [ImagenMeta(filename="x.jpg"), ImagenMeta(filename="y.jpg", principal=True)]
    store_module.guardar_imagenes(imgs)
    result = store_module.obtener_imagenes()
    assert len(result) == 2
    assert result[1].principal is True


# ── Rutas HTTP ─────────────────────────────────────────────────────────────

def test_post_config_campaign_persiste_link(client):
    import rifafacil.web.store as store_module
    response = client.post("/admin/config/campaign", data={"link": "https://ig.com/test"}, auth=ADMIN)
    assert response.status_code == 200
    assert store_module.obtener_campaign_link() == "https://ig.com/test"


def test_subir_imagen_guarda_metadata(client):
    import rifafacil.web.store as store_module
    response = client.post(
        "/admin/imagenes/subir",
        files={"file": ("foto.jpg", b"fake image data", "image/jpeg")},
        auth=ADMIN,
    )
    assert response.status_code == 200
    imagenes = store_module.obtener_imagenes()
    assert len(imagenes) == 1
    assert imagenes[0].filename.endswith(".jpg")


def test_subir_imagen_rechaza_archivos_mayores_a_2mb(client):
    big = b"x" * (2 * 1024 * 1024 + 1)
    response = client.post(
        "/admin/imagenes/subir",
        files={"file": ("grande.jpg", big, "image/jpeg")},
        auth=ADMIN,
    )
    assert response.status_code == 400


def test_subir_imagen_rechaza_mas_de_10_imagenes(client):
    import rifafacil.web.store as store_module
    store_module.guardar_imagenes([ImagenMeta(filename=f"img{i}.jpg") for i in range(10)])
    response = client.post(
        "/admin/imagenes/subir",
        files={"file": ("extra.jpg", b"data", "image/jpeg")},
        auth=ADMIN,
    )
    assert response.status_code == 400


def test_marcar_imagen_como_principal(client):
    import rifafacil.web.store as store_module
    store_module.guardar_imagenes([ImagenMeta(filename="a.jpg"), ImagenMeta(filename="b.jpg")])
    response = client.post("/admin/imagenes/b.jpg/principal", auth=ADMIN)
    assert response.status_code == 200
    updated = store_module.obtener_imagenes()
    assert updated[0].principal is False
    assert updated[1].principal is True


def test_eliminar_imagen_la_quita_de_metadata(client):
    import rifafacil.web.store as store_module
    store_module.guardar_imagenes([ImagenMeta(filename="a.jpg"), ImagenMeta(filename="b.jpg")])
    response = client.delete("/admin/imagenes/a.jpg", auth=ADMIN)
    assert response.status_code == 200
    remaining = store_module.obtener_imagenes()
    assert len(remaining) == 1
    assert remaining[0].filename == "b.jpg"


def test_subir_sin_credenciales_retorna_401(client):
    response = client.post(
        "/admin/imagenes/subir",
        files={"file": ("foto.jpg", b"data", "image/jpeg")},
    )
    assert response.status_code == 401
