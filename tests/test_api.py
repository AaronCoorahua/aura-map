def test_health_responde_ok(client):
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["status"] == "ok"


def test_health_incluye_version(client):
    datos = client.get("/health").get_json()
    assert "version" in datos
