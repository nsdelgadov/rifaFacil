import pytest

from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono


def test_crear_participante():
    p = Participante(nombre="Ana Torres", telefono=Telefono(numero="+56912345678"))

    assert p.nombre == "Ana Torres"
    assert p.telefono.numero == "+56912345678"


def test_nombre_vacio_es_invalido():
    with pytest.raises(ValueError, match="vacío"):
        Participante(nombre="   ", telefono=Telefono(numero="+56912345678"))


def test_dos_participantes_con_mismos_datos_son_iguales():
    p1 = Participante(nombre="Ana", telefono=Telefono(numero="+56912345678"))
    p2 = Participante(nombre="Ana", telefono=Telefono(numero="+56912345678"))

    assert p1 == p2


def test_participantes_con_distinto_telefono_son_distintos():
    p1 = Participante(nombre="Ana", telefono=Telefono(numero="+56911111111"))
    p2 = Participante(nombre="Ana", telefono=Telefono(numero="+56922222222"))

    assert p1 != p2
