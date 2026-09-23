"""Configuracion de la aplicacion leida desde variables de entorno."""
import os


def database_uri() -> str:
    """URL de la base de datos.

    DATABASE_URL tiene prioridad. Si no hay DB_HOST se usa SQLite local
    (modo desarrollo sin Docker y pruebas).
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    host = os.getenv("DB_HOST")
    if not host:
        return "sqlite:///auramap.db"

    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_DATABASE", "auradb")
    user = os.getenv("DB_USER", "aurauser")
    password = os.getenv("DB_PASSWORD", "")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


class Config:
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # pool_pre_ping evita usar conexiones que Postgres ya cerró (p. ej. tras un reinicio).
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
