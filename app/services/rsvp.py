"""Reglas de inscripción a batallas, sin tocar la base de datos."""
from typing import Any, Iterable


class RsvpError(ValueError):
    """Error base de inscripción."""


class RsvpValidationError(RsvpError):
    """El payload de inscripción no es válido."""


class BattleFullError(RsvpError):
    """La batalla ya no tiene cupo."""


class DuplicateRsvpError(RsvpError):
    """Esa persona ya estaba inscrita en la batalla."""


def validate_rsvp_payload(payload: Any) -> str:
    """Devuelve el nombre normalizado o lanza RsvpValidationError."""
    if not isinstance(payload, dict):
        raise RsvpValidationError("El cuerpo debe ser un objeto JSON.")

    nombre = payload.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        raise RsvpValidationError("El nombre es obligatorio.")
    return nombre.strip()


def check_can_rsvp(nombre: str, cupo: int, inscritos: Iterable[str]) -> str:
    """Valida cupo y duplicados. Devuelve el nombre listo para persistir."""
    nombres = [existente.strip().lower() for existente in inscritos]

    if len(nombres) >= cupo:
        raise BattleFullError("La batalla ya no tiene cupo disponible.")
    if nombre.strip().lower() in nombres:
        raise DuplicateRsvpError("Esa persona ya está inscrita en la batalla.")
    return nombre.strip()
