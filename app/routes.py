"""Rutas de la API de batallas."""
from flask import Blueprint, jsonify, request

from app.db import db
from app.models import Battle
from app.services.battles import BattleValidationError, validate_battle_payload


battles_bp = Blueprint("battles", __name__)


@battles_bp.post("/api/battles")
def create_battle():
    try:
        datos = validate_battle_payload(request.get_json(silent=True))
    except BattleValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    batalla = Battle(**datos)
    db.session.add(batalla)
    db.session.commit()
    return jsonify(batalla.to_dict()), 201


@battles_bp.get("/api/battles")
def list_battles():
    batallas = Battle.query.order_by(Battle.fecha.asc(), Battle.id.asc()).all()
    return jsonify([batalla.to_dict() for batalla in batallas])


@battles_bp.get("/api/battles/<int:battle_id>")
def get_battle(battle_id: int):
    batalla = db.session.get(Battle, battle_id)
    if batalla is None:
        return jsonify({"error": "Batalla no encontrada."}), 404
    return jsonify(batalla.to_dict())
