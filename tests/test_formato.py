"""Pruebas del formato de duraciones y periodos."""

from datetime import date, timedelta

import pytest

from wikitunes.formato import formatear_duracion, formatear_periodo


@pytest.mark.parametrize(
    ("duracion", "texto"),
    [
        (0, "0:00"),
        (191, "3:11"),
        (timedelta(seconds=4749), "1:19:09"),
        (timedelta(minutes=47, seconds=3), "47:03"),
        (None, "—"),
    ],
)
def test_formatear_duracion(duracion, texto):
    assert formatear_duracion(duracion) == texto


@pytest.mark.parametrize(
    ("inicio", "fin", "texto"),
    [
        (date(1972, 7, 1), date(1974, 12, 31), "1972–1974"),
        (date(2013, 9, 25), None, "2013–"),
        (date(1970, 1, 1), date(1970, 6, 30), "1970"),
        (None, None, "—"),
        (None, date(1962, 8, 16), "?–1962"),
    ],
)
def test_formatear_periodo(inicio, fin, texto):
    assert formatear_periodo(inicio, fin) == texto
