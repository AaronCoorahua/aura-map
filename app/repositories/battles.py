"""Consultas y persistencia de batallas."""
from sqlalchemy import func, select

from app.db import db
from app.models import Battle


def save_battle(data: dict) -> Battle:
    """Guarda una batalla nueva y devuelve la instancia persistida."""
    battle = Battle(**data)
    db.session.add(battle)
    db.session.commit()
    return battle


def find_battles(district: str | None = None) -> list[Battle]:
    """Lista batallas ordenadas, filtrando por distrito cuando se indica."""
    statement = select(Battle)
    if district:
        statement = statement.where(
            func.lower(Battle.distrito) == district.lower()
        )
    statement = statement.order_by(Battle.fecha.asc(), Battle.id.asc())
    return list(db.session.scalars(statement).all())


def find_battle_by_id(battle_id: int) -> Battle | None:
    """Busca una batalla por clave primaria usando la sesión de SQLAlchemy."""
    return db.session.get(Battle, battle_id)
