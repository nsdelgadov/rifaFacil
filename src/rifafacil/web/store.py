import json
import os
from pathlib import Path

from pydantic import BaseModel

from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono
from rifafacil.infrastructure.sqlite_rifa_repository import SqliteRifaRepository

_repo = SqliteRifaRepository(os.getenv("RIFA_DB_PATH", "rifa.db"))


class ImagenMeta(BaseModel):
    filename: str
    principal: bool = False


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


def obtener_uploads_dir() -> Path:
    db_path = Path(_repo._db_path)
    uploads = db_path.parent / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    return uploads


def obtener_campaign_link() -> str:
    return _repo.get_config("campaign_link", "")


def guardar_campaign_link(link: str) -> None:
    _repo.set_config("campaign_link", link)


def obtener_imagenes() -> list[ImagenMeta]:
    raw = _repo.get_config("imagenes", "[]")
    return [ImagenMeta.model_validate(x) for x in json.loads(raw)]


def guardar_imagenes(imagenes: list[ImagenMeta]) -> None:
    _repo.set_config("imagenes", json.dumps([i.model_dump() for i in imagenes]))


def obtener_max_boletos() -> int:
    default = os.getenv("MAX_BOLETOS_POR_RESERVA", "20")
    return int(_repo.get_config("max_boletos_por_reserva", default))


def guardar_max_boletos(max_boletos: int) -> None:
    _repo.set_config("max_boletos_por_reserva", str(max_boletos))


def imagen_principal(imagenes: list[ImagenMeta]) -> ImagenMeta | None:
    if not imagenes:
        return None
    for img in imagenes:
        if img.principal:
            return img
    return imagenes[0]
