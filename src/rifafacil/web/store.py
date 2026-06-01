import os

from rifafacil.domain.rifa import Rifa
from rifafacil.domain.telefono import Telefono

_rifa: Rifa | None = None


def obtener_rifa() -> Rifa:
    global _rifa
    if _rifa is None:
        _rifa = Rifa.crear(
            nombre=os.getenv("RIFA_NOMBRE", "Rifa Solidaria"),
            precio_boleto=int(os.getenv("RIFA_PRECIO_BOLETO", "5000")),
            cantidad_boletos=int(os.getenv("RIFA_CANTIDAD_BOLETOS", "50")),
            telefono_admin=Telefono(numero=os.getenv("RIFA_TELEFONO_ADMIN", "+56912345678")),
        )
    return _rifa
