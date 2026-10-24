"""RF-06 Confirmación de la compra: transición de estados (CP-016 a CP-019)."""
import pytest

from swaglabs import order as o


@pytest.fixture
def flow():
    f = o.PurchaseFlow()
    f.login_ok()
    return f


def test_login_lleva_a_vacio(flow):
    assert flow.state == o.VACIO


def test_agregar_y_eliminar_ultimo_producto(flow):
    flow.add("sauce-labs-backpack")
    assert flow.state == o.CON_PRODUCTOS
    flow.remove("sauce-labs-backpack")
    assert flow.state == o.VACIO


def test_cp007_checkout_desde_vacio_no_permitido(flow):
    with pytest.raises(o.TransitionError):
        flow.checkout()


def test_cp016_cancelar_vuelve_al_carrito_con_productos(flow):
    flow.add("sauce-labs-backpack")
    flow.checkout()
    flow.cancel()
    assert flow.state == o.CON_PRODUCTOS and flow.cart.count == 1


def test_cp017_finish_y_back_home(flow):
    flow.add("sauce-labs-backpack")
    flow.checkout()
    flow.continue_to_overview("Ana", "Pérez", "10147")
    flow.finish()
    assert flow.state == o.COMPLETADO and flow.cart.is_empty()
    flow.back_home()
    assert flow.state == o.VACIO and len(flow.orders) == 1


def test_finish_sin_revisar_resumen_no_permitido(flow):
    flow.add("sauce-labs-backpack")
    flow.checkout()
    with pytest.raises(o.TransitionError):
        flow.finish()


def test_cp018_boton_atras_tras_completar_no_permite_recomprar(flow):
    flow.add("sauce-labs-backpack")
    flow.checkout()
    flow.continue_to_overview("Ana", "Pérez", "10147")
    flow.finish()
    with pytest.raises(o.TransitionError):
        flow.browser_back()
    with pytest.raises(o.TransitionError):
        flow.finish()
    assert len(flow.orders) == 1


def test_cp019_carrito_cambia_despues_del_resumen_no_confirma(flow):
    flow.add("sauce-labs-backpack")
    flow.checkout()
    flow.continue_to_overview("Ana", "Pérez", "10147")
    flow.add("sauce-labs-bike-light")  # simulación de la otra pestaña
    with pytest.raises(o.TransitionError, match="cambió"):
        flow.finish()
    assert flow.orders == []


def test_login_dos_veces_no_permitido(flow):
    with pytest.raises(o.TransitionError):
        flow.login_ok()
