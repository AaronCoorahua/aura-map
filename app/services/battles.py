"""Validación de dominio para batallas."""
from datetime import datetime, timezone
from typing import Any


class BattleValidationError(ValueError):
    """Indica que un payload de batalla no cumple las reglas del MVP."""


def validate_battle_payload(payload: Any) -> dict:
    """Valida y normaliza un payload de batalla para persistirlo."""
    if not isinstance(payload, dict):
        raise BattleValidationError("El cuerpo debe ser un objeto JSON.")

    titulo = payload.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        raise BattleValidationError("El título es obligatorio.")

    raw_fecha = payload.get("fecha")
    if not isinstance(raw_fecha, str):
        raise BattleValidationError("La fecha es obligatoria y debe ser ISO 8601.")
    try:
        fecha = datetime.fromisoformat(raw_fecha.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BattleValidationError("La fecha debe tener formato ISO 8601.") from exc
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    fecha = fecha.astimezone(timezone.utc)
    if fecha <= datetime.now(timezone.utc):
        raise BattleValidationError("La fecha debe ser futura.")

    cupo = payload.get("cupo")
    if isinstance(cupo, bool) or not isinstance(cupo, int) or not 1 <= cupo <= 100:
        raise BattleValidationError("El cupo debe ser un entero entre 1 y 100.")

    coordenadas = {}
    for campo, minimo, maximo in (("lat", -90, 90), ("lng", -180, 180)):
        valor = payload.get(campo)
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise BattleValidationError(f"{campo} debe ser un número válido.")
        if not minimo <= valor <= maximo:
            raise BattleValidationError(f"{campo} debe estar entre {minimo} y {maximo}.")
        coordenadas[campo] = float(valor)

    campos_texto = ("distrito", "direccion", "organizador")
    normalizados = {}
    for campo in campos_texto:
        valor = payload.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            raise BattleValidationError(f"{campo} es obligatorio.")
        normalizados[campo] = valor.strip()

    descripcion = payload.get("descripcion", "")
    if not isinstance(descripcion, str):
        raise BattleValidationError("La descripción debe ser texto.")
    tiene_permiso = payload.get("tiene_permiso", False)
    if not isinstance(tiene_permiso, bool):
        raise BattleValidationError("tiene_permiso debe ser booleano.")

    return {
        "titulo": titulo.strip(),
        "descripcion": descripcion.strip(),
        **normalizados,
        **coordenadas,
        "fecha": fecha.replace(tzinfo=None),
        "cupo": cupo,
        "tiene_permiso": tiene_permiso,
    }
