import os
import secrets
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono
from rifafacil.web.store import guardar_rifa, guardar_refresh_segundos, obtener_rifa, obtener_refresh_segundos

_security = HTTPBasic()


def _verificar_admin(credentials: HTTPBasicCredentials = Depends(_security)) -> None:
    usuario_ok = secrets.compare_digest(
        credentials.username.encode(),
        os.getenv("ADMIN_USER", "admin").encode(),
    )
    password_ok = secrets.compare_digest(
        credentials.password.encode(),
        os.getenv("ADMIN_PASSWORD", "").encode(),
    )
    if not (usuario_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

app = FastAPI(title="rifaFacil")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _pesos(valor: int) -> str:
    return f"${valor:,}".replace(",", ".")


def _fecha(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d/%m %H:%M")


templates.env.filters["pesos"] = _pesos
templates.env.filters["fecha"] = _fecha
templates.env.globals["version"] = os.getenv("APP_VERSION", "?")

_PRIORIDAD_ESTADO = {"reservado": 0, "pagado": 1}


def _filtrar_y_ordenar(boletos: list, orden: str, dir: str, q: str) -> list:
    resultado = [b for b in boletos if b.estado != "disponible"]
    if q:
        q_norm = q.strip().lower()
        resultado = [
            b for b in resultado
            if q_norm in (b.participante.nombre.lower() if b.participante else "")
            or q.strip() in f"{b.numero.valor:03d}"
        ]
    if orden == "estado":
        resultado.sort(
            key=lambda b: _PRIORIDAD_ESTADO.get(b.estado.value, 2),
            reverse=(dir == "desc"),
        )
    elif orden == "reservado_en":
        resultado.sort(
            key=lambda b: b.reservado_en or datetime.min,
            reverse=(dir == "desc"),
        )
    return resultado


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"rifa": obtener_rifa(), "refresh_segundos": obtener_refresh_segundos()},
    )


@app.get("/boletos", response_class=HTMLResponse)
async def grilla_boletos(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/grilla.html",
        context={"rifa": obtener_rifa(), "refresh_segundos": obtener_refresh_segundos()},
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
        rifa.reservar_boleto(numero=numero, participante=participante, reservado_en=datetime.now())
        guardar_rifa(rifa)
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


@app.get("/admin/tabla", response_class=HTMLResponse)
async def admin_tabla(
    request: Request,
    orden: str = "numero",
    dir: str = "asc",
    q: str = "",
    _: None = Depends(_verificar_admin),
):
    rifa = obtener_rifa()
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/tabla_boletos.html",
        context={
            "rifa": rifa,
            "boletos_filtrados": _filtrar_y_ordenar(rifa.boletos, orden, dir, q),
            "refresh_segundos": obtener_refresh_segundos(),
            "orden": orden,
            "dir": dir,
            "q": q,
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def panel_admin(request: Request, _: None = Depends(_verificar_admin)):
    rifa = obtener_rifa()
    return templates.TemplateResponse(
        request=request,
        name="admin/panel.html",
        context={
            "rifa": rifa,
            "boletos_filtrados": _filtrar_y_ordenar(rifa.boletos, "numero", "asc", ""),
            "refresh_segundos": obtener_refresh_segundos(),
            "orden": "numero",
            "dir": "asc",
            "q": "",
        },
    )


@app.post("/admin/config/refresh", response_class=HTMLResponse)
async def admin_config_refresh(
    request: Request,
    segundos: int = Form(),
    _: None = Depends(_verificar_admin),
):
    if segundos != -1:
        segundos = max(5, segundos)
    guardar_refresh_segundos(segundos)
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/config_refresh.html",
        context={"refresh_segundos": segundos},
    )


@app.post("/admin/boletos/{numero}/confirmar", response_class=HTMLResponse)
async def admin_confirmar(request: Request, numero: int, _: None = Depends(_verificar_admin)):
    rifa = obtener_rifa()
    try:
        rifa.confirmar_pago(numero)
        guardar_rifa(rifa)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request, name="partials/error.html", context={"mensaje": str(e)}
        )
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/fila_boleto.html",
        context={"boleto": rifa.obtener_boleto(numero)},
    )


@app.post("/admin/boletos/{numero}/liberar", response_class=HTMLResponse)
async def admin_liberar(request: Request, numero: int, _: None = Depends(_verificar_admin)):
    rifa = obtener_rifa()
    try:
        rifa.liberar_boleto(numero)
        guardar_rifa(rifa)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request, name="partials/error.html", context={"mensaje": str(e)}
        )
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/fila_boleto.html",
        context={"boleto": rifa.obtener_boleto(numero)},
    )
