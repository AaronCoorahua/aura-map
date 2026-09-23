"""Consultas y persistencia de inscripciones."""
from sqlalchemy import select

from app.db import db
from app.models import Rsvp


def find_names_by_battle(battle_id: int) -> list[str]:
    """Nombres ya inscritos en una batalla."""
    statement = select(Rsvp.nombre).where(Rsvp.battle_id == battle_id)
    return list(db.session.scalars(statement).all())


def save_rsvp(battle_id: int, nombre: str) -> Rsvp:
    """Guarda una inscripción y devuelve la instancia persistida."""
    inscripcion = Rsvp(battle_id=battle_id, nombre=nombre)
    db.session.add(inscripcion)
    db.session.commit()
    return inscripcion
