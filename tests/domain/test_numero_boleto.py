import pytest

from rifafacil.domain.numero_boleto import NumeroBoleto


def test_numero_boleto_valido():
    n = NumeroBoleto(valor=42)
    assert n.valor == 42


def test_numero_boleto_cero_es_invalido():
    with pytest.raises(ValueError):
        NumeroBoleto(valor=0)


def test_numero_boleto_negativo_es_invalido():
    with pytest.raises(ValueError):
        NumeroBoleto(valor=-1)


def test_dos_numeros_iguales_son_el_mismo_valor():
    assert NumeroBoleto(valor=7) == NumeroBoleto(valor=7)


def test_dos_numeros_distintos_son_valores_distintos():
    assert NumeroBoleto(valor=1) != NumeroBoleto(valor=2)
