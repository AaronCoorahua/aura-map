"""Instancia unica de SQLAlchemy compartida por la aplicacion."""
import time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

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
