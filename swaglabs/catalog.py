"""Catálogo de productos y ordenamiento (RF-02)."""

from decimal import Decimal

PRODUCTS = {
    "sauce-labs-backpack": ("Sauce Labs Backpack", Decimal("29.99")),
    "sauce-labs-bike-light": ("Sauce Labs Bike Light", Decimal("9.99")),
    "sauce-labs-bolt-t-shirt": ("Sauce Labs Bolt T-Shirt", Decimal("15.99")),
    "sauce-labs-fleece-jacket": ("Sauce Labs Fleece Jacket", Decimal("49.99")),
    "sauce-labs-onesie": ("Sauce Labs Onesie", Decimal("7.99")),
    "test.allthethings()-t-shirt-(red)": ("Test.allTheThings() T-Shirt (Red)", Decimal("15.99")),
}

SORT_OPTIONS = ("az", "za", "lohi", "hilo")  # Name A-Z (por defecto), Name Z-A, Price low-high, Price high-low


def name(product_id):
    return PRODUCTS[product_id][0]


def price(product_id):
    if product_id not in PRODUCTS:
        raise KeyError(f"Producto inexistente: {product_id}")
    return PRODUCTS[product_id][1]


def sorted_products(option="az"):
    """Devuelve la lista de IDs ordenada según la opción del filtro."""
    if option not in SORT_OPTIONS:
        raise ValueError(f"Opción de ordenamiento no válida: {option}")
    ids = list(PRODUCTS)
    if option == "az":
        return sorted(ids, key=name)
    if option == "za":
        return sorted(ids, key=name, reverse=True)
    if option == "lohi":
        return sorted(ids, key=lambda p: (price(p), name(p)))
    return sorted(ids, key=lambda p: (-price(p), name(p)))
