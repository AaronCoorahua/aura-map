"""Rutas de la API de batallas y vista del mapa."""
from flask import Blueprint, jsonify, render_template, request

from app.repositories.battles import find_battle_by_id, find_battles, save_battle
from app.repositories.rsvp import find_names_by_battle, save_rsvp
from app.services.battles import BattleValidationError, validate_battle_payload
from app.services.geo import filter_within_radius
from app.services.rsvp import (
    BattleFullError,
    DuplicateRsvpError,
    RsvpValidationError,
    check_can_rsvp,
    validate_rsvp_payload,
)


battles_bp = Blueprint("battles", __name__)


@battles_bp.post("/api/battles")
def create_battle():
    try:
        datos = validate_battle_payload(request.get_json(silent=True))
    except BattleValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    batalla = save_battle(datos)
    return jsonify(batalla.to_dict()), 201


@battles_bp.get("/api/battles")
def list_battles():
    distrito = request.args.get("district", "").strip()
    batallas = find_battles(distrito or None)

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
    batalla = find_battle_by_id(battle_id)
    if batalla is None:
        return jsonify({"error": "Batalla no encontrada."}), 404
    return jsonify(batalla.to_dict())


@battles_bp.post("/api/battles/<int:battle_id>/rsvp")
def rsvp_battle(battle_id: int):
    batalla = find_battle_by_id(battle_id)
    if batalla is None:
        return jsonify({"error": "Batalla no encontrada."}), 404

    try:
        nombre = validate_rsvp_payload(request.get_json(silent=True))
    except RsvpValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        nombre = check_can_rsvp(nombre, batalla.cupo, find_names_by_battle(battle_id))
    except (BattleFullError, DuplicateRsvpError) as exc:
        return jsonify({"error": str(exc)}), 409

    inscripcion = save_rsvp(battle_id, nombre)
    return jsonify(inscripcion.to_dict()), 201


@battles_bp.get("/")
def mapa():
    return render_template("index.html")
