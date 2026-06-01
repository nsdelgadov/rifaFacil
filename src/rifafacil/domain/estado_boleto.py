from enum import StrEnum


class EstadoBoleto(StrEnum):
    DISPONIBLE = "disponible"
    RESERVADO = "reservado"
    PAGADO = "pagado"

    def transiciones_validas(self) -> set["EstadoBoleto"]:
        match self:
            case EstadoBoleto.DISPONIBLE:
                return {EstadoBoleto.RESERVADO}
            case EstadoBoleto.RESERVADO:
                return {EstadoBoleto.PAGADO, EstadoBoleto.DISPONIBLE}
            case EstadoBoleto.PAGADO:
                return set()
