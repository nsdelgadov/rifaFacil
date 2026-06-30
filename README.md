# rifaFacil

Proyecto de aprendizaje de **Domain-Driven Design**, **TDD sin mocks** y **Red-Green-Refactor (Tidy First)** usando Python 3.12 y el dominio de rifas como ejemplo concreto.

---

## Arranque rápido

```bash
pixi install            # instala dependencias (solo la primera vez)
pixi run test           # corre los tests
pixi run dev            # levanta el servidor en http://localhost:8000
pixi run cov            # tests + cobertura
pixi run lint-imports   # verifica que las capas no se violen
```

---

## Qué estamos aprendiendo

### 1. Domain-Driven Design (DDD)

DDD propone organizar el código alrededor del **negocio**, no de la tecnología. El código debe hablar el mismo idioma que el experto del dominio.

Los bloques de construcción principales:

#### Value Object
Un valor que se define por sus atributos, **no tiene identidad propia**. Dos Value Objects con los mismos datos son idénticos. Son **inmutables**.

> Ejemplo de rifas: el precio de un boleto. `$500` es `$500`, no importa "cuál" de los `$500` es. Si cambia el precio, no se modifica — se reemplaza por uno nuevo.

En el código: cuando ves `frozen=True` en una clase, es un Value Object.

#### Entity
Un objeto que tiene **identidad propia** que persiste en el tiempo, más allá de sus atributos. Dos entidades pueden tener los mismos datos y ser distintas.

> Ejemplo de rifas: un boleto específico. El boleto N°42 es distinto al boleto N°43 aunque ambos cuesten lo mismo y pertenezcan a la misma rifa.

#### Aggregate
Un **grupo de Entities y Value Objects** que forman una unidad coherente. Tiene una raíz (Aggregate Root) que es el único punto de entrada para modificar el grupo. Garantiza que las reglas de negocio se cumplan siempre.

> Ejemplo de rifas: `Rifa` es el Aggregate Root. Para agregar un boleto, siempre pasás por `Rifa` — nunca creás un `Boleto` suelto sin una `Rifa`.

#### Domain Event
Algo importante que **ocurrió** en el dominio, expresado en tiempo pasado.

> Ejemplo: `BoletosEmitidos`, `SorteoRealizado`, `GanadorDeclarado`.

#### Repository
Abstracción que oculta cómo se guardan y recuperan los Aggregates. El dominio no sabe si los datos viven en una base de datos, un archivo Excel o en memoria.

---

### 2. Testing sin mocks (James Shore)

El problema con los mocks es que reemplazan la implementación real con una falsa que puede comportarse diferente. Si el mock está mal configurado, el test pasa pero el sistema falla en producción.

La alternativa: **Nullables**. El mismo código de producción tiene una versión "nula" (liviana, en memoria) que se activa en tests. No hay sustituto externo — es la misma clase, con otro modo de operar.

```
# Con mocks (evitamos esto):
repo = Mock()
repo.guardar.return_value = None   ← frágil, desacoplado de la realidad

# Con Nullable (lo que hacemos):
repo = RifaRepository.crear_null()  ← misma clase, modo en-memoria
```

---

### 3. Red-Green-Refactor

Cada nueva funcionalidad sigue este ciclo:

```
🔴 RED    → Escribir el test que falla (la funcionalidad no existe aún)
🟢 GREEN  → Escribir el mínimo código para que pase (sin sobre-ingeniería)
🔵 TIDY   → Ordenar el código sin cambiar comportamiento (Kent Beck: "Tidy First")
```

El **Tidy First** de Kent Beck propone separar los commits de "orden" de los de "comportamiento". Primero tidyings pequeños y seguros (renombrar, extraer, mover), luego el cambio de comportamiento. Nunca mezclar los dos en el mismo commit.

---

## Estructura del proyecto

```
rifaFacil/
├── src/rifafacil/
│   ├── domain/          ← Aggregates, Entities, Value Objects
│   │                       NO depende de nada externo
│   ├── application/     ← Casos de uso (orquesta el dominio)
│   ├── infrastructure/  ← Repositorios, SQLite, Excel, etc.
│   └── web/             ← FastAPI + Jinja2 + HTMX
│
└── tests/
    └── domain/          ← Tests de dominio (sin base de datos, sin mocks)
```

`import-linter` verifica automáticamente en cada `pixi run lint-imports` que estas capas no se violen: el dominio no puede importar de application ni de infrastructure.

---

## Ciclos completados

### Ciclos 1–2 — Crear Rifa con validaciones ✅
**Conceptos**: Aggregate Root, factory method, invariantes de dominio.

### Ciclos 3 (fix) — Modelo monetario chileno ✅
**Concepto**: El modelo refleja la realidad del negocio — pesos sin decimales, límites de rifa solidaria ($10.000 por boleto, $2.500.000 total).

### Ciclo 4 — Value Objects ✅
**Conceptos**: `EstadoBoleto` (máquina de estados), `NumeroBoleto`, `Telefono` (validación chilena + enlace WhatsApp).

### Ciclos 5+6 — Boleto, Participante y reservas ✅
**Conceptos**: Entity (`Boleto` con ciclo de vida), Value Object (`Participante` identificado por teléfono), Aggregate protegiendo las transiciones de estado.

### Ciclo 7 — Capa web ✅
**Conceptos**: FastAPI (rutas), Jinja2 (templates), HTMX (actualizaciones sin JavaScript).  
La grilla se actualiza sola cada 3 segundos. Al reservar, se genera el enlace WhatsApp al administrador.

### Ciclo 8 — Repository con SQLite ✅
**Concepto**: Repository Pattern — el dominio no sabe dónde viven los datos. `SqliteRifaRepository` serializa la `Rifa` completa con Pydantic; la app sobrevive reinicios.

### Ciclo 9 — Panel de administrador ✅
**Conceptos**: HTTP Basic Auth con `secrets.compare_digest` (protección contra timing attacks). Credenciales via variables de entorno, nunca hardcodeadas.  
El admin confirma pagos y libera reservas desde `/admin`. HTMX actualiza solo la fila afectada.

### Ciclo 10 — Deploy en Render ✅
**Concepto**: separación entre dependencias de desarrollo (pixi) y de producción (`pyproject.toml`). Variables sensibles se configuran en el dashboard de Render, no en el repo.

### Ciclo 11 — Mutation testing ✅

**Concepto**: Verificar que los tests realmente detectan errores — mutmut modifica el código automáticamente y comprueba que los tests fallen. Corre en GitHub Actions (no en Windows nativo). El log de CI muestra el diff de cada mutante que sobrevive.

### Ciclo 12 — UX/UI de la grilla pública ✅

**Conceptos**: Grid con doble ancho de celda (3/4/5 columnas). Nombre del participante visible con ellipsis. Click/tap en boleto usado muestra tooltip flotante. Accesibilidad: reservados en azul, pagados con tachado. Header sticky al hacer scroll. Intervalo de refresco baja de 3 s a 60 s; el admin puede cambiarlo en vivo desde el panel (mín. 5 s, -1 = nunca) vía env var `GRILLA_REFRESH_SEGUNDOS`.

> **Nota**: el plan gratuito de Render tiene sistema de archivos efímero — `rifa.db` se pierde al reiniciar. Migrado a AWS EC2 + EBS en ciclo 13.

### Ciclo 13 — Deploy en AWS EC2 + EBS ✅

**Concepto**: infraestructura como código. EC2 t3.micro con volumen EBS montado en `/data/rifafacil/` — SQLite persiste entre reinicios. `setup_server.sh` reproduce el servidor desde cero. GitHub Actions despliega automáticamente en cada push a `main` via SSH. Variables sensibles viven en `/etc/rifafacil.env` directo en el servidor, nunca en el repo.

### Ciclos 14+15 — HTTPS y UX del panel de administrador ✅

**Ciclo 14**: dominio propio con Namecheap apuntando a la IP de EC2 + certificado real via certbot + nginx como reverse proxy. Versión de la app inyectada como `APP_VERSION` en el deploy.

**Ciclo 15**: seis mejoras al panel `/admin`:
- Auto-refresh de la tabla al mismo ritmo que la grilla pública (nuevo endpoint `GET /admin/tabla`)
- Botones "Confirmar pago" y "Liberar" muestran "Cargando…" y se deshabilitan mutuamente durante el request
- Columna con fecha y hora de reserva para decidir si liberar boletos viejos
- Intervalo de refresh persiste en SQLite — sobrevive reinicios del servidor
- Orden por Estado (reservado → pagado) o por fecha de reserva (asc/desc)
- Buscador por nombre de participante o número de boleto (`003`)

### Ciclo 16 — Confianza y transparencia ✅

**Concepto**: información que genera confianza en el comprador antes de reservar.
- Link a campaña externa (Instagram, Facebook, etc.) visible debajo del título
- Galería de imágenes de la causa con carrusel (hasta 10 imágenes, máx. 2 MB c/u)
- Imagen principal como thumbnail sticky junto al título; click abre el carrusel a 90vw/90vh
- Todo gestionado desde `/admin`: subir/eliminar imágenes, marcar principal, guardar link
- Estados de carga en todos los botones del admin (Guardar, subir imagen, marcar principal)

### Ciclo 17 — Selección múltiple de boletos ✅

**Concepto**: flujo optimizado para compradores que quieren aportar más de un boleto.

**Grilla pública**:
- Click en boleto disponible lo selecciona (amarillo). Click de nuevo lo deselecciona
- Barra flotante en la parte inferior muestra cuántos están seleccionados + botones Limpiar / Reservar →
- La selección persiste entre refrescos automáticos del HTMX (`window._rfSel`)
- Máximo de boletos por reserva configurable desde el admin (default 20, persiste en SQLite)

**Formulario y confirmación**:
- Un solo formulario para todos los boletos seleccionados
- Botón "Reservar" muestra "Cargando…" y se deshabilita durante el POST
- Mensaje WhatsApp incluye todos los números y el total a transferir
- Al cerrar la confirmación, la selección se limpia automáticamente

**Panel admin**:
- Checkboxes en filas RESERVADO con "seleccionar todos" (estado `indeterminate` en selección parcial)
- Barra sticky encima de la tabla para confirmar o liberar boletos en lote
- La selección sobrevive al auto-refresh; se limpia solo tras una acción en lote
- Tabla responsive en mobile: 2 filas por boleto (principal + detalle con teléfono, fecha y botones)
- Estado nunca truncado ("Reservado" / "Pagado" completos). Nombres largos con ellipsis y tooltip al tocar

---

## Dos rifas en paralelo (configuración, sin código nuevo)

El código ya soporta correr múltiples rifas en el mismo servidor EC2 usando `RIFA_DB_PATH`. No se necesita cambiar nada — solo configuración de nginx y systemd.

### Arquitectura

```
rifa1.tudominio.cl ─┐
                    ├─ nginx ─┬─ localhost:8001  (RIFA_DB_PATH=/data/rifafacil/rifa1.db)
rifa2.tudominio.cl ─┘         └─ localhost:8002  (RIFA_DB_PATH=/data/rifafacil/rifa2.db)
```

### 1. Dos servicios systemd

Copiar `/etc/systemd/system/rifafacil.service` como `rifafacil-rifa1.service` y `rifafacil-rifa2.service`. La única diferencia entre ambos es el puerto y la base de datos:

```ini
# rifafacil-rifa1.service
[Service]
EnvironmentFile=/etc/rifafacil-rifa1.env
ExecStart=/ruta/al/venv/bin/uvicorn rifafacil.web.app:app --host 127.0.0.1 --port 8001

# rifafacil-rifa2.service
[Service]
EnvironmentFile=/etc/rifafacil-rifa2.env
ExecStart=/ruta/al/venv/bin/uvicorn rifafacil.web.app:app --host 127.0.0.1 --port 8002
```

Cada archivo `.env` tiene sus propias variables (`RIFA_NOMBRE`, `RIFA_PRECIO_BOLETO`, `RIFA_DB_PATH`, `ADMIN_PASSWORD`, etc.).

```bash
sudo systemctl enable --now rifafacil-rifa1 rifafacil-rifa2
```

### 2. Dos bloques nginx

```nginx
server {
    server_name rifa1.tudominio.cl;
    location / { proxy_pass http://127.0.0.1:8001; }
}

server {
    server_name rifa2.tudominio.cl;
    location / { proxy_pass http://127.0.0.1:8002; }
}
```

### 3. Certificados

```bash
sudo certbot --nginx -d rifa1.tudominio.cl -d rifa2.tudominio.cl
```

Certbot configura HTTPS para ambos subdominios en una sola pasada.

### 4. DNS en Namecheap

Agregar dos registros A apuntando ambos subdominios a la misma IP del EC2:

| Host | Type | Value |
|------|------|-------|
| `rifa1` | A | `<IP del EC2>` |
| `rifa2` | A | `<IP del EC2>` |

---

## Próximos ciclos

| Ciclo | Qué construimos | Concepto / Motivo |
|-------|----------------|-------------------|
| **18** | Seguridad | Auditoría y endurecimiento antes de exponer la app a más usuarios |
| **19** | Datos de la rifa y fecha de sorteo | Agregar fecha de sorteo visible al público. Si no se venden todos los boletos antes de la fecha, el admin puede postergar con una nueva fecha y un mensaje público explicando el motivo — transparencia ante los compradores |
| **20** | Cierre de rifa y ganadores | El admin declara el sorteo realizado eligiendo los boletos ganadores. La página pública muestra el estado final: ganadores con nombre y número de boleto ganador, sin teléfonos. La rifa queda en modo cerrado (no se aceptan nuevas reservas) pero sigue siendo visible |
| **21** | Múltiples rifas — admin por rifa | Cada rifa tiene su propio administrador con credenciales independientes |
| **22** | Migración a PostgreSQL + JSONB | Reemplazar SQLite por PostgreSQL en AWS RDS — misma flexibilidad de esquema mientras el dominio evoluciona, sin cambiar el dominio (solo la capa de infraestructura) |
