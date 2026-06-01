import pytest

from rifafacil.domain.rifa import Rifa


# ── Ciclo 1 ── Crear una rifa ──────────────────────────────────────────────

def test_crear_rifa():
    rifa = Rifa.crear(nombre="Rifa Navidad", precio_boleto=500)

    assert rifa.nombre == "Rifa Navidad"
    assert rifa.precio_boleto == 500


# ── Ciclo 2 ── Precio debe ser positivo ───────────────────────────────────

def test_precio_negativo_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=-1)


def test_precio_cero_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=0)
