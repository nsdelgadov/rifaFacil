from pydantic import BaseModel, ConfigDict, field_validator


class NumeroBoleto(BaseModel):
    model_config = ConfigDict(frozen=True)

    valor: int

    @field_validator("valor")
    @classmethod
    def debe_ser_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El número de boleto debe ser mayor a cero")
        return v
