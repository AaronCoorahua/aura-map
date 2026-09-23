# AuraMap

Un "Airbnb de batallas de aura": los organizadores publican una batalla (lugar,
fecha, cupo, permiso municipal) y la gente busca batallas cerca en un mapa y se
inscribe.

Proyecto del curso **DevOps - UTEC 2026-2** (Informe Parcial).

## Estado

Esqueleto inicial: app factory de Flask con `/health`. El resto del producto se
construye commit por commit segun el roadmap de `CLAUDE.md`.

## Stack

Python 3.12, Flask (app factory `create_app`), Flask-SQLAlchemy, Gunicorn,
PostgreSQL 16.3 con psycopg 3, Jinja + Leaflet. Pruebas con pytest sobre SQLite
en memoria.

## Prerrequisitos

- git
- Python 3.12
- Docker con `docker compose` v2
- GitHub CLI (`gh`)

## Uso rapido

```bash
python -m venv .venv
source .venv/bin/activate      # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements-dev.txt
pytest -v
flask --app app:create_app run --debug
```

Mas adelante todo esto se hace con `./devops.sh` (clone, test, local, docker,
down, evidence).

## Equipo y roles

| Persona | Rol DevOps |
|---|---|
| A | Release Manager / Integracion |
| B | QA & Test Automation |
| C | Platform / Container Engineer |

## Flujo de trabajo

GitFlow: `main` (estable) y `develop` (integracion). Cada bloque del roadmap va
en su rama, se integra por Pull Request hacia `develop` con merge commit
(`--no-ff`) y mensajes en formato Conventional Commits.
