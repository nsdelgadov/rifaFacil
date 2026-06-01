from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class Rifa(BaseModel):
    model_config = ConfigDict(frozen=True)

    nombre: str
    precio_boleto: Decimal

    @field_validator("precio_boleto")
    @classmethod
    def precio_debe_ser_positivo(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0"):
            raise ValueError("El precio del boleto debe ser positivo")
        return v

    @classmethod
    def crear(cls, nombre: str, precio_boleto: Decimal) -> "Rifa":
        return cls(nombre=nombre, precio_boleto=precio_boleto)
