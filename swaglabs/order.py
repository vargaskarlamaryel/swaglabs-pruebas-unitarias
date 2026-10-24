"""Máquina de estados del flujo de compra (RF-06, transición de estados)."""

from .cart import Cart
from .checkout import CheckoutError, start_checkout, summary, validate_buyer

SIN_SESION = "SIN_SESION"
VACIO = "VACIO"
CON_PRODUCTOS = "CON_PRODUCTOS"
EN_CHECKOUT = "EN_CHECKOUT"
COMPLETADO = "COMPLETADO"


class TransitionError(Exception):
    """Se lanza ante una transición no permitida."""


class PurchaseFlow:
    def __init__(self):
        self.state = SIN_SESION
        self.cart = Cart()
        self.orders = []
        self._reviewed_items = None

    def _require(self, *states):
        if self.state not in states:
            raise TransitionError(f"Transición no permitida desde {self.state}")

    def _refresh(self):
        if self.state in (VACIO, CON_PRODUCTOS):
            self.state = CON_PRODUCTOS if self.cart.count else VACIO

    def login_ok(self):
        self._require(SIN_SESION)
        self.state = VACIO

    def add(self, product_id):
        self._require(VACIO, CON_PRODUCTOS, EN_CHECKOUT)
        self.cart.add(product_id)
        self._refresh()

    def remove(self, product_id):
        self._require(CON_PRODUCTOS, EN_CHECKOUT)
        self.cart.remove(product_id)
        self._refresh()

    def checkout(self):
        self._require(VACIO, CON_PRODUCTOS)
        try:
            start_checkout(self.cart)
        except CheckoutError as exc:
            raise TransitionError(str(exc)) from exc
        self.state = EN_CHECKOUT

    def continue_to_overview(self, first, last, postal_code):
        self._require(EN_CHECKOUT)
        validate_buyer(first, last, postal_code)
        self._reviewed_items = self.cart.items
        return summary(self._reviewed_items)

    def cancel(self):
        self._require(EN_CHECKOUT)
        self._reviewed_items = None
        self.state = CON_PRODUCTOS

    def finish(self):
        """Confirma solo lo que el usuario vio en el resumen (supuesto AMB-07)."""
        self._require(EN_CHECKOUT)
        if self._reviewed_items is None:
            raise TransitionError("Debe revisar el resumen antes de confirmar")
        if self.cart.items != self._reviewed_items:
            raise TransitionError("El carrito cambió después del resumen")
        self.orders.append(self._reviewed_items)
        self.cart.clear()
        self._reviewed_items = None
        self.state = COMPLETADO

    def back_home(self):
        self._require(COMPLETADO)
        self.state = VACIO

    def browser_back(self):
        """Supuesto AMB-06: tras completar no se puede volver a confirmar."""
        if self.state == COMPLETADO:
            raise TransitionError("La orden ya fue completada")
