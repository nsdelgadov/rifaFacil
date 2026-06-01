from pydantic import BaseModel, ConfigDict, field_validator

from rifafacil.domain.telefono import Telefono


class Participante(BaseModel):
    model_config = ConfigDict(frozen=True)

    nombre: str
    telefono: Telefono

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v
