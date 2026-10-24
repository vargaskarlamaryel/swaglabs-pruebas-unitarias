"""Carrito de compras (RF-03). Una unidad por producto, máximo 6 productos."""

from . import catalog


class Cart:
    def __init__(self):
        self._items = []

    def add(self, product_id):
        catalog.price(product_id)  # valida que el producto exista
        if product_id in self._items:
            raise ValueError("El producto ya está en el carrito")
        self._items.append(product_id)

    def remove(self, product_id):
        if product_id not in self._items:
            raise ValueError("El producto no está en el carrito")
        self._items.remove(product_id)

    def clear(self):
        self._items.clear()

    @property
    def items(self):
        return list(self._items)

    @property
    def count(self):
        return len(self._items)

    @property
    def badge(self):
        """Número del ícono del carrito; vacío no muestra número."""
        return str(self.count) if self.count else ""

    def is_empty(self):
        return self.count == 0
