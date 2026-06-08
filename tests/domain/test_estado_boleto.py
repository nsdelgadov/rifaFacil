from rifafacil.domain.estado_boleto import EstadoBoleto


def test_boleto_disponible_solo_puede_reservarse():
    assert EstadoBoleto.DISPONIBLE.transiciones_validas() == {EstadoBoleto.RESERVADO}


def test_boleto_reservado_puede_confirmarse_o_liberarse():
    assert EstadoBoleto.RESERVADO.transiciones_validas() == {EstadoBoleto.PAGADO, EstadoBoleto.DISPONIBLE}


def test_boleto_pagado_no_puede_cambiar_de_estado():
    assert EstadoBoleto.PAGADO.transiciones_validas() == set()
