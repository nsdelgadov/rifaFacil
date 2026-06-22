# rifaFacil — instrucciones para Claude

## Flujo de trabajo por ciclos

El proyecto avanza en **ciclos TDD** cortos. Cada ciclo introduce un concepto nuevo de DDD o infraestructura.

### Reglas de git (obligatorias)

- Nunca commitear directamente a `main`.
- Cada ciclo va en su propio branch: `feat/ciclo-NN-descripcion-corta`.
- Cada ciclo termina en un **PR** para revisión manual antes de mergear.
- Usar **Conventional Commits**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `build`.
- Scopes útiles: `domain`, `application`, `infrastructure`, `web`.

### Reglas de TDD

- No commitear tests en rojo. Cada commit incluye test + implementación pasando juntos.
- Si hay refactor (Tidy First), va en un commit separado: `refactor(scope): ...`.
- No mezclar cambios de comportamiento con cambios de orden en el mismo commit.

### Al iniciar un ciclo

1. Crear el branch **antes** de escribir cualquier código.
2. Acordar el objetivo del ciclo antes de implementar.
3. Seguir Red → Green → Tidy (refactor opcional en commit separado).

## Stack

- Python 3.12, Pixi, Pydantic v2, FastAPI, Jinja2, HTMX, SQLite
- pytest + mutmut (mutation testing)
- import-linter (enforcer de capas DDD)
- Deploy: AWS EC2 + EBS, nginx, certbot, GitHub Actions

## Comandos útiles

```bash
pixi run test          # correr tests
pixi run dev           # servidor local http://localhost:8000
pixi run cov           # tests + cobertura
pixi run lint-imports  # verificar capas DDD
```
