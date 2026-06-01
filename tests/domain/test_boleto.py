import pytest

from rifafacil.domain.boleto import Boleto
from rifafacil.domain.estado_boleto import EstadoBoleto
from rifafacil.domain.numero_boleto import NumeroBoleto
from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono


def _participante() -> Participante:
    return Participante(nombre="Ana Torres", telefono=Telefono(numero="+56912345678"))


def _boleto() -> Boleto:
    return Boleto(numero=NumeroBoleto(valor=1))


# ── Estado inicial ─────────────────────────────────────────────────────────

def test_boleto_nuevo_esta_disponible():
    assert _boleto().estado == EstadoBoleto.DISPONIBLE


def test_boleto_nuevo_no_tiene_participante():
    assert _boleto().participante is None


# ── Reservar ───────────────────────────────────────────────────────────────

def test_reservar_boleto_disponible():
    b = _boleto()
    b.reservar(_participante())

    assert b.estado == EstadoBoleto.RESERVADO
    assert b.participante.nombre == "Ana Torres"


def test_no_se_puede_reservar_boleto_ya_reservado():
    b = _boleto()
    b.reservar(_participante())

    with pytest.raises(ValueError, match="reservarse"):
        b.reservar(_participante())


def test_no_se_puede_reservar_boleto_pagado():
    b = _boleto()
    b.reservar(_participante())
    b.confirmar_pago()

    with pytest.raises(ValueError, match="reservarse"):
        b.reservar(_participante())


# ── Confirmar pago ─────────────────────────────────────────────────────────

def test_confirmar_pago_de_boleto_reservado():
    b = _boleto()
    b.reservar(_participante())
    b.confirmar_pago()

    assert b.estado == EstadoBoleto.PAGADO


def test_no_se_puede_confirmar_boleto_disponible():
    with pytest.raises(ValueError, match="confirmarse"):
        _boleto().confirmar_pago()


# ── Liberar ────────────────────────────────────────────────────────────────

def test_liberar_boleto_reservado_lo_deja_disponible():
    b = _boleto()
    b.reservar(_participante())
    b.liberar()

    assert b.estado == EstadoBoleto.DISPONIBLE
    assert b.participante is None


def test_boleto_pagado_no_puede_liberarse():
    b = _boleto()
    b.reservar(_participante())
    b.confirmar_pago()

    with pytest.raises(ValueError, match="liberarse"):
        b.liberar()
