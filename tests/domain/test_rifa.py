from datetime import datetime

import pytest

from rifafacil.domain.estado_boleto import EstadoBoleto
from rifafacil.domain.participante import Participante
from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono


def _telefono_admin() -> Telefono:
    return Telefono(numero="+56900000000")


def _crear_rifa(**kwargs) -> Rifa:
    defaults = {
        "nombre": "Rifa Navidad",
        "precio_boleto": 500,
        "cantidad_boletos": 5,
        "telefono_admin": _telefono_admin(),
    }
    return Rifa.crear(**{**defaults, **kwargs})


def _participante() -> Participante:
    return Participante(nombre="Ana Torres", telefono=Telefono(numero="+56912345678"))


# ── Ciclo 1 ── Crear una rifa ──────────────────────────────────────────────

def test_crear_rifa():
    rifa = _crear_rifa()

    assert rifa.nombre == "Rifa Navidad"
    assert rifa.precio_boleto == 500
    assert rifa.cantidad_boletos == 5


# ── Ciclo 2 ── Precio debe ser positivo ───────────────────────────────────

def test_precio_negativo_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        _crear_rifa(precio_boleto=-1)


def test_precio_cero_es_invalido():
    with pytest.raises(ValueError, match="positivo"):
        _crear_rifa(precio_boleto=0)


# ── Ciclo 3 ── Límites de rifas solidarias ────────────────────────────────

def test_precio_boleto_no_puede_superar_10000():
    with pytest.raises(ValueError, match=r"10\.000"):
        _crear_rifa(precio_boleto=10_001, cantidad_boletos=1)


def test_precio_boleto_exactamente_en_el_limite_es_valido():
    rifa = _crear_rifa(precio_boleto=10_000, cantidad_boletos=1)

    assert rifa.precio_boleto == 10_000


def test_total_rifa_no_puede_superar_2_500_000():
    with pytest.raises(ValueError, match=r"2\.500\.000"):
        _crear_rifa(precio_boleto=10_000, cantidad_boletos=251)


def test_total_rifa_exactamente_en_el_limite_es_valido():
    rifa = _crear_rifa(precio_boleto=10_000, cantidad_boletos=250)

    assert rifa.precio_boleto * rifa.cantidad_boletos == 2_500_000


# ── Ciclo 5+6 ── Boletos y reservas ───────────────────────────────────────

def test_rifa_crea_todos_sus_boletos_al_crear():
    rifa = _crear_rifa(cantidad_boletos=5)

    assert len(rifa.boletos) == 5


def test_boletos_estan_numerados_desde_1():
    rifa = _crear_rifa(cantidad_boletos=3)

    assert [b.numero.valor for b in rifa.boletos] == [1, 2, 3]


def test_todos_los_boletos_inician_disponibles():
    rifa = _crear_rifa(cantidad_boletos=3)

    assert all(b.estado == EstadoBoleto.DISPONIBLE for b in rifa.boletos)


def test_reservar_boleto():
    rifa = _crear_rifa()
    rifa.reservar_boleto(numero=3, participante=_participante())

    boleto = rifa.obtener_boleto(3)
    assert boleto.estado == EstadoBoleto.RESERVADO
    assert boleto.participante.nombre == "Ana Torres"


def test_no_se_puede_reservar_boleto_ya_reservado():
    rifa = _crear_rifa()
    rifa.reservar_boleto(numero=1, participante=_participante())

    with pytest.raises(ValueError):
        rifa.reservar_boleto(numero=1, participante=_participante())


def test_confirmar_pago_de_boleto_reservado():
    rifa = _crear_rifa()
    rifa.reservar_boleto(numero=1, participante=_participante())
    rifa.confirmar_pago(numero=1)

    assert rifa.obtener_boleto(1).estado == EstadoBoleto.PAGADO


def test_liberar_boleto_reservado():
    rifa = _crear_rifa()
    rifa.reservar_boleto(numero=1, participante=_participante())
    rifa.liberar_boleto(numero=1)

    boleto = rifa.obtener_boleto(1)
    assert boleto.estado == EstadoBoleto.DISPONIBLE
    assert boleto.participante is None


def test_boleto_inexistente_lanza_error():
    rifa = _crear_rifa(cantidad_boletos=5)

    with pytest.raises(ValueError):
        rifa.reservar_boleto(numero=99, participante=_participante())


def test_reservar_boleto_guarda_fecha():
    rifa = _crear_rifa()
    ahora = datetime(2026, 6, 22, 14, 30)
    rifa.reservar_boleto(numero=1, participante=_participante(), reservado_en=ahora)

    assert rifa.obtener_boleto(1).reservado_en == ahora


# ── Ciclo 17 ── Reserva múltiple ──────────────────────────────────────────

def test_reservar_multiples_boletos():
    rifa = _crear_rifa(cantidad_boletos=5)
    rifa.reservar_boletos(numeros=[1, 3, 5], participante=_participante())

    assert rifa.obtener_boleto(1).estado == EstadoBoleto.RESERVADO
    assert rifa.obtener_boleto(3).estado == EstadoBoleto.RESERVADO
    assert rifa.obtener_boleto(5).estado == EstadoBoleto.RESERVADO
    assert rifa.obtener_boleto(2).estado == EstadoBoleto.DISPONIBLE


def test_reservar_multiples_boletos_falla_si_uno_no_disponible():
    rifa = _crear_rifa(cantidad_boletos=5)
    rifa.reservar_boleto(numero=2, participante=_participante())

    with pytest.raises(ValueError):
        rifa.reservar_boletos(numeros=[1, 2, 3], participante=_participante())
