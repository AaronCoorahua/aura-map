"""Instancia unica de SQLAlchemy compartida por la aplicacion."""
import time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

db = SQLAlchemy()

INTENTOS_CONEXION = 5
ESPERA_INICIAL_SEGUNDOS = 1


def wait_for_db(app, intentos: int = INTENTOS_CONEXION, espera_inicial: float = ESPERA_INICIAL_SEGUNDOS) -> None:
    """Reintenta la conexion inicial a la DB con backoff exponencial.

    depends_on con service_healthy solo ordena el arranque de los contenedores;
    no protege si Postgres tarda en aceptar conexiones o cae despues de arrancar.
    """
    espera = espera_inicial
    for intento in range(1, intentos + 1):
        try:
            with app.app_context(), db.engine.connect():
                pass
            return
        except OperationalError:
            if intento == intentos:
                raise
            time.sleep(espera)
            espera *= 2


def create_tables(app) -> None:
    """Crea las tablas que falten. Es idempotente."""
    with app.app_context():
        try:
            db.create_all()
        except (IntegrityError, ProgrammingError):
            # Los workers de Gunicorn arrancan a la vez: si otro ya creó las tablas, basta reintentar.
            db.create_all()
