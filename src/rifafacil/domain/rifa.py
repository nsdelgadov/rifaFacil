from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from rifafacil.domain.boleto import Boleto
from rifafacil.domain.numero_boleto import NumeroBoleto
from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono

PRECIO_MAXIMO_BOLETO = 10_000
TOTAL_MAXIMO_RIFA = 2_500_000


class Rifa(BaseModel):
    model_config = ConfigDict(frozen=False)

    nombre: str
    precio_boleto: int
    cantidad_boletos: int
    telefono_admin: Telefono
    boletos: list[Boleto] = []

    @field_validator("precio_boleto")
    @classmethod
    def validar_precio(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El precio del boleto debe ser positivo")
        if v > PRECIO_MAXIMO_BOLETO:
            raise ValueError("El precio del boleto no puede superar $10.000")
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
    def crear(cls, nombre: str, precio_boleto: int, cantidad_boletos: int, telefono_admin: Telefono) -> "Rifa":
        boletos = [Boleto(numero=NumeroBoleto(valor=n)) for n in range(1, cantidad_boletos + 1)]
        return cls(
            nombre=nombre,
            precio_boleto=precio_boleto,
            cantidad_boletos=cantidad_boletos,
            telefono_admin=telefono_admin,
            boletos=boletos,
        )

    def obtener_boleto(self, numero: int) -> Boleto:
        for b in self.boletos:
            if b.numero.valor == numero:
                return b
        raise ValueError(f"El boleto N°{numero} no existe en esta rifa")

    def reservar_boleto(self, numero: int, participante: Participante, reservado_en: datetime | None = None) -> None:
        self.obtener_boleto(numero).reservar(participante, reservado_en)

    def reservar_boletos(self, numeros: list[int], participante: Participante, reservado_en: datetime | None = None) -> None:
        for numero in numeros:
            self.reservar_boleto(numero, participante, reservado_en)

    def confirmar_pago(self, numero: int) -> None:
        self.obtener_boleto(numero).confirmar_pago()

    def liberar_boleto(self, numero: int) -> None:
        self.obtener_boleto(numero).liberar()
