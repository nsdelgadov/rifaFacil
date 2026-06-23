from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import rifafacil.web.store as store_module
from rifafacil.domain.participante import Participante
from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono
from rifafacil.infrastructure.sqlite_rifa_repository import SqliteRifaRepository
from rifafacil.web.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USER", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")

    repo = SqliteRifaRepository(str(tmp_path / "test.db"))
    rifa = Rifa.crear(
        nombre="Rifa Test",
        precio_boleto=5_000,
        cantidad_boletos=10,
        telefono_admin=Telefono(numero="+56912345678"),
    )
    participante = Participante(nombre="Ana", telefono=Telefono(numero="+56987654321"))
    rifa.reservar_boleto(1, participante, reservado_en=datetime(2026, 1, 15, 10, 30))
    repo.guardar(rifa)

    monkeypatch.setattr(store_module, "_repo", repo)
    return TestClient(app)


@pytest.fixture
def client_completo(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USER", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")

    repo = SqliteRifaRepository(str(tmp_path / "test.db"))
    rifa = Rifa.crear(
        nombre="Rifa Test",
        precio_boleto=5_000,
        cantidad_boletos=10,
        telefono_admin=Telefono(numero="+56912345678"),
    )
    ana = Participante(nombre="Ana", telefono=Telefono(numero="+56987654321"))
    bob = Participante(nombre="Bob", telefono=Telefono(numero="+56911111111"))
    carlos = Participante(nombre="Carlos", telefono=Telefono(numero="+56922222222"))

    rifa.reservar_boleto(1, ana, reservado_en=datetime(2026, 1, 15, 10, 30))
    rifa.reservar_boleto(2, bob, reservado_en=datetime(2026, 3, 1, 9, 0))
    rifa.reservar_boleto(3, carlos, reservado_en=datetime(2026, 2, 1, 14, 0))
    rifa.confirmar_pago(3)
    repo.guardar(rifa)

    monkeypatch.setattr(store_module, "_repo", repo)
    return TestClient(app)
