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


class Rsvp(db.Model):
    """Inscripción de una persona a una batalla."""

    __table_args__ = (db.UniqueConstraint("battle_id", "nombre"),)

    id = db.Column(db.Integer, primary_key=True)
    battle_id = db.Column(db.Integer, db.ForeignKey("battle.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)

    battle = db.relationship("Battle", backref=db.backref("inscripciones", lazy=True))

    def to_dict(self) -> dict:
        return {"id": self.id, "battle_id": self.battle_id, "nombre": self.nombre}
