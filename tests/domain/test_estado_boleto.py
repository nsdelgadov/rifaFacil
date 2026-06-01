from rifafacil.domain.estado_boleto import EstadoBoleto


def test_boleto_disponible_solo_puede_reservarse():
    assert EstadoBoleto.RESERVADO in EstadoBoleto.DISPONIBLE.transiciones_validas()
    assert EstadoBoleto.PAGADO not in EstadoBoleto.DISPONIBLE.transiciones_validas()


def test_boleto_reservado_puede_confirmarse_o_liberarse():
    assert EstadoBoleto.PAGADO in EstadoBoleto.RESERVADO.transiciones_validas()
    assert EstadoBoleto.DISPONIBLE in EstadoBoleto.RESERVADO.transiciones_validas()


def test_boleto_pagado_no_puede_cambiar_de_estado():
    assert len(EstadoBoleto.PAGADO.transiciones_validas()) == 0
