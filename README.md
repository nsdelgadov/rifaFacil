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

> **Nota**: el plan gratuito de Render tiene sistema de archivos efímero — `rifa.db` se pierde al reiniciar. Se migrará a AWS EC2 + EBS para persistencia real (ciclo 13).

---

## Próximos ciclos

| Ciclo | Qué construimos | Concepto / Motivo |
|-------|----------------|-------------------|
| **13** | Deploy en AWS EC2 + EBS | Migrar de Render a EC2 t3.micro con volumen EBS para que `rifa.db` sobreviva reinicios. CI/CD con GitHub Actions |
| **14** | UX del panel de administrador | Mejorar la experiencia del admin: diseño, flujos y usabilidad del panel |
| **15** | Confianza y transparencia | Link a campaña (Instagram/Facebook), imágenes de la causa, datos de cuenta bancaria para donaciones directas |
| **16** | Selección múltiple de boletos | Elegir entre 1 y 10 boletos a la vez — flujo para quienes quieren aportar más |
| **17** | Múltiples rifas — un solo admin | Soporte para más de una rifa activa en el mismo servidor, todas gestionadas por el mismo administrador |
| **18** | Múltiples rifas — admin por rifa | Cada rifa tiene su propio administrador con credenciales independientes |
| **19** | Migración a PostgreSQL + JSONB | Reemplazar SQLite por PostgreSQL en AWS RDS — misma flexibilidad de esquema mientras el dominio evoluciona, sin cambiar el dominio (solo la capa de infraestructura) |
