"""Rutas de la API de batallas y vista del mapa."""
from flask import Blueprint, jsonify, render_template, request

from app.db import db
from app.models import Battle
from app.services.battles import BattleValidationError, validate_battle_payload
from app.services.geo import filter_within_radius


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
    consulta = Battle.query

    distrito = request.args.get("district", "").strip()
    if distrito:
        consulta = consulta.filter(db.func.lower(Battle.distrito) == distrito.lower())

    batallas = consulta.order_by(Battle.fecha.asc(), Battle.id.asc()).all()

    cerca = ("lat", "lng", "radius_km")
    recibidos = [campo for campo in cerca if request.args.get(campo)]
    if recibidos:
        if len(recibidos) != len(cerca):
            return jsonify(
                {"error": "Para buscar cerca envía lat, lng y radius_km juntos."}
            ), 400
        try:
            batallas = filter_within_radius(
                batallas,
                request.args.get("lat"),
                request.args.get("lng"),
                request.args.get("radius_km"),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    return jsonify([batalla.to_dict() for batalla in batallas])


@battles_bp.get("/api/battles/<int:battle_id>")
def get_battle(battle_id: int):
    batalla = db.session.get(Battle, battle_id)
    if batalla is None:
        return jsonify({"error": "Batalla no encontrada."}), 404
    return jsonify(batalla.to_dict())


@battles_bp.get("/")
def mapa():
    return render_template("index.html")
