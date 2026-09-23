#!/usr/bin/env bash
# Automatización de AuraMap. Funciona en Linux, macOS y Git Bash/WSL.
set -euo pipefail

VENV_DIR=".venv"
PUERTO_APP=8080

uso() {
  cat <<'AYUDA'
AuraMap — automatización del proyecto

Uso: ./devops.sh <comando> [opciones]

Comandos:
  clone <url> [dir]  Clona el repositorio, crea el venv e instala las dependencias.
  test               Corre las pruebas con cobertura (crea el venv si falta).
  local              Levanta la app sin Docker, con SQLite en instance/.
  docker             Genera los secretos si faltan y levanta flask + postgres.
  down [-v]          Baja los servicios. Con -v borra además el volumen de datos.
  evidence           Guarda las salidas de verificación en docs/evidencias/.
  -h | --help        Muestra esta ayuda.
AYUDA
}

aviso() { printf '\n==> %s\n' "$*"; }
error() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

# Python del venv: en Windows vive en Scripts/, en el resto en bin/.
python_venv() {
  if [ -x "$VENV_DIR/bin/python" ]; then
    echo "$VENV_DIR/bin/python"
  else
    echo "$VENV_DIR/Scripts/python.exe"
  fi
}

python_sistema() {
  for candidato in python3.12 python3 python; do
    if command -v "$candidato" >/dev/null 2>&1; then
      echo "$candidato"
      return 0
    fi
  done
  error "No encontré Python. Instala Python 3.12."
}

asegurar_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    aviso "Creando el entorno virtual en $VENV_DIR"
    "$(python_sistema)" -m venv "$VENV_DIR"
  fi
  aviso "Instalando dependencias de desarrollo"
  "$(python_venv)" -m pip install --quiet --upgrade pip
  "$(python_venv)" -m pip install --quiet -r requirements-dev.txt
}

nombre_proyecto() {
  basename "$PWD" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_-'
}

cmd_clone() {
  local url="${1:-}" destino="${2:-}"
  [ -n "$url" ] || error "Falta la URL. Uso: ./devops.sh clone <url> [dir]"
  [ -n "$destino" ] || destino="$(basename "$url" .git)"

  aviso "Clonando $url en $destino"
  git clone "$url" "$destino"
  cd "$destino"
  asegurar_venv
  aviso "Listo. Entra con: cd $destino && ./devops.sh test"
}

cmd_test() {
  asegurar_venv
  aviso "Ejecutando las pruebas"
  "$(python_venv)" -m pytest -v --cov=app --cov-report=term-missing
}

cmd_local() {
  asegurar_venv
  mkdir -p instance

  export FLASK_APP="app:create_app"
  export DATABASE_URL="sqlite:///$PWD/instance/auramap.db"

  aviso "Cargando datos de ejemplo"
  # El comando seed llega en C10; hasta entonces avisamos sin abortar.
  "$(python_venv)" -m flask seed || aviso "No pude ejecutar 'flask seed'; sigo sin datos de ejemplo."

  aviso "Arrancando en http://localhost:5000 (Ctrl+C para cortar)"
  "$(python_venv)" -m flask run --debug
}

generar_secretos() {
  if [ -f secrets/pg_password.txt ] && [ -f .env.dev ]; then
    aviso "Secretos ya presentes, los reutilizo"
    return
  fi

  aviso "Generando una contraseña nueva para Postgres"
  mkdir -p secrets
  local clave
  clave="$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 24)"
  # La MISMA contraseña va en los dos archivos: uno lo lee Postgres, el otro Flask.
  printf '%s' "$clave" > secrets/pg_password.txt
  printf 'DB_PASSWORD=%s\n' "$clave" > .env.dev
}

esperar_postgres() {
  aviso "Esperando a que Postgres esté healthy"
  local intento
  for intento in $(seq 1 30); do
    if docker compose ps postgres | grep -q "healthy"; then
      aviso "Postgres healthy tras $intento intento(s)"
      return 0
    fi
    sleep 2
  done
  error "Postgres no llegó a healthy. Revisa: docker compose logs postgres"
}

# Postgres healthy no significa que Gunicorn ya esté escuchando: hay que reintentar.
esperar_health() {
  aviso "Probando /health"
  local intento
  for intento in $(seq 1 20); do
    if curl -fsS "http://localhost:$PUERTO_APP/health"; then
      printf '\n'
      return 0
    fi
    sleep 2
  done
  error "La app no respondió en /health. Revisa: docker compose logs flask"
}

cmd_docker() {
  command -v docker >/dev/null 2>&1 || error "Docker no está instalado o no está en el PATH."
  generar_secretos

  aviso "Levantando los servicios"
  docker compose up -d --build
  esperar_postgres

  esperar_health

  aviso "Estado de los servicios"
  docker compose ps
}

cmd_down() {
  if [ "${1:-}" = "-v" ]; then
    aviso "ATENCIÓN: esto borra el volumen postgres-data y con él todas las batallas guardadas."
    docker compose down -v
  else
    docker compose down
  fi
}

cmd_evidence() {
  local destino="docs/evidencias"
  mkdir -p "$destino"
  aviso "Guardando evidencias en $destino"

  git log --oneline --graph --all > "$destino/git-log.txt"
  "$(python_venv)" -m pytest -v --cov=app --cov-report=term-missing \
    > "$destino/pytest.txt" 2>&1 || true
  docker compose ps > "$destino/compose-ps.txt" 2>&1 || true
  curl -fsS "http://localhost:$PUERTO_APP/health" > "$destino/health.txt" 2>&1 || true
  docker network inspect "$(nombre_proyecto)_private" --format 'internal={{.Internal}}' \
    > "$destino/red-privada.txt" 2>&1 || true
  # Postgres no debe publicar puertos al host: la consulta no devuelve nada.
  local publicado
  publicado="$(docker compose port postgres 5432 2>/dev/null || true)"
  if [ -n "$publicado" ] && [ "${publicado%%:*}" != "invalid IP" ]; then
    printf 'PROBLEMA: Postgres está publicando %s\n' "$publicado"
  else
    printf 'Sin puertos publicados: Postgres solo es alcanzable desde la red privada.\n'
  fi > "$destino/postgres-puerto.txt"

  ls -1 "$destino"
}

comando="${1:--h}"
shift || true

case "$comando" in
  clone)    cmd_clone "$@" ;;
  test)     cmd_test ;;
  local)    cmd_local ;;
  docker)   cmd_docker ;;
  down)     cmd_down "$@" ;;
  evidence) cmd_evidence ;;
  -h|--help) uso ;;
  *)        uso; error "Comando desconocido: $comando" ;;
esac
