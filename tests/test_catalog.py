"""RF-02 Catálogo y ordenamiento."""
from decimal import Decimal

import pytest

from swaglabs import catalog


def test_catalogo_tiene_seis_productos():
    assert len(catalog.PRODUCTS) == 6


def test_orden_por_defecto_es_nombre_a_z():
    names = [catalog.name(p) for p in catalog.sorted_products()]
    assert names == sorted(names)


def test_orden_nombre_z_a():
    names = [catalog.name(p) for p in catalog.sorted_products("za")]
    assert names == sorted(names, reverse=True)


def test_orden_precio_menor_a_mayor():
    prices = [catalog.price(p) for p in catalog.sorted_products("lohi")]
    assert prices == sorted(prices)


def test_cp006_orden_precio_mayor_a_menor():
    prices = [str(catalog.price(p)) for p in catalog.sorted_products("hilo")]
    assert prices == ["49.99", "29.99", "15.99", "15.99", "9.99", "7.99"]


def test_opcion_de_orden_invalida():
    with pytest.raises(ValueError):
        catalog.sorted_products("precio")


def test_precio_de_producto_inexistente():
    with pytest.raises(KeyError):
        catalog.price("producto-x")


def test_precios_son_decimales_exactos():
    assert catalog.price("sauce-labs-backpack") == Decimal("29.99")
