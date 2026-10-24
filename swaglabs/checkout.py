"""Checkout: datos del comprador (RF-04) y resumen con impuesto (RF-05)."""

import re
from decimal import Decimal, ROUND_HALF_UP

from . import catalog

TAX_RATE = Decimal("0.08")  # Supuesto AMB-05: 8 % del item total
CENT = Decimal("0.01")

ERR_FIRST = "Error: First Name is required"
ERR_LAST = "Error: Last Name is required"
ERR_ZIP = "Error: Postal Code is required"
ERR_ZIP_FORMAT = "Error: Postal Code must contain only digits"
ERR_EMPTY_CART = "Error: Cart is empty"

_ZIP_PATTERN = re.compile(r"^\d{3,10}$")


class CheckoutError(Exception):
    """Se lanza cuando el formulario o el carrito no permiten continuar."""


def validate_buyer(first_name, last_name, postal_code):
    """Valida el formulario en orden secuencial (tabla de decisión R1-R4).

    Un campo con solo espacios se considera vacío. El formato del código
    postal (solo dígitos) es el supuesto AMB-03: la aplicación real acepta
    letras, lo que se registró como defecto DEF-06.
    """
    if not (first_name or "").strip():
        raise CheckoutError(ERR_FIRST)
    if not (last_name or "").strip():
        raise CheckoutError(ERR_LAST)
    if not (postal_code or "").strip():
        raise CheckoutError(ERR_ZIP)
    if not _ZIP_PATTERN.match(postal_code.strip()):
        raise CheckoutError(ERR_ZIP_FORMAT)
    return True


def start_checkout(cart):
    """Supuesto AMB-04: no se puede iniciar el pago con el carrito vacío."""
    if cart.is_empty():
        raise CheckoutError(ERR_EMPTY_CART)
    return True


def item_total(product_ids):
    return sum((catalog.price(p) for p in product_ids), Decimal("0.00"))


def tax(amount):
    return (amount * TAX_RATE).quantize(CENT, rounding=ROUND_HALF_UP)


def summary(product_ids):
    """Devuelve (item_total, tax, total) como en «Checkout: Overview»."""
    subtotal = item_total(product_ids)
    t = tax(subtotal)
    return subtotal, t, subtotal + t
