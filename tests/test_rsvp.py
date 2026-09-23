from datetime import datetime, timedelta, timezone


def crear_batalla(client, cupo):
    payload = {
        "titulo": "Batalla con cupo",
        "descripcion": "Competencia abierta",
        "distrito": "Miraflores",
        "direccion": "Parque Kennedy",
        "lat": -12.121,
        "lng": -77.029,
        "fecha": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "cupo": cupo,
        "organizador": "Colectivo Aura",
        "tiene_permiso": True,
    }
    return client.post("/api/battles", json=payload).get_json()["id"]


def test_inscribe_cuando_hay_cupo(client):
    battle_id = crear_batalla(client, cupo=2)

    respuesta = client.post(f"/api/battles/{battle_id}/rsvp", json={"nombre": "Ana"})

    assert respuesta.status_code == 201
    assert respuesta.get_json()["nombre"] == "Ana"


def test_rechaza_cuando_no_hay_cupo(client):
    battle_id = crear_batalla(client, cupo=1)
    client.post(f"/api/battles/{battle_id}/rsvp", json={"nombre": "Ana"})

    respuesta = client.post(f"/api/battles/{battle_id}/rsvp", json={"nombre": "Beto"})

    assert respuesta.status_code == 409
    assert "cupo" in respuesta.get_json()["error"]


def test_rechaza_inscripcion_duplicada(client):
    battle_id = crear_batalla(client, cupo=10)
    client.post(f"/api/battles/{battle_id}/rsvp", json={"nombre": "Ana"})

    respuesta = client.post(f"/api/battles/{battle_id}/rsvp", json={"nombre": "  ana  "})

    assert respuesta.status_code == 409
    assert "ya está inscrita" in respuesta.get_json()["error"]
