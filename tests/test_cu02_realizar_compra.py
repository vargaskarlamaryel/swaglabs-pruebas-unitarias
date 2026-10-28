"""Pruebas unitarias del caso de uso CU-02 Realizar compra.

Cada prueba indica en su nombre el flujo del caso de uso que verifica:
FP = flujo principal, FA = flujo alternativo, FE = flujo de excepción.
"""
from decimal import Decimal as D

import pytest

from swaglabs import catalog
from swaglabs import order as o
from swaglabs.cart import Cart
from swaglabs.checkout import CheckoutError, summary, validate_buyer

MOCHILA = "sauce-labs-backpack"
LUZ = "sauce-labs-bike-light"


@pytest.fixture
def compra():
    """Flujo de compra con sesión iniciada y carrito vacío (precondición de CU-02)."""
    flujo = o.PurchaseFlow()
    flujo.login_ok()
    return flujo


def llegar_al_resumen(flujo, productos=(MOCHILA,)):
    for p in productos:
        flujo.add(p)
    flujo.checkout()
    return flujo.continue_to_overview("Ana", "Pérez", "10147")


# ---------- Flujo principal ----------

def test_cu02_fp_catalogo_muestra_seis_productos():
    """FP paso 1: el catálogo tiene los 6 productos de la tienda."""
    assert len(catalog.PRODUCTS) == 6


def test_cu02_fp_agregar_producto_actualiza_carrito(compra):
    """FP paso 2: al agregar un producto el carrito pasa a tener 1 y muestra «1»."""
    compra.add(MOCHILA)
    assert compra.state == o.CON_PRODUCTOS
    assert compra.cart.badge == "1"


def test_cu02_fp_resumen_calcula_subtotal_impuesto_y_total(compra):
    """FP paso 5: el resumen muestra item total, impuesto (8 %) y total."""
    assert llegar_al_resumen(compra) == (D("29.99"), D("2.40"), D("32.39"))


def test_cu02_fp_finish_confirma_orden_y_vacia_carrito(compra):
    """FP pasos 6-7: Finish registra la orden y deja el carrito vacío."""
    llegar_al_resumen(compra)
    compra.finish()
    assert compra.state == o.COMPLETADO
    assert compra.cart.is_empty()
    assert compra.orders == [[MOCHILA]]


def test_cu02_fp_back_home_vuelve_al_catalogo_con_carrito_vacio(compra):
    """FP paso 8: Back Home lleva al catálogo listo para otra compra."""
    llegar_al_resumen(compra)
    compra.finish()
    compra.back_home()
    assert compra.state == o.VACIO


# ---------- Flujos alternativos ----------

@pytest.mark.parametrize("opcion, esperado", [
    ("az", "Sauce Labs Backpack"),
    ("za", "Test.allTheThings() T-Shirt (Red)"),
    ("lohi", "Sauce Labs Onesie"),
    ("hilo", "Sauce Labs Fleece Jacket"),
])
def test_cu02_fa01_ordenar_catalogo_pone_primero_el_producto_correcto(opcion, esperado):
    """FA-01: cada opción del filtro coloca primero el producto que corresponde."""
    assert catalog.name(catalog.sorted_products(opcion)[0]) == esperado


def test_cu02_fa01_orden_precio_mayor_a_menor_completo():
    """FA-01: «Price (high to low)» ordena los 6 precios de mayor a menor."""
    precios = [str(catalog.price(p)) for p in catalog.sorted_products("hilo")]
    assert precios == ["49.99", "29.99", "15.99", "15.99", "9.99", "7.99"]


def test_cu02_fa02_eliminar_ultimo_producto_deja_carrito_vacio(compra):
    """FA-02: quitar el único producto devuelve el carrito al estado vacío."""
    compra.add(MOCHILA)
    compra.remove(MOCHILA)
    assert compra.state == o.VACIO
    assert compra.cart.badge == ""


def test_cu02_fa03_cancelar_checkout_conserva_los_productos(compra):
    """FA-03: Cancel en el checkout vuelve al carrito sin perder productos."""
    compra.add(MOCHILA)
    compra.checkout()
    compra.cancel()
    assert compra.state == o.CON_PRODUCTOS
    assert compra.cart.items == [MOCHILA]


@pytest.mark.parametrize("cantidad, subtotal, impuesto, total", [
    (1, "29.99", "2.40", "32.39"),     # límite inferior
    (2, "39.98", "3.20", "43.18"),     # límite inferior + 1
    (5, "121.95", "9.76", "131.71"),   # límite superior - 1
    (6, "129.94", "10.40", "140.34"),  # límite superior
])
def test_cu02_fa04_resumen_en_los_valores_limite_del_carrito(cantidad, subtotal, impuesto, total):
    """FA-04: el resumen es correcto con 1, 2, 5 y 6 productos (valores límite)."""
    seleccion = {
        1: [MOCHILA],
        2: [MOCHILA, LUZ],
        5: [p for p in catalog.PRODUCTS if p != "sauce-labs-onesie"],
        6: list(catalog.PRODUCTS),
    }[cantidad]
    assert summary(seleccion) == (D(subtotal), D(impuesto), D(total))


def test_cu02_fa04_tres_productos_coincide_con_lo_observado_en_la_app():
    """FA-04: reproduce la compra real del Laboratorio 01 ($95.97 + $7.68 = $103.65)."""
    seleccion = [MOCHILA, "sauce-labs-bolt-t-shirt", "sauce-labs-fleece-jacket"]
    assert summary(seleccion) == (D("95.97"), D("7.68"), D("103.65"))


def test_cu02_fa05_boton_atras_antes_de_confirmar_esta_permitido(compra):
    """FA-05: antes de confirmar, volver atrás no altera el carrito ni el estado."""
    compra.add(MOCHILA)
    compra.browser_back()
    assert compra.state == o.CON_PRODUCTOS
    assert compra.cart.items == [MOCHILA]


# ---------- Flujos de excepción ----------

def test_cu02_fe01_no_se_puede_iniciar_checkout_con_carrito_vacio(compra):
    """FE-01: con el carrito vacío, Checkout no avanza (supuesto AMB-04)."""
    with pytest.raises(o.TransitionError, match="Cart is empty"):
        compra.checkout()


@pytest.mark.parametrize("nombre, apellido, codigo, mensaje", [
    ("", "Pérez", "10147", "First Name is required"),   # FE-02
    ("", "", "", "First Name is required"),              # FE-02: se valida primero
    ("Ana", "", "10147", "Last Name is required"),       # FE-03
    ("Ana", "   ", "10147", "Last Name is required"),    # FE-03: solo espacios
    ("Ana", "Pérez", "", "Postal Code is required"),     # FE-04
])
def test_cu02_fe02_a_fe04_datos_obligatorios_del_comprador(nombre, apellido, codigo, mensaje):
    """FE-02 a FE-04: cada campo vacío muestra su error, en orden nombre → apellido → código."""
    with pytest.raises(CheckoutError, match=mensaje):
        validate_buyer(nombre, apellido, codigo)


@pytest.mark.parametrize("codigo", ["ABC", "10A47", "10-147", "12"])
def test_cu02_fe05_codigo_postal_con_formato_invalido(codigo):
    """FE-05: el código postal debe tener solo dígitos (supuesto AMB-03, defecto DEF-06 en la app)."""
    with pytest.raises(CheckoutError, match="only digits"):
        validate_buyer("Ana", "Pérez", codigo)


def test_cu02_fe06_no_se_agrega_el_mismo_producto_dos_veces():
    """FE-06: cada producto se agrega una sola vez; no existe un séptimo producto distinto."""
    carrito = Cart()
    for p in catalog.PRODUCTS:
        carrito.add(p)
    with pytest.raises(ValueError):
        carrito.add(MOCHILA)
    assert carrito.count == 6


def test_cu02_fe06_producto_inexistente_no_se_agrega():
    """FE-06: un producto que no está en el catálogo se rechaza."""
    with pytest.raises(KeyError):
        Cart().add("producto-inexistente")


def test_cu02_fe06_eliminar_producto_que_no_esta_en_el_carrito():
    """FE-06: quitar algo que no está en el carrito produce un error controlado."""
    with pytest.raises(ValueError):
        Cart().remove(MOCHILA)


def test_cu02_fe07_finish_sin_revisar_el_resumen(compra):
    """FE-07: no se puede confirmar sin haber pasado por el resumen."""
    compra.add(MOCHILA)
    compra.checkout()
    with pytest.raises(o.TransitionError, match="revisar el resumen"):
        compra.finish()


def test_cu02_fe08_carrito_cambia_despues_del_resumen(compra):
    """FE-08: si el carrito cambia tras el resumen (otra pestaña), no se confirma (AMB-07)."""
    llegar_al_resumen(compra)
    compra.add(LUZ)
    with pytest.raises(o.TransitionError, match="cambió"):
        compra.finish()
    assert compra.orders == []


def test_cu02_fe09_no_se_puede_recomprar_una_orden_completada(compra):
    """FE-09: tras confirmar, el botón atrás y un segundo Finish se rechazan (AMB-06)."""
    llegar_al_resumen(compra)
    compra.finish()
    with pytest.raises(o.TransitionError):
        compra.browser_back()
    with pytest.raises(o.TransitionError):
        compra.finish()
    assert len(compra.orders) == 1


def test_cu02_fe10_acciones_fuera_de_orden_se_rechazan():
    """FE-10: sin iniciar sesión no se puede comprar, ni iniciar sesión dos veces."""
    flujo = o.PurchaseFlow()
    with pytest.raises(o.TransitionError):
        flujo.add(MOCHILA)
    flujo.login_ok()
    with pytest.raises(o.TransitionError):
        flujo.login_ok()


def test_cu02_fe10_opcion_de_orden_invalida():
    """FE-10: una opción de orden que no existe en el filtro se rechaza."""
    with pytest.raises(ValueError):
        catalog.sorted_products("precio")
