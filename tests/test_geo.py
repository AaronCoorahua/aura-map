from types import SimpleNamespace

import pytest

from app.services.geo import filter_within_radius, haversine_km


def punto(lat, lng, nombre=""):
    return SimpleNamespace(lat=lat, lng=lng, titulo=nombre)


def test_mismo_punto_da_cero():
    assert haversine_km(-12.121, -77.029, -12.121, -77.029) == pytest.approx(0.0)


def test_un_grado_de_longitud_en_el_ecuador():
    assert haversine_km(0, 0, 0, 1) == pytest.approx(111.19, abs=0.5)


def test_el_filtro_excluye_las_lejanas():
    miraflores = punto(-12.121, -77.029, "Miraflores")
    cusco = punto(-13.532, -71.967, "Cusco")

    cercanas = filter_within_radius([miraflores, cusco], -12.121, -77.029, 10)

    assert [batalla.titulo for batalla in cercanas] == ["Miraflores"]


def test_coordenadas_invalidas_lanzan_value_error():
    with pytest.raises(ValueError):
        haversine_km(100, 0, 0, 0)
