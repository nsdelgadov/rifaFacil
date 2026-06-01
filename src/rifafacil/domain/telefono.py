import re
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, field_validator

_PATRON_MOVIL_CHILENO = re.compile(r"^\+569\d{8}$")


class Telefono(BaseModel):
    model_config = ConfigDict(frozen=True)

    numero: str

    @field_validator("numero")
    @classmethod
    def debe_ser_movil_chileno(cls, v: str) -> str:
        if not _PATRON_MOVIL_CHILENO.match(v):
            raise ValueError("El teléfono debe ser un móvil chileno: +569XXXXXXXX")
        return v

    def enlace_whatsapp(self, mensaje: str = "") -> str:
        numero_limpio = self.numero.lstrip("+")
        if mensaje:
            return f"https://wa.me/{numero_limpio}?text={quote(mensaje)}"
        return f"https://wa.me/{numero_limpio}"
