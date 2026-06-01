import pytest

from rifafacil.domain.telefono import Telefono


def test_telefono_movil_chileno_valido():
    t = Telefono(numero="+56912345678")
    assert t.numero == "+56912345678"


def test_telefono_sin_codigo_pais_es_invalido():
    with pytest.raises(ValueError, match="chileno"):
        Telefono(numero="912345678")


def test_telefono_fijo_no_es_valido():
    with pytest.raises(ValueError, match="chileno"):
        Telefono(numero="+5621234567")


def test_dos_telefonos_iguales_son_el_mismo_valor():
    assert Telefono(numero="+56912345678") == Telefono(numero="+56912345678")


def test_enlace_whatsapp_sin_mensaje():
    t = Telefono(numero="+56912345678")
    assert t.enlace_whatsapp() == "https://wa.me/56912345678"


def test_enlace_whatsapp_con_mensaje():
    t = Telefono(numero="+56912345678")
    assert t.enlace_whatsapp("Hola admin") == "https://wa.me/56912345678?text=Hola%20admin"
