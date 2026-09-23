# CLAUDE.md — AuraMap

Eres el asistente de ingeniería de nuestro equipo para el Informe Parcial del curso DevOps (UTEC 2026-2). Vas a construir el proyecto commit por commit siguiendo un roadmap compartido entre 3 personas. Este mismo archivo lo usan los 3 integrantes; cada uno declara al inicio de la sesión qué Persona es (A, B o C).

REPO: https://github.com/AaronCoorahua/aura-map

## 0. Cómo operas en cada sesión

1. Detecta el estado real. La fuente de verdad es git, no tu memoria. Si no hay repo local, estás en modo bootstrap (solo Persona A). Si hay repo: `git fetch --all`, `git log --oneline --graph --all -40`, `gh pr list --state all`, y compáralo con el ROADMAP (sección 4) para saber qué IDs ya están en develop, cuáles están en PRs abiertos y cuál sigue.
2. Si hay un PR abierto donde yo soy el revisor asignado, revísalo antes de cualquier otra cosa: `gh pr checkout <n>`, corre las pruebas (`./devops.sh test` o `pytest -v` si el script aún no existe), verifica que cada commit cumpla Conventional Commits y reporta hallazgos concretos. No apruebes ni mergees tú; dame los comandos `gh pr review <n> --approve` y `gh pr merge <n> --merge --delete-branch` para ejecutarlos yo.
3. Si el siguiente bloque del roadmap me corresponde, ejecútalo completo: rama nueva desde develop actualizado, implementación, pruebas en verde, commits EXACTAMENTE como están definidos (un commit por ID, el mensaje indicado, sin trailers Co-Authored-By ni "Generated with"), push y PR con `gh pr create --base develop` asignando como reviewer al revisor del roadmap. Nunca juntes dos IDs en un commit ni partas uno en varios.
4. Si el siguiente bloque NO me corresponde, no escribas su código. Dime quién sigue y si tengo algo que revisar.
5. Nunca hagas commit ni push directo a main ni a develop (única excepción: C1 en bootstrap). Los PRs se integran con merge commit (--no-ff, como GitFlow), nunca squash ni rebase, para que cada commit quede en el historial.
6. Cierra SIEMPRE con la sección "Salida" (sección 6).

## 1. Producto

AuraMap (nombre provisional): un "Airbnb de batallas de aura". Los organizadores publican una batalla (lugar, fecha, cupo, si tiene permiso municipal) y la gente busca batallas cerca en un mapa y se inscribe.

MVP, sin agregar alcance extra (sin login, sin pagos):
- Publicar batalla: título, descripción, distrito, dirección, lat, lng, fecha y hora, cupo de participantes, nombre del organizador, tiene_permiso (bool).
- Buscar batallas cercanas por radio en km desde una ubicación y filtrar por distrito.
- Inscribirse a una batalla con control de cupo y sin duplicados por nombre.
- Vista web con mapa (Leaflet + OpenStreetMap por CDN) y formulario simple para publicar. Interfaz en español.
- Endpoint /health.

## 2. Stack y decisiones técnicas

- Python 3.12, Flask con app factory `create_app`, Flask-SQLAlchemy, Gunicorn, PostgreSQL 16.3 con psycopg 3, plantillas Jinja sin frameworks JS.
- Configuración por variables de entorno: DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD, APP_VERSION. Si existe DATABASE_URL tiene prioridad. Tests y modo local sin Docker usan SQLite.
- Lógica de negocio en funciones puras dentro de app/services/ (geo.py, battles.py, rsvp.py) para testear sin DB.
- Pruebas con pytest + pytest-cov en tests/, SQLite en memoria y test client de Flask. Mínimo exigido 9; el roadmap llega a 15.
- API: GET /health → {"status":"ok","version":APP_VERSION} · GET /api/battles?lat=&lng=&radius_km=&district= · POST /api/battles · GET /api/battles/<id> · POST /api/battles/<id>/rsvp · GET / (mapa).
- Comando CLI `flask seed` que carga 3 batallas de ejemplo en Lima si la DB está vacía.

Estructura final esperada:
  app/ (__init__.py, config.py, db.py, models.py, routes.py, services/, templates/, static/)
  tests/ (conftest.py, test_battles.py, test_geo.py, test_rsvp.py, test_api.py)
  docs/INFORME.md y docs/evidencias/
  secrets/.gitkeep (secrets/*.txt ignorado)
  Dockerfile, .dockerignore, compose.yaml, .env.dev.example (.env.dev ignorado)
  devops.sh en la raíz, requirements.txt, requirements-dev.txt
  .github/workflows/tests.yml, CLAUDE.md, README.md

Dockerfile (lo visto en clase):
- Multi-stage: etapa builder instala dependencias; etapa final python:3.12-slim solo con lo necesario.
- Primero COPY de requirements y pip install, luego COPY del código, para aprovechar el caché de capas. COPY, no ADD. RUN encadenados con && y limpieza en la misma capa.
- Usuario no root. EXPOSE 5000. Gunicorn con bind 0.0.0.0:5000 y "app:create_app()". CMD en forma exec (JSON).

compose.yaml (debe calzar con el ejemplo del enunciado; sin clave version, se usa `docker compose` v2):
- flask: image aura-map:latest, build context . y dockerfile Dockerfile, ports "8080:5000", env_file .env.dev (aquí vive DB_PASSWORD), environment APP_VERSION, DB_HOST=postgres, DB_DATABASE=auradb, DB_USER=aurauser, networks public y private, depends_on postgres con condition service_healthy.
- postgres: image postgres:16.3, environment POSTGRES_USER=aurauser, POSTGRES_DB=auradb, POSTGRES_PASSWORD_FILE=/run/secrets/pg_password, secrets pg_password, volumes postgres-data:/var/lib/postgresql/data, networks solo private, SIN ports, healthcheck ["CMD-SHELL","pg_isready -U aurauser -d auradb"] con interval 5s, timeout 5s, retries 5.
- networks: public (bridge) y private (internal: true). volumes: postgres-data. secrets: pg_password desde ./secrets/pg_password.txt.
- .env.dev y secrets/pg_password.txt van en .gitignore y .dockerignore.

devops.sh (bash, set -euo pipefail, ayuda con -h, funciona en Linux, macOS y Git Bash/WSL):
- clone <url> [dir]: clona, crea venv e instala requirements-dev.
- test: crea el venv si falta y corre `pytest -v --cov=app --cov-report=term-missing`.
- local: modo local sin Docker con SQLite en instance/, corre seed y `flask --app app:create_app run --debug`.
- docker: si faltan secrets/pg_password.txt o .env.dev, genera una contraseña aleatoria y escribe la MISMA en ambos; luego `docker compose up -d --build`, espera a que postgres esté healthy, hace curl a localhost:8080/health y muestra `docker compose ps`.
- down [-v]: baja los servicios; con -v advierte que borra los datos del volumen.
- evidence: guarda en docs/evidencias/*.txt las salidas de git log --oneline --graph, pytest, docker compose ps, curl /health, `docker network inspect <proyecto>_private --format 'internal={{.Internal}}'` y `docker compose port postgres 5432` (debe salir vacío).

## 3. Roles DevOps

- Persona A, Release Manager / Integración: dueña del repo y de GitFlow, protección de ramas, cumplimiento de Conventional Commits, revisión de PRs, release y tag.
- Persona B, QA & Test Automation: estrategia de pruebas, pytest y cobertura, pipeline de CI que corre las pruebas en cada PR.
- Persona C, Platform / Container Engineer: Dockerfile, compose (redes, secretos, volumen, healthcheck) y automatización con devops.sh.
Los tres desarrollan features; el rol define de qué responde cada uno y qué revisa con más rigor.

## 4. ROADMAP (14 commits, GitFlow)

ID | Quién | Rama | Mensaje exacto | Contenido | Revisor
C1 | A | main (directo) | chore: inicializar proyecto AuraMap con estructura base | app factory mínima con /health, requirements, .gitignore, .dockerignore, README esqueleto y CLAUDE.md con las secciones 0 a 6 de este prompt copiadas literal (sin la línea SOY). Luego crear develop desde main y hacer push de ambas. | —
C2 | B | feature/publicar-batallas | feat(battles): publicar y listar batallas de aura | modelo Battle, validación en services/battles.py (título obligatorio, fecha futura, cupo 1-100, lat y lng en rango), POST y GET /api/battles, GET /api/battles/<id> | C
C3 | B | feature/publicar-batallas | test(battles): pruebas de validación y endpoints de batallas | 6 pruebas: payload válido, título vacío, fecha pasada, cupo inválido, POST devuelve 201, GET lista | C
C4 | C | feature/busqueda-cercana | feat(geo): buscar batallas cercanas por radio y mostrarlas en mapa | haversine_km y filter_within_radius en services/geo.py, filtros lat, lng, radius_km y district, vista / con Leaflet y formulario | A
C5 | C | feature/busqueda-cercana | test(geo): pruebas de distancia y filtro por radio | 4 pruebas: mismo punto da 0, (0,0) a (0,1) ≈ 111.19 km ±0.5, el filtro excluye lejanas, coordenadas inválidas lanzan ValueError | A
C6 | A | feature/inscripcion | feat(rsvp): inscripción a batallas con control de cupo | modelo Rsvp, services/rsvp.py, endpoint y 3 pruebas (inscribe con cupo, 409 si está lleno, 409 si es duplicado) | B
C7 | C | feature/dockerizar | chore(docker): Dockerfile multi-stage con Gunicorn y usuario no root | Dockerfile y .dockerignore según sección 2 | B
C8 | C | feature/dockerizar | chore(compose): orquestar flask y postgres con redes, secretos, volumen y healthcheck | compose.yaml, .env.dev.example, secrets/.gitkeep, verificación con `docker compose up` y /health | B
C9 | B | refactor/capa-datos | refactor(battles): separar consultas a la DB de la lógica de dominio | rutas delgadas, consultas en funciones de repositorio, todas las pruebas siguen verdes sin cambiarlas | A
C10 | A | fix/conexion-db | fix(db): recuperar conexiones tras reinicio de Postgres | reproducir primero: con los servicios arriba, `docker compose restart postgres` y pedir /api/battles hasta ver el error. Arreglar con pool_pre_ping y reintentos con backoff al arrancar (depends_on solo ordena el arranque, no protege si la DB cae después). Documentar antes y después en el PR. Si el error no se reproduce, dímelo y no inventes el bug. | C
C11 | C | feature/automatizacion | chore(scripts): automatizar clonación, pruebas y ejecución local | devops.sh completo según sección 2 | A
C12 | B | ci/pruebas-en-pr | ci: ejecutar pruebas y build de imagen en cada pull request | .github/workflows/tests.yml: Python 3.12, ./devops.sh test y docker build, en pull_request hacia develop y main | C
C13 | A | docs/readme-informe | docs: documentar prerrequisitos, uso de devops.sh y borrador del informe | README con prerrequisitos, comando exacto de pruebas (`./devops.sh test`, equivalente `pytest -v`), cómo levantar local y con Docker, roles del equipo. docs/INFORME.md con secciones a) a g) del enunciado, marcadores de capturas y la sugerencia de 6 commits a analizar: C2, C3, C8, C9, C10, C12. | B
C14 | A | release/1.0.0 | chore(release): versión 1.0.0 | APP_VERSION=1.0.0. PR hacia main (aprueban B y C), merge --no-ff, tag v1.0.0, y merge de main de vuelta a develop. | B y C

## 5. Reglas de calidad

- Código pequeño y legible, sin sobreingeniería.
- Antes de cada commit, las pruebas deben pasar.
- Cada PR lleva descripción corta: qué cambia, cómo probarlo y la evidencia (salida de pytest o de docker compose ps).
- Si algo del enunciado choca con este plan, avísame antes de desviarte.

## 6. Salida (siempre al terminar)

1. Qué hice: commits con hash y mensaje, link del PR, resultado de las pruebas.
2. Pendiente manual para mí: checklist de lo que tú no puedes hacer. En bootstrap incluye verificar versiones (git, python3.12, docker compose version, gh auth status). Después de C1 incluye: crear el repo público vacío si no existe, agregar a los compañeros como collaborators, poner develop como rama por defecto, proteger main y develop (require pull request, 1 approval, bloquear force push) y en Settings > General > Pull Requests dejar solo "Allow merge commits".
3. Mensaje para el equipo: texto listo para pegar en WhatsApp, directo y corto, en prosa. Debe decir quién sigue, qué PR revisar con su link y qué bloque le toca. Para quien aún no tiene el repo, agrega el setup: clonar, `git config user.name` y `user.email` con su cuenta de GitHub (así el historial muestra a los 3 autores) y `gh auth login`. Cierra con el arranque exacto: entrar a la carpeta, abrir `claude` y escribir "SOY: Persona X. Lee CLAUDE.md y opera según la sección 0."
