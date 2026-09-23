"""Cálculo de distancias y filtrado geográfico, sin tocar la base de datos."""
from math import asin, cos, radians, sin, sqrt
from typing import Iterable, TypeVar

RADIO_TIERRA_KM = 6371.0

T = TypeVar("T")


def validar_coordenada(lat: float, lng: float) -> tuple[float, float]:
    """Devuelve la coordenada como floats o lanza ValueError si no es válida."""
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError) as exc:
        raise ValueError("Las coordenadas deben ser números.") from exc

    if not -90 <= lat_f <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90.")
    if not -180 <= lng_f <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180.")
    return lat_f, lng_f


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distancia en kilómetros entre dos puntos sobre la esfera terrestre."""
    lat1, lng1 = validar_coordenada(lat1, lng1)
    lat2, lng2 = validar_coordenada(lat2, lng2)

    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    )
    return 2 * RADIO_TIERRA_KM * asin(sqrt(a))


def filter_within_radius(
    items: Iterable[T], lat: float, lng: float, radius_km: float
) -> list[T]:
    """Deja solo los elementos cuyo (lat, lng) cae dentro del radio dado."""
    lat, lng = validar_coordenada(lat, lng)
    try:
        radio = float(radius_km)
    except (TypeError, ValueError) as exc:
        raise ValueError("El radio debe ser un número en kilómetros.") from exc
    if radio <= 0:
        raise ValueError("El radio debe ser mayor que cero.")

    return [
        item
        for item in items
        if haversine_km(lat, lng, item.lat, item.lng) <= radio
    ]
