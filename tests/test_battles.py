from datetime import datetime, timedelta, timezone

import pytest

from app.services.battles import BattleValidationError, validate_battle_payload


def payload_batalla(**cambios):
    datos = {
        "titulo": "Batalla de prueba",
        "descripcion": "Competencia abierta",
        "distrito": "Miraflores",
        "direccion": "Parque Kennedy",
        "lat": -12.121,
        "lng": -77.029,
        "fecha": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "cupo": 32,
        "organizador": "Colectivo Aura",
        "tiene_permiso": True,
    }
    datos.update(cambios)
    return datos


def test_payload_valido():
    datos = validate_battle_payload(payload_batalla())
    assert datos["titulo"] == "Batalla de prueba"
    assert datos["cupo"] == 32


def test_titulo_vacio():
    with pytest.raises(BattleValidationError, match="título es obligatorio"):
        validate_battle_payload(payload_batalla(titulo="  "))


def test_fecha_pasada():
    fecha_pasada = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    with pytest.raises(BattleValidationError, match="fecha debe ser futura"):
        validate_battle_payload(payload_batalla(fecha=fecha_pasada))


def test_cupo_invalido():
    with pytest.raises(BattleValidationError, match="cupo debe ser un entero"):
        validate_battle_payload(payload_batalla(cupo=101))


def test_post_devuelve_201(client):
    respuesta = client.post("/api/battles", json=payload_batalla())
    assert respuesta.status_code == 201
    assert respuesta.get_json()["titulo"] == "Batalla de prueba"


def test_get_lista_batallas(client):
    client.post("/api/battles", json=payload_batalla())

    respuesta = client.get("/api/battles")

    assert respuesta.status_code == 200
    assert [batalla["titulo"] for batalla in respuesta.get_json()] == ["Batalla de prueba"]
