from enum import Enum


class EstadoBoleto(str, Enum):
    DISPONIBLE = "disponible"
    RESERVADO = "reservado"
    PAGADO = "pagado"

    def transiciones_validas(self) -> set["EstadoBoleto"]:
        if self == EstadoBoleto.DISPONIBLE:
            return {EstadoBoleto.RESERVADO}
        if self == EstadoBoleto.RESERVADO:
            return {EstadoBoleto.PAGADO, EstadoBoleto.DISPONIBLE}
        return set()
