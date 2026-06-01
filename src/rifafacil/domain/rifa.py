from pydantic import BaseModel, ConfigDict, field_validator, model_validator

PRECIO_MAXIMO_BOLETO = 10_000
TOTAL_MAXIMO_RIFA = 2_500_000


class Rifa(BaseModel):
    model_config = ConfigDict(frozen=True)

    nombre: str
    precio_boleto: int
    cantidad_boletos: int

    @field_validator("precio_boleto")
    @classmethod
    def validar_precio(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El precio del boleto debe ser positivo")
        if v > PRECIO_MAXIMO_BOLETO:
            raise ValueError(f"El precio del boleto no puede superar $10.000")
        return v

    @model_validator(mode="after")
    def validar_total(self) -> "Rifa":
        total = self.precio_boleto * self.cantidad_boletos
        if total > TOTAL_MAXIMO_RIFA:
            raise ValueError(
                f"El total de la rifa no puede superar $2.500.000 "
                f"(precio ${self.precio_boleto:,} × {self.cantidad_boletos} boletos = ${total:,})"
            )
        return self

    @classmethod
    def crear(cls, nombre: str, precio_boleto: int, cantidad_boletos: int) -> "Rifa":
        return cls(nombre=nombre, precio_boleto=precio_boleto, cantidad_boletos=cantidad_boletos)
