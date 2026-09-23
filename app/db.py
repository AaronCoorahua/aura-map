"""Instancia unica de SQLAlchemy compartida por la aplicacion."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
