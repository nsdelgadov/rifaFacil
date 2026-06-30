import os
import secrets
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from rifafacil.domain.participante import Participante
from rifafacil.domain.telefono import Telefono
from rifafacil.web.store import (
    ImagenMeta,
    guardar_campaign_link,
    guardar_imagenes,
    guardar_max_boletos,
    guardar_rifa,
    guardar_refresh_segundos,
    imagen_principal,
    obtener_campaign_link,
    obtener_imagenes,
    obtener_max_boletos,
    obtener_rifa,
    obtener_refresh_segundos,
    obtener_uploads_dir,
)

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
templates.env.globals["imagen_principal"] = imagen_principal

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


# ── Rutas públicas ─────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    imagenes = obtener_imagenes()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "rifa": obtener_rifa(),
            "refresh_segundos": obtener_refresh_segundos(),
            "imagenes": imagenes,
            "campaign_link": obtener_campaign_link(),
        },
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


@app.get("/uploads/{filename}")
async def servir_imagen(filename: str):
    filepath = obtener_uploads_dir() / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(str(filepath))


# ── Admin: boletos ─────────────────────────────────────────────────────────

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
    imagenes = obtener_imagenes()
    return templates.TemplateResponse(
        request=request,
        name="admin/panel.html",
        context={
            "rifa": rifa,
            "boletos_filtrados": _filtrar_y_ordenar(rifa.boletos, "numero", "asc", ""),
            "refresh_segundos": obtener_refresh_segundos(),
            "max_boletos": obtener_max_boletos(),
            "orden": "numero",
            "dir": "asc",
            "q": "",
            "campaign_link": obtener_campaign_link(),
            "imagenes": imagenes,
        },
    )


@app.post("/admin/config/max-boletos", response_class=HTMLResponse)
async def admin_config_max_boletos(
    request: Request,
    max_boletos: int = Form(),
    _: None = Depends(_verificar_admin),
):
    max_boletos = max(1, max_boletos)
    guardar_max_boletos(max_boletos)
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/config_max_boletos.html",
        context={"max_boletos": max_boletos},
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


# ── Admin: campaña e imágenes ──────────────────────────────────────────────

def _ctx_campaign(imagenes: list[ImagenMeta], link: str) -> dict:
    return {"campaign_link": link, "imagenes": imagenes}


def _ctx_galeria(imagenes: list[ImagenMeta]) -> dict:
    return {"imagenes": imagenes}


@app.post("/admin/config/campaign", response_class=HTMLResponse)
async def admin_config_campaign(
    request: Request,
    link: str = Form(default=""),
    _: None = Depends(_verificar_admin),
):
    guardar_campaign_link(link)
    imagenes = obtener_imagenes()
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/config_campaign.html",
        context=_ctx_campaign(imagenes, link),
    )


@app.post("/admin/imagenes/subir", response_class=HTMLResponse)
async def admin_subir_imagen(
    request: Request,
    file: UploadFile = File(),
    _: None = Depends(_verificar_admin),
):
    imagenes = obtener_imagenes()
    if len(imagenes) >= 10:
        raise HTTPException(status_code=400, detail="Máximo 10 imágenes")
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx. 2 MB)")
    ext = Path(file.filename or "img.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid4().hex}{ext}"
    (obtener_uploads_dir() / filename).write_bytes(contents)
    imagenes.append(ImagenMeta(filename=filename))
    guardar_imagenes(imagenes)
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/galeria_imagenes.html",
        context=_ctx_galeria(imagenes),
    )


@app.post("/admin/imagenes/{filename}/principal", response_class=HTMLResponse)
async def admin_marcar_principal(
    request: Request,
    filename: str,
    _: None = Depends(_verificar_admin),
):
    imagenes = obtener_imagenes()
    for img in imagenes:
        img.principal = img.filename == filename
    guardar_imagenes(imagenes)
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/galeria_imagenes.html",
        context=_ctx_galeria(imagenes),
    )


@app.delete("/admin/imagenes/{filename}", response_class=HTMLResponse)
async def admin_eliminar_imagen(
    request: Request,
    filename: str,
    _: None = Depends(_verificar_admin),
):
    imagenes = [i for i in obtener_imagenes() if i.filename != filename]
    guardar_imagenes(imagenes)
    (obtener_uploads_dir() / filename).unlink(missing_ok=True)
    return templates.TemplateResponse(
        request=request,
        name="admin/partials/galeria_imagenes.html",
        context=_ctx_galeria(imagenes),
    )
