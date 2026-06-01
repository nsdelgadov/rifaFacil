from pydantic import BaseModel, ConfigDict, field_validator


class Rifa(BaseModel):
    model_config = ConfigDict(frozen=True)

    nombre: str
    precio_boleto: int

    @field_validator("precio_boleto")
    @classmethod
    def precio_debe_ser_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El precio del boleto debe ser positivo")
        return v

    @classmethod
    def crear(cls, nombre: str, precio_boleto: int) -> "Rifa":
        return cls(nombre=nombre, precio_boleto=precio_boleto)
