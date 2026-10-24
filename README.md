# Pruebas unitarias – Swag Labs

Proyecto académico de **TI3312 – Aseguramiento de la Calidad del Software** (UNIBE).
Autora: Karla Vargas (25-0484) · Docente: Lorenzo Martínez

## Qué contiene

Swag Labs (https://www.saucedemo.com/) es una aplicación web cuyo código fuente no es público.
Por eso este repositorio **modela en Python las reglas de negocio** observadas en los laboratorios
y las verifica con **pruebas unitarias en pytest**. Cada prueba lleva en su nombre el caso
de la suite del Laboratorio 03 que respalda (por ejemplo, `test_cp008_un_producto`).

```
swaglabs/
  auth.py       RF-01 Inicio de sesión · RF-07 Control de acceso
  catalog.py    RF-02 Catálogo y ordenamiento
  cart.py       RF-03 Carrito
  checkout.py   RF-04 Datos del comprador · RF-05 Impuesto y total
  order.py      RF-06 Confirmación (máquina de estados)
tests/
  test_auth.py · test_catalog.py · test_checkout.py · test_order.py
```

## Cómo ejecutar

Requiere Python 3.9 o superior.

```bash
pip install -r requirements.txt
python -m pytest -v
```

Resultado esperado: **50 passed**.

## Relación con la suite de casos (Laboratorio 03)

| Técnica | Casos | Pruebas unitarias |
| --- | --- | --- |
| Partición de equivalencia | CP-001 a CP-006 | test_auth.py, test_catalog.py, test_cp005_* |
| Valores límite | CP-007 a CP-011 | test_cp007_* a test_cp011_* |
| Tabla de decisión | CP-012 a CP-015 | test_cp012_* a test_cp015_* |
| Transición de estados | CP-016 a CP-020 | test_order.py, test_cp020_* |

## Supuestos del modelo

El modelo implementa los supuestos del registro de ambigüedades. Donde la aplicación real
se comporta distinto, la diferencia es un defecto ya registrado:

| Supuesto | Modelo | Aplicación real |
| --- | --- | --- |
| AMB-03 Formato del código postal | Solo dígitos | Acepta letras (defecto DEF-06) |
| AMB-04 Checkout con carrito vacío | Lo impide | Por verificar (CP-007) |
| AMB-05 Impuesto | 8 % redondeado a 2 decimales | Coincide con lo observado |
| AMB-06 Botón «atrás» tras comprar | No permite recomprar | Por verificar (CP-018) |
| AMB-07 Carrito cambiado en otra pestaña | No confirma | Por verificar (CP-019) |
