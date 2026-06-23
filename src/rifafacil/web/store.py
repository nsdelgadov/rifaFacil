import os

from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono
from rifafacil.infrastructure.sqlite_rifa_repository import SqliteRifaRepository

_repo = SqliteRifaRepository(os.getenv("RIFA_DB_PATH", "rifa.db"))


def obtener_rifa() -> Rifa:
    rifa = _repo.obtener()
    if rifa is None:
        rifa = Rifa.crear(
            nombre=os.getenv("RIFA_NOMBRE", "Rifa Solidaria"),
            precio_boleto=int(os.getenv("RIFA_PRECIO_BOLETO", "5000")),
            cantidad_boletos=int(os.getenv("RIFA_CANTIDAD_BOLETOS", "50")),
            telefono_admin=Telefono(numero=os.getenv("RIFA_TELEFONO_ADMIN", "+56912345678")),
        )
        _repo.guardar(rifa)
    return rifa


def guardar_rifa(rifa: Rifa) -> None:
    _repo.guardar(rifa)


def obtener_refresh_segundos() -> int:
    default = os.getenv("GRILLA_REFRESH_SEGUNDOS", "60")
    return int(_repo.get_config("refresh_segundos", default))


def guardar_refresh_segundos(segundos: int) -> None:
    _repo.set_config("refresh_segundos", str(segundos))
