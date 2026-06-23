from datetime import datetime

from pydantic import BaseModel, ConfigDict

from rifafacil.domain.estado_boleto import EstadoBoleto
from rifafacil.domain.numero_boleto import NumeroBoleto
from rifafacil.domain.participante import Participante


class Boleto(BaseModel):
    model_config = ConfigDict(frozen=False)

    numero: NumeroBoleto
    estado: EstadoBoleto = EstadoBoleto.DISPONIBLE
    participante: Participante | None = None
    reservado_en: datetime | None = None

    def reservar(self, participante: Participante, reservado_en: datetime | None = None) -> None:
        if EstadoBoleto.RESERVADO not in self.estado.transiciones_validas():
            raise ValueError(
                f"El boleto N°{self.numero.valor} no puede reservarse "
                f"porque está {self.estado}"
            )
        self.estado = EstadoBoleto.RESERVADO
        self.participante = participante
        self.reservado_en = reservado_en

    def confirmar_pago(self) -> None:
        if EstadoBoleto.PAGADO not in self.estado.transiciones_validas():
            raise ValueError(
                f"El boleto N°{self.numero.valor} no puede confirmarse "
                f"porque está {self.estado}"
            )
        self.estado = EstadoBoleto.PAGADO

    def liberar(self) -> None:
        if EstadoBoleto.DISPONIBLE not in self.estado.transiciones_validas():
            raise ValueError(
                f"El boleto N°{self.numero.valor} no puede liberarse "
                f"porque está {self.estado}"
            )
        self.estado = EstadoBoleto.DISPONIBLE
        self.participante = None
        self.reservado_en = None
