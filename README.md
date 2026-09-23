# AuraMap

Un "Airbnb de batallas de aura": los organizadores publican una batalla (lugar,
fecha, cupo, permiso municipal) y la gente busca batallas cerca en un mapa y se
inscribe. Sin login, sin pagos.

Proyecto del curso **DevOps - UTEC 2026-2** (Informe Parcial). El informe
completo está en [`docs/INFORME.md`](docs/INFORME.md).

## Stack

Python 3.12, Flask (app factory `create_app`), Flask-SQLAlchemy, Gunicorn,
PostgreSQL 16.3 con psycopg 3, Jinja + Leaflet (mapa por CDN, sin frameworks
JS). Pruebas con pytest + pytest-cov sobre SQLite en memoria.

## Prerrequisitos

- `git`
- Python 3.12
- Docker con `docker compose` v2
- GitHub CLI (`gh`), si vas a crear o revisar Pull Requests

## Uso rápido con `./devops.sh`

`devops.sh` automatiza clonar, probar y correr el proyecto (local o con
Docker). Funciona en Linux, macOS y Git Bash/WSL en Windows.

```bash
./devops.sh -h        # ayuda y lista de comandos
```

| Comando | Qué hace |
|---|---|
| `./devops.sh clone <url> [dir]` | Clona el repo, crea el venv e instala `requirements-dev.txt`. |
| `./devops.sh test` | Crea el venv si falta y corre las pruebas. |
| `./devops.sh local` | Levanta la app sin Docker, con SQLite en `instance/`, y carga datos de ejemplo. |
| `./devops.sh docker` | Genera `secrets/pg_password.txt` y `.env.dev` si faltan, y levanta `flask` + `postgres` con `docker compose`. |
| `./devops.sh down [-v]` | Baja los servicios (`-v` borra además el volumen de datos). |
| `./devops.sh evidence` | Guarda en `docs/evidencias/` la salida de git log, pytest, `docker compose ps`, `/health` y la verificación de la red privada. |

### Pruebas

```bash
./devops.sh test
# equivalente:
pytest -v --cov=app --cov-report=term-missing
```

### Modo local (sin Docker, SQLite)

```bash
./devops.sh local
# abre http://localhost:5000
```

### Modo Docker (Flask + Postgres)

```bash
./devops.sh docker
# abre http://localhost:8080
```

Esto construye la imagen, genera una contraseña aleatoria para Postgres (la
misma en `secrets/pg_password.txt` y en `.env.dev`, ninguno de los dos se
versiona), espera a que Postgres esté `healthy` y verifica `/health`.

Para bajar los servicios:

```bash
./devops.sh down       # conserva los datos
./devops.sh down -v    # borra también el volumen postgres-data
```

## API

| Método y ruta | Descripción |
|---|---|
| `GET /health` | Estado de la app y versión. |
| `GET /api/battles?lat=&lng=&radius_km=&district=` | Lista batallas, con filtro opcional por cercanía o distrito. |
| `POST /api/battles` | Publica una batalla nueva. |
| `GET /api/battles/<id>` | Detalle de una batalla. |
| `POST /api/battles/<id>/rsvp` | Inscribe un participante (con control de cupo y sin duplicados). |
| `GET /` | Vista web con el mapa (Leaflet + OpenStreetMap) y el formulario para publicar. |

## Equipo y roles

| Persona | Rol DevOps | Responsabilidad principal |
|---|---|---|
| A | Release Manager / Integración | GitFlow, protección de ramas, Conventional Commits, revisión de PRs, release y tag. |
| B | QA & Test Automation | Estrategia de pruebas, pytest y cobertura, pipeline de CI. |
| C | Platform / Container Engineer | Dockerfile, `compose.yaml` (redes, secretos, volumen, healthcheck) y `devops.sh`. |

Los tres desarrollan features de producto; el rol define de qué responde cada
uno y qué revisa con más rigor.

## Flujo de trabajo

GitFlow: `main` (estable) y `develop` (integración). Cada bloque del roadmap
va en su propia rama, se integra por Pull Request hacia `develop` (o `main`
en el release) con merge commit (`--no-ff`, sin squash ni rebase) y mensajes
en formato [Conventional Commits](https://www.conventionalcommits.org/). El
detalle completo del roadmap y de cómo operar el repo está en `CLAUDE.md`.
