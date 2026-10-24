"""RF-03 Carrito, RF-04 Datos del comprador y RF-05 Impuesto y total."""
from decimal import Decimal

import pytest

from swaglabs import catalog
from swaglabs.cart import Cart
from swaglabs.checkout import CheckoutError, start_checkout, summary, validate_buyer

D = Decimal


# ---- Tabla de decisión (CP-012 a CP-015) ----

def test_cp012_r1_tres_campos_llenos_avanza():
    assert validate_buyer("Ana", "Pérez", "10147") is True


def test_cp013_r2_zip_vacio():
    with pytest.raises(CheckoutError, match="Postal Code is required"):
        validate_buyer("Ana", "Pérez", "")


def test_cp014_r3_last_name_vacio():
    with pytest.raises(CheckoutError, match="Last Name is required"):
        validate_buyer("Ana", "", "10147")


def test_cp014_r3_last_name_vacio_y_zip_vacio_muestra_error_de_last_name():
    with pytest.raises(CheckoutError, match="Last Name is required"):
        validate_buyer("Ana", "", "")


@pytest.mark.parametrize("last, zip_code", [("Pérez", "10147"), ("", "10147"), ("Pérez", ""), ("", "")])
def test_cp015_r4_first_name_vacio_siempre_muestra_error_de_first_name(last, zip_code):
    with pytest.raises(CheckoutError, match="First Name is required"):
        validate_buyer("", last, zip_code)


def test_apellido_con_solo_espacios_se_rechaza():
    with pytest.raises(CheckoutError, match="Last Name is required"):
        validate_buyer("Ana", "   ", "10147")


# ---- Partición: formato del código postal (CP-005, supuesto AMB-03) ----

@pytest.mark.parametrize("zip_code", ["ABC", "10A47", "10-147"])
def test_cp005_codigo_postal_con_letras_o_simbolos_se_rechaza(zip_code):
    with pytest.raises(CheckoutError, match="only digits"):
        validate_buyer("Ana", "Pérez", zip_code)


# ---- Valores límite del carrito (CP-007 a CP-011) ----

def test_cp007_no_se_puede_iniciar_checkout_con_carrito_vacio():
    cart = Cart()
    cart.add("sauce-labs-backpack")
    cart.remove("sauce-labs-backpack")
    with pytest.raises(CheckoutError, match="Cart is empty"):
        start_checkout(cart)


def test_cp008_un_producto():
    assert summary(["sauce-labs-backpack"]) == (D("29.99"), D("2.40"), D("32.39"))


def test_cp009_dos_productos():
    items = ["sauce-labs-backpack", "sauce-labs-bike-light"]
    assert summary(items) == (D("39.98"), D("3.20"), D("43.18"))


def test_cp010_cinco_productos():
    items = [p for p in catalog.PRODUCTS if p != "sauce-labs-onesie"]
    assert summary(items) == (D("121.95"), D("9.76"), D("131.71"))


def test_cp011_seis_productos():
    assert summary(list(catalog.PRODUCTS)) == (D("129.94"), D("10.40"), D("140.34"))


def test_lab01_tres_productos_coincide_con_lo_observado():
    items = ["sauce-labs-backpack", "sauce-labs-bolt-t-shirt", "sauce-labs-fleece-jacket"]
    assert summary(items) == (D("95.97"), D("7.68"), D("103.65"))


def test_carrito_no_admite_siete_productos_distintos():
    cart = Cart()
    for p in catalog.PRODUCTS:
        cart.add(p)
    assert cart.count == 6
    with pytest.raises(ValueError):
        cart.add("sauce-labs-backpack")


def test_contador_del_carrito():
    cart = Cart()
    assert cart.badge == ""
    cart.add("sauce-labs-backpack")
    assert cart.badge == "1"
