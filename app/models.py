"""Modelos persistidos de AuraMap."""
from app.db import db


class Battle(db.Model):
    """Batalla publicada por un organizador."""

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False, default="")
    distrito = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(250), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    cupo = db.Column(db.Integer, nullable=False)
    organizador = db.Column(db.String(200), nullable=False)
    tiene_permiso = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self) -> dict:
        """Representación JSON estable para la API."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "distrito": self.distrito,
            "direccion": self.direccion,
            "lat": self.lat,
            "lng": self.lng,
            "fecha": self.fecha.isoformat(),
            "cupo": self.cupo,
            "organizador": self.organizador,
            "tiene_permiso": self.tiene_permiso,
        }
