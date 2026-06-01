import pytest
from decimal import Decimal

from rifafacil.domain.rifa import Rifa


# ── Ciclo 1 ── Crear una rifa ──────────────────────────────────────────────

def test_crear_rifa():
    rifa = Rifa.crear(nombre="Rifa Navidad", precio_boleto=Decimal("500.00"))

    assert rifa.nombre == "Rifa Navidad"
    assert rifa.precio_boleto == Decimal("500.00")


# ── Ciclo 2 ── Precio del boleto debe ser positivo ─────────────────────────

def test_precio_negativo_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=Decimal("-1.00"))


def test_precio_cero_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        Rifa.crear(nombre="Rifa Navidad", precio_boleto=Decimal("0.00"))
