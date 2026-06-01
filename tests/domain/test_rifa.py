import pytest

from rifafacil.domain.rifa import Rifa


# ── Ciclo 1 ── Crear una rifa ──────────────────────────────────────────────

def test_crear_rifa():
    rifa = Rifa.crear(nombre="Rifa Navidad", precio_boleto=500, cantidad_boletos=100)

    assert rifa.nombre == "Rifa Navidad"
    assert rifa.precio_boleto == 500
    assert rifa.cantidad_boletos == 100


# ── Ciclo 2 ── Precio debe ser positivo ───────────────────────────────────

def test_precio_negativo_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=-1, cantidad_boletos=10)


def test_precio_cero_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=0, cantidad_boletos=10)


# ── Ciclo 3 ── Límites de rifas solidarias ────────────────────────────────

def test_precio_boleto_no_puede_superar_10000():
    with pytest.raises(ValueError, match=r"10\.000"):
        Rifa.crear(nombre="Rifa X", precio_boleto=10_001, cantidad_boletos=1)


def test_precio_boleto_exactamente_en_el_limite_es_valido():
    rifa = Rifa.crear(nombre="Rifa X", precio_boleto=10_000, cantidad_boletos=1)

    assert rifa.precio_boleto == 10_000


def test_total_rifa_no_puede_superar_2_500_000():
    with pytest.raises(ValueError, match=r"2\.500\.000"):
        Rifa.crear(nombre="Rifa X", precio_boleto=10_000, cantidad_boletos=251)


def test_total_rifa_exactamente_en_el_limite_es_valido():
    rifa = Rifa.crear(nombre="Rifa X", precio_boleto=10_000, cantidad_boletos=250)

    assert rifa.precio_boleto * rifa.cantidad_boletos == 2_500_000
