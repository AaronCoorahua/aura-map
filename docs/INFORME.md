# Informe Parcial — AuraMap

Curso DevOps, UTEC 2026-2. Repositorio: <https://github.com/AaronCoorahua/aura-map>

> Borrador vivo: se actualiza a medida que avanza el roadmap de `CLAUDE.md`.
> Los bloques `[CAPTURA: ...]` marcan dónde va cada captura de pantalla.

## a) Título y descripción del proyecto y del equipo

**Nombre del producto:** AuraMap (nombre provisional) — un "Airbnb de
batallas de aura".

**Problema y solución:** organizar una batalla de aura hoy se coordina a
mano (grupos de chat, volantes, boca a boca), sin un lugar central donde ver
qué batallas hay cerca, cuánto cupo queda o si tienen permiso municipal.
AuraMap resuelve esto con una app web mínima (sin login, sin pagos) donde:

- un organizador publica una batalla con lugar, fecha, cupo y si tiene
  permiso municipal;
- cualquiera busca batallas cercanas en un mapa (Leaflet + OpenStreetMap),
  filtra por distrito o por radio en kilómetros, y se inscribe con control de
  cupo y sin duplicarse.

**Integrantes y roles:**

| Persona | Rol DevOps | Responsabilidad principal |
|---|---|---|
| A | Release Manager / Integración | GitFlow, protección de ramas, Conventional Commits, revisión de PRs, release y tag. |
| B | QA & Test Automation | Estrategia de pruebas, pytest y cobertura, pipeline de CI. |
| C | Platform / Container Engineer | Dockerfile, `compose.yaml` (redes, secretos, volumen, healthcheck) y `devops.sh`. |

Los tres desarrollan features de producto además de su rol; el rol define de
qué responde cada uno y qué revisa con más rigor en los Pull Requests.

`[CAPTURA: foto o mockup del equipo / repositorio en GitHub con los 3 colaboradores]`

## b) Justificación de la elección del tema

**Contexto:** el curso pide construir un proyecto real siguiendo un flujo
DevOps completo (Git con convenciones, pruebas automatizadas, CI y
containerización) en equipos de 3, con roles diferenciados. AuraMap se eligió
por ser un dominio simple de modelar (batalla, ubicación, inscripción) que
permite cubrir todo ese flujo sin alcance innecesario: no requiere login,
pagos ni integraciones externas más allá de un mapa por CDN.

**Motivación y relevancia:** las batallas de aura (freestyle/baile/arte
urbano) son un fenómeno cultural con comunidades activas pero fragmentadas
por falta de un canal común de descubrimiento. Un mapa con búsqueda por
cercanía y control de cupo es una necesidad concreta y acotada, ideal para
practicar de punta a punta: modelo de datos, API, pruebas unitarias,
Dockerfile multi-stage, `docker compose` con redes/secretos/healthcheck, CI
en cada PR y automatización con un script bash propio (`devops.sh`).

## c) Aplicación de Git con Conventional Commits

**Qué son y por qué se usan:** [Conventional Commits](https://www.conventionalcommits.org/)
es una convención para escribir mensajes de commit con el formato
`tipo(alcance opcional): descripción en modo imperativo`. Se usa porque hace
el historial legible y homogéneo entre los 3 integrantes, permite saber de un
vistazo qué cambió y por qué (una feature, un fix, un cambio de
infraestructura...) sin abrir el diff, y es la base para automatizar
changelogs o versionado semántico si el proyecto creciera.

**Tipos principales usados en AuraMap:**

| Tipo | Cuándo se usa | Ejemplo en este repo |
|---|---|---|
| `feat` | Funcionalidad nueva de producto | `feat(battles): publicar y listar batallas de aura` |
| `fix` | Corrección de un bug | `fix(db): recuperar conexiones tras reinicio de Postgres` |
| `docs` | Cambios de documentación | `docs: documentar prerrequisitos, uso de devops.sh y borrador del informe` |
| `test` | Pruebas nuevas o modificadas | `test(battles): pruebas de validación y endpoints de batallas` |
| `chore` | Tareas de mantenimiento/infra que no son feat ni fix | `chore(docker): Dockerfile multi-stage con Gunicorn y usuario no root` |
| `ci` | Cambios en integración continua | `ci: ejecutar pruebas y build de imagen en cada pull request` |
| `refactor` | Reestructurar código sin cambiar comportamiento | `refactor(battles): separar consultas a la DB de la lógica de dominio` |

Regla del equipo (documentada en `CLAUDE.md`): un commit por ID del roadmap,
mensaje exacto acordado de antemano, sin mezclar dos cambios en un commit ni
partir uno en varios.

`[CAPTURA: git log --oneline --graph --all, o "Insights > Network" en GitHub]`

### Análisis de 6 commits (de un historial con más de 9)

**1. `35c1546` — `feat(battles): publicar y listar batallas de aura`**
Introduce el modelo `Battle`, la validación de negocio en
`app/services/battles.py` (título obligatorio, fecha futura, cupo entre 1 y
100, lat/lng en rango) y los endpoints `POST /api/battles` y
`GET /api/battles`. 4 archivos, 140 líneas agregadas. Es la primera feature
de producto real del proyecto: define el modelo de datos que usan todos los
commits siguientes (geo, rsvp, refactor de repositorios).

**2. `ab71d8e` — `test(battles): pruebas de validación y endpoints de batallas`**
Agrega 6 pruebas unitarias sobre lo anterior: payload válido, título vacío,
fecha pasada, cupo inválido, `POST` devuelve 201, `GET` lista. Un solo
archivo (`tests/test_battles.py`), 59 líneas. Ejemplo de la disciplina del
roadmap: cada feature va acompañada de su commit de pruebas por separado,
nunca mezclados.

**3. `360634d` — `refactor(battles): separar consultas a la DB de la lógica de dominio`**
Mueve las consultas SQLAlchemy de `app/routes.py` a
`app/repositories/battles.py`, dejando las rutas delgadas (solo orquestan
validación + repositorio + respuesta HTTP). 3 archivos, 34 líneas agregadas,
12 eliminadas. Es un refactor puro: ninguna prueba existente se modificó, lo
que confirma que el comportamiento externo no cambió.

**4. `4bc9f73` — `chore(compose): orquestar flask y postgres con redes, secretos, volumen y healthcheck`**
Agrega `compose.yaml` y `.env.dev.example`. Configura dos redes (`public` y
`private`, esta última `internal: true` para que Postgres no sea alcanzable
desde fuera), un secreto Docker (`pg_password`) en vez de una variable de
entorno en texto plano, un volumen (`postgres-data`) y un healthcheck con
`pg_isready` del que depende el servicio `flask` (`condition:
service_healthy`). 2 archivos, 56 líneas. Es el commit que hace reproducible
el entorno completo con un solo comando.

**5. `66809f5` — `ci: ejecutar pruebas y build de imagen en cada pull request`**
Agrega `.github/workflows/tests.yml`: en cada Pull Request hacia `develop` o
`main`, instala Python 3.12, corre `./devops.sh test` (con fallback a
`pytest` directo si el script no está) y hace `docker build` de la imagen.
1 archivo, 34 líneas. Cierra el ciclo: ya no depende de que cada persona
recuerde correr las pruebas antes de pedir revisión.

**6. `123289b` — `fix(db): recuperar conexiones tras reinicio de Postgres`**
Corrige un bug reproducido deliberadamente: con los servicios arriba,
`docker compose restart postgres` seguido de peticiones a `/api/battles`
producía `OperationalError: server closed the connection unexpectedly` en
~10% de los intentos, porque SQLAlchemy reutilizaba conexiones del pool que
Postgres ya había cerrado. El fix agrega `pool_pre_ping: True` (SQLAlchemy
verifica la conexión antes de reutilizarla) y una espera con reintentos y
backoff exponencial al arrancar la app (`app/db.py::wait_for_db`), porque
`depends_on: condition: service_healthy` solo ordena el arranque de los
contenedores y no protege si Postgres cae después. 5 archivos, incluyendo la
evidencia de antes/después en `docs/evidencias/`. Ejemplo de un fix con
reproducción documentada antes de escribir la corrección.

`[CAPTURA: para cada uno de los 6 commits, git show <hash> --stat o la vista de "Files changed" del PR correspondiente]`

**Pull Requests según la metodología de branching:** el equipo usa GitFlow —
rama `develop` como integración, `main` como estable, y una rama por bloque
del roadmap (`feature/...`, `fix/...`, `chore/...`, `docs/...`,
`release/...`) que se integra a `develop` (o a `main` en el release) por
Pull Request con merge commit (`--no-ff`, sin squash ni rebase), siempre con
al menos un revisor asignado según la tabla de roles del roadmap.

`[CAPTURA: lista de Pull Requests (gh pr list o la pestaña "Pull requests" en GitHub) mostrando rama origen, rama destino y revisor]`

## d) Pruebas unitarias

**Herramientas:** [pytest](https://docs.pytest.org/) como framework de
pruebas y [pytest-cov](https://pytest-cov.readthedocs.io/) para el reporte de
cobertura. Las pruebas usan el test client de Flask y una base de datos
SQLite en memoria (fixture `app` en `tests/conftest.py`), por lo que no
dependen de Docker ni de Postgres para correr.

**Implementación:** 15 pruebas unitarias repartidas en 4 archivos (mínimo
exigido: 9):

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `tests/test_api.py` | 2 | `/health` responde 200 e incluye la versión. |
| `tests/test_battles.py` | 6 | Validación de payload (título vacío, fecha pasada, cupo inválido) y endpoints `POST`/`GET` de batallas. |
| `tests/test_geo.py` | 4 | `haversine_km` (mismo punto = 0, 1° de longitud en el ecuador ≈ 111.19 km), filtro por radio y coordenadas inválidas. |
| `tests/test_rsvp.py` | 3 | Inscripción con cupo disponible, rechazo por cupo lleno (409) y rechazo por duplicado (409). |

**Evidencia de ejecución:**

```
./devops.sh test
# equivalente: pytest -v --cov=app --cov-report=term-missing

15 passed in 1.16s
TOTAL cobertura: 82%
```

`[CAPTURA: terminal con la salida completa de ./devops.sh test, o docs/evidencias/pytest.txt generado por ./devops.sh evidence]`

## e) Automatización en scripts bash

Todo el ciclo de desarrollo se automatiza con `devops.sh` (bash, `set -euo
pipefail`, ayuda con `-h`, compatible con Linux, macOS y Git Bash/WSL en
Windows):

- **Clonación:** `./devops.sh clone <url> [dir]` clona el repositorio, crea
  el entorno virtual e instala `requirements-dev.txt`.
- **Pruebas:** `./devops.sh test` crea el entorno virtual si falta y corre
  `pytest -v --cov=app --cov-report=term-missing`.
- **Modo local:** `./devops.sh local` levanta la app sin Docker, con SQLite
  en `instance/`, y arranca `flask --app app:create_app run --debug`.

Además, `./devops.sh docker` (genera secretos y levanta Flask + Postgres),
`./devops.sh down [-v]` (baja los servicios) y `./devops.sh evidence`
(guarda las evidencias de este informe en `docs/evidencias/`).

`[CAPTURA: terminal corriendo ./devops.sh clone, ./devops.sh test y ./devops.sh local, una tras otra]`

## f) Dockerizar su aplicación

**Dockerfile:** build multi-stage. La etapa `builder` (`python:3.12-slim`)
instala las dependencias en un entorno virtual; la etapa final, también
`python:3.12-slim`, copia solo ese entorno virtual y el código de la app,
corre como usuario sin privilegios (`aura`, no root), expone el puerto 5000 y
arranca con Gunicorn en forma exec:
`CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", ..., "app:create_app()"]`.

**Docker Compose — servicio web (Flask + Gunicorn):**

```yaml
flask:
  image: aura-map:latest
  build:
    context: .
    dockerfile: Dockerfile
  ports:
    - "8080:5000"
  env_file:
    - .env.dev
  environment:
    APP_VERSION: "0.1.0"
    DB_HOST: postgres
    DB_DATABASE: auradb
    DB_USER: aurauser
  networks:
    - public
    - private
  depends_on:
    postgres:
      condition: service_healthy
```

**Docker Compose — base de datos (Postgres):**

```yaml
postgres:
  image: postgres:16.3
  environment:
    POSTGRES_USER: aurauser
    POSTGRES_DB: auradb
    POSTGRES_PASSWORD_FILE: /run/secrets/pg_password
  secrets:
    - pg_password
  volumes:
    - postgres-data:/var/lib/postgresql/data
  networks:
    - private
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U aurauser -d auradb"]
    interval: 5s
    timeout: 5s
    retries: 5
```

Postgres no publica puertos al host (solo es alcanzable desde la red
`private`, que es `internal: true`); su contraseña se inyecta por Docker
secret (`secrets/pg_password.txt`, ignorado por git), nunca en texto plano en
`compose.yaml`.

**Evidencia de la aplicación corriendo en Docker:**

```
./devops.sh docker
...
Postgres healthy tras 1 intento(s)
{"status":"ok","version":"0.1.0"}

NAME                  IMAGE             STATUS                   PORTS
aura-map-flask-1      aura-map:latest   Up                       0.0.0.0:8080->5000/tcp
aura-map-postgres-1   postgres:16.3     Up (healthy)              5432/tcp
```

Postgres queda `Up (healthy)` sin puertos publicados al host, y `flask`
responde en `http://localhost:8080/health`.

`[CAPTURA: terminal con la salida de ./devops.sh docker y docker compose ps, y el navegador en http://localhost:8080 mostrando el mapa]`

## g) Conclusiones preliminares

- **Git con convenciones claras:** usar Conventional Commits desde el primer
  commit y un roadmap con un ID y un mensaje fijo por bloque eliminó la
  ambigüedad de "qué se supone que hace este commit" al revisar PRs entre 3
  personas trabajando en paralelo. La trazabilidad se nota en la práctica: el
  bug de `fix(db)` (commit `123289b`) se pudo documentar y revisar sin
  necesidad de explicación extra, porque el tipo y el alcance del commit ya
  dicen qué se tocó y por qué.
- **Pruebas unitarias:** correr las 15 pruebas en menos de 2 segundos, sin
  Docker ni Postgres, permitió refactorizar (`360634d`) con la garantía de
  que el comportamiento externo no cambiaba, y detectar en CI cualquier
  regresión antes de mergear. La cobertura (82%) además señala qué ramas del
  código (sobre todo manejo de errores en rutas) todavía no están probadas.
- **Dockerizar la aplicación:** reproducir el entorno completo con un solo
  comando (`./devops.sh docker`) hizo posible reproducir de forma
  determinística un bug real (conexiones caídas tras reiniciar Postgres) en
  vez de solo poder discutirlo en teoría, y las redes/secretos/healthcheck de
  `compose.yaml` obligan a modelar desde el inicio cómo se comunican los
  servicios en producción, no solo en la laptop de cada integrante.

## Anexo: evidencias

Las capturas y salidas de comandos referidas en este informe se guardan en
[`docs/evidencias/`](evidencias/), generadas con `./devops.sh evidence` o
adjuntas manualmente por cada integrante.
