import pytest

from rifafacil.domain.estado_boleto import EstadoBoleto
from rifafacil.domain.participante import Participante
from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono
from rifafacil.infrastructure.sqlite_rifa_repository import SqliteRifaRepository


def _rifa_base() -> Rifa:
    return Rifa.crear(
        nombre="Rifa Test",
        precio_boleto=5_000,
        cantidad_boletos=5,
        telefono_admin=Telefono(numero="+56912345678"),
    )


def test_obtener_retorna_none_si_no_hay_rifa(tmp_path):
    repo = SqliteRifaRepository(str(tmp_path / "test.db"))
    assert repo.obtener() is None


def test_rifa_persiste_entre_instancias(tmp_path):
    db_path = str(tmp_path / "rifa.db")
    participante = Participante(nombre="Ana", telefono=Telefono(numero="+56987654321"))

    rifa = _rifa_base()
    rifa.reservar_boleto(1, participante)
    SqliteRifaRepository(db_path).guardar(rifa)

    rifa_recuperada = SqliteRifaRepository(db_path).obtener()

    assert rifa_recuperada is not None
    assert rifa_recuperada.nombre == "Rifa Test"
    boleto_1 = rifa_recuperada.obtener_boleto(1)
    assert boleto_1.estado == EstadoBoleto.RESERVADO
    assert boleto_1.participante.nombre == "Ana"


def test_guardar_sobreescribe_estado_previo(tmp_path):
    db_path = str(tmp_path / "rifa.db")
    participante = Participante(nombre="Luis", telefono=Telefono(numero="+56911111111"))

    rifa = _rifa_base()
    repo = SqliteRifaRepository(db_path)
    repo.guardar(rifa)

    rifa.reservar_boleto(2, participante)
    repo.guardar(rifa)

    recuperada = SqliteRifaRepository(db_path).obtener()
    assert recuperada.obtener_boleto(2).participante.nombre == "Luis"
