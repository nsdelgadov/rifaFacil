from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono
from rifafacil.web.store import obtener_rifa

app = FastAPI(title="rifaFacil")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _pesos(valor: int) -> str:
    return f"${valor:,}".replace(",", ".")


templates.env.filters["pesos"] = _pesos


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"rifa": obtener_rifa()},
    )


@app.get("/boletos", response_class=HTMLResponse)
async def grilla_boletos(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/grilla.html",
        context={"rifa": obtener_rifa()},
    )


@app.get("/boletos/{numero}/formulario", response_class=HTMLResponse)
async def formulario_reserva(request: Request, numero: int):
    boleto = obtener_rifa().obtener_boleto(numero)
    return templates.TemplateResponse(
        request=request,
        name="partials/formulario.html",
        context={"boleto": boleto},
    )


@app.post("/boletos/{numero}/reservar", response_class=HTMLResponse)
async def reservar_boleto(
    request: Request,
    numero: int,
    nombre: str = Form(),
    telefono: str = Form(),
):
    rifa = obtener_rifa()
    try:
        participante = Participante(nombre=nombre, telefono=Telefono(numero=telefono))
        rifa.reservar_boleto(numero=numero, participante=participante)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={"mensaje": str(e)},
        )

    mensaje_admin = (
        f"Hola! Reservé el boleto N°{numero:03d} de {rifa.nombre}. "
        f"Soy {nombre}, mi teléfono es {telefono}. "
        f"Quedo atento para la transferencia de {_pesos(rifa.precio_boleto)}."
    )
    return templates.TemplateResponse(
        request=request,
        name="partials/confirmacion.html",
        context={
            "numero": numero,
            "enlace_admin": rifa.telefono_admin.enlace_whatsapp(mensaje_admin),
        },
    )
