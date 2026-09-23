"""Datos de ejemplo: tres batallas de aura en Lima."""
from datetime import datetime, timedelta, timezone

from app.db import db
from app.models import Battle


def batallas_de_ejemplo(ahora: datetime) -> list[dict]:
    return [
        {
            "titulo": "Batalla de Aura en el Parque Kennedy",
            "descripcion": "Duelos 1 vs 1 de puro aura farming. Los gatos del parque son jurado.",
            "distrito": "Miraflores",
            "direccion": "Parque Kennedy, Av. Diagonal",
            "lat": -12.1211,
            "lng": -77.0297,
            "fecha": ahora + timedelta(days=3, hours=2),
            "cupo": 20,
            "organizador": "Colectivo Aura Miraflores",
            "tiene_permiso": True,
        },
        {
            "titulo": "Duelo de Aura en la Plaza San Martín",
            "descripcion": "Formato torneo: pierde quien pierda la compostura primero.",
            "distrito": "Cercado de Lima",
            "direccion": "Plaza San Martín, Jr. de la Unión",
            "lat": -12.0515,
            "lng": -77.0346,
            "fecha": ahora + timedelta(days=7, hours=5),
            "cupo": 40,
            "organizador": "Aura Centro Lima",
            "tiene_permiso": True,
        },
        {
            "titulo": "Aura Farming al atardecer en el Malecón de Barranco",
            "descripcion": "Batalla libre con el sunset de fondo. Se gana con presencia, no con gritos.",
            "distrito": "Barranco",
            "direccion": "Puente de los Suspiros",
            "lat": -12.1496,
            "lng": -77.0221,
            "fecha": ahora + timedelta(days=10, hours=1),
            "cupo": 15,
            "organizador": "Barranco Aura Club",
            "tiene_permiso": False,
        },
    ]


def seed_battles() -> int:
    """Inserta las batallas de ejemplo si la tabla está vacía. Devuelve cuántas insertó."""
    if db.session.query(Battle.id).first() is not None:
        return 0
    ahora = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    batallas = [Battle(**datos) for datos in batallas_de_ejemplo(ahora)]
    db.session.add_all(batallas)
    db.session.commit()
    return len(batallas)
