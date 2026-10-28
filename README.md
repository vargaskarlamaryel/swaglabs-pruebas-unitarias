# Pruebas unitarias – Swag Labs

Proyecto académico de **TI3312 – Aseguramiento de la Calidad del Software** (UNIBE).
Autora: Karla Vargas (25-0484) · Docente: Lorenzo Martínez

Este repositorio contiene **57 pruebas unitarias en pytest** para dos casos de uso del
caso de estudio Swag Labs (https://www.saucedemo.com/): **CU-01 Iniciar sesión** y
**CU-02 Realizar compra**. Las pruebas cubren el flujo principal, los flujos alternativos
y los flujos de excepción de cada caso de uso, y alcanzan **100 % de cobertura** de líneas
y de ramas del código.

## 1. Cómo ejecutar las pruebas

Requisitos: Python 3.9 o superior.

```bash
# 1. Instalar las dependencias (pytest y pytest-cov)
pip install -r requirements.txt

# 2. Ejecutar todas las pruebas
python -m pytest

# 3. Ejecutar las pruebas con el reporte de cobertura
python -m pytest --cov --cov-report=term-missing

# 4. (Opcional) Reporte de cobertura en HTML: se abre htmlcov/index.html en el navegador
python -m pytest --cov --cov-report=html

# Ejecutar solo un caso de uso
python -m pytest tests/test_cu01_iniciar_sesion.py
python -m pytest tests/test_cu02_realizar_compra.py
```

Resultado esperado: `57 passed` y `TOTAL ... 100%`.

## 2. Estructura del proyecto

```
swaglabs/                         Código bajo prueba (reglas de negocio de Swag Labs)
  auth.py                         Inicio de sesión y control de acceso      → CU-01
  catalog.py                      Catálogo y ordenamiento                   → CU-02
  cart.py                         Carrito de compras                        → CU-02
  checkout.py                     Datos del comprador, impuesto y total     → CU-02
  order.py                        Estados del flujo de compra               → CU-02
tests/
  test_cu01_iniciar_sesion.py     21 pruebas del caso de uso CU-01
  test_cu02_realizar_compra.py    36 pruebas del caso de uso CU-02
requirements.txt · pytest.ini · .coveragerc
```

**¿Por qué un modelo en Python?** El código fuente de Swag Labs no es público. Por eso
`swaglabs/` reproduce las reglas de negocio observadas en la aplicación durante los
laboratorios (mensajes de error, impuesto del 8 %, orden de validación, estados de la compra)
y las pruebas unitarias verifican ese modelo.

**Convención de nombres.** Cada prueba indica en su nombre el caso de uso y el flujo que
verifica: `test_cu01_fe04_usuario_bloqueado` prueba el flujo de excepción FE-04 del CU-01.
FP = flujo principal, FA = flujo alternativo, FE = flujo de excepción.

## 3. Caso de uso CU-01: Iniciar sesión

| Elemento | Descripción |
| --- | --- |
| Actor | Comprador |
| Objetivo | Acceder a la tienda con sus credenciales |
| Precondición | El comprador no tiene una sesión iniciada |
| Postcondición | Existe una sesión activa y se muestra el catálogo (/inventory.html) |

**Flujo principal (FP)**

1. El comprador abre https://www.saucedemo.com/.
2. Escribe su usuario y su contraseña.
3. Pulsa «Login» y el sistema valida las credenciales.
4. El sistema crea la sesión y muestra el catálogo.

**Flujos alternativos (FA)**

- **FA-01** Inicia sesión con otro usuario válido (problem_user, performance_glitch_user, error_user o visual_user).
- **FA-02** El comprador pulsa «Logout» y la sesión se cierra.
- **FA-03** El comprador abre la página de login, que no requiere sesión.

**Flujos de excepción (FE)**

- **FE-01** Usuario vacío → «Epic sadface: Username is required».
- **FE-02** Contraseña vacía → «Epic sadface: Password is required».
- **FE-03** Usuario o contraseña incorrectos → «Epic sadface: Username and password do not match any user in this service».
- **FE-04** Usuario bloqueado (locked_out_user) → «Epic sadface: Sorry, this user has been locked out.».
- **FE-05** Acceso a una página protegida sin sesión → redirige al login con «You can only access '...' when you are logged in.».

**Pruebas unitarias del CU-01** (`tests/test_cu01_iniciar_sesion.py`)

| Prueba | Flujo | Propósito |
| --- | --- | --- |
| `test_cu01_fp_login_valido_crea_sesion_activa` | FP | Un usuario registrado con su contraseña obtiene una sesión activa. |
| `test_cu01_fp_con_sesion_activa_accede_al_catalogo` | FP paso 4 | Con sesión activa, /inventory.html se muestra sin error. |
| `test_cu01_fa01_otros_usuarios_validos_inician_sesion` (4 variantes) | FA-01 | Los demás usuarios de la lista también pueden iniciar sesión. |
| `test_cu01_fa02_logout_cierra_la_sesion` | FA-02 | Al pulsar Logout la sesión deja de estar activa. |
| `test_cu01_fa03_pagina_publica_no_requiere_sesion` | FA-03 | La página de login ("/") se puede abrir sin sesión. |
| `test_cu01_fe01_usuario_vacio` | FE-01 | Sin usuario, el sistema muestra «Username is required». |
| `test_cu01_fe02_contrasena_vacia` | FE-02 | Sin contraseña, el sistema muestra «Password is required». |
| `test_cu01_fe01_ambos_campos_vacios_valida_primero_el_usuario` | FE-01 | Con los dos campos vacíos se informa primero el usuario. |
| `test_cu01_fe03_credenciales_no_coinciden` (3 variantes) | FE-03 | Usuario o contraseña incorrectos producen el mismo mensaje. |
| `test_cu01_fe04_usuario_bloqueado` | FE-04 | Locked_out_user tiene credenciales correctas pero está bloqueado. |
| `test_cu01_fe05_pagina_protegida_sin_sesion_redirige_al_login` (una por página protegida) | FE-05 | Sin sesión, toda página protegida redirige al login con aviso. |
| `test_cu01_fe05_despues_de_logout_no_se_accede_al_catalogo` | FE-05 | Tras cerrar sesión, pegar /inventory.html vuelve al login. |

## 4. Caso de uso CU-02: Realizar compra

| Elemento | Descripción |
| --- | --- |
| Actor | Comprador |
| Objetivo | Comprar uno o más productos del catálogo |
| Precondición | El comprador inició sesión (CU-01) y su carrito está vacío |
| Postcondición | La orden queda registrada y el carrito vacío |

**Flujo principal (FP)**

1. El comprador ve el catálogo de 6 productos.
2. Pulsa «Add to cart» en uno o más productos; el ícono del carrito muestra la cantidad.
3. Abre el carrito y pulsa «Checkout».
4. Escribe nombre, apellido y código postal y pulsa «Continue».
5. El sistema valida los datos y muestra el resumen: item total, impuesto (8 %) y total.
6. El comprador pulsa «Finish».
7. El sistema registra la orden, muestra «Thank you for your order!» y vacía el carrito.
8. El comprador pulsa «Back Home» y vuelve al catálogo.

**Flujos alternativos (FA)**

- **FA-01** Ordena el catálogo por nombre (A-Z, Z-A) o por precio (menor a mayor, mayor a menor).
- **FA-02** Elimina un producto del carrito.
- **FA-03** Pulsa «Cancel» en el checkout y vuelve al carrito con sus productos.
- **FA-04** Compra varios productos (valores límite: 1, 2, 5 y 6 productos).
- **FA-05** Usa el botón «atrás» del navegador antes de confirmar.

**Flujos de excepción (FE)**

- **FE-01** Inicia el checkout con el carrito vacío → no avanza (supuesto AMB-04).
- **FE-02** Nombre vacío → «Error: First Name is required».
- **FE-03** Apellido vacío o solo con espacios → «Error: Last Name is required».
- **FE-04** Código postal vacío → «Error: Postal Code is required».
- **FE-05** Código postal con letras o símbolos → error de formato (supuesto AMB-03).
- **FE-06** Agrega un producto repetido o inexistente, o quita uno que no está en el carrito → se rechaza.
- **FE-07** Intenta confirmar sin pasar por el resumen → se rechaza.
- **FE-08** El carrito cambia después del resumen (por ejemplo, desde otra pestaña) → no se confirma (supuesto AMB-07).
- **FE-09** Intenta recomprar una orden ya completada con el botón «atrás» → se rechaza (supuesto AMB-06).
- **FE-10** Acciones fuera de orden u opciones inexistentes (comprar sin sesión, opción de orden inválida) → se rechazan.

**Pruebas unitarias del CU-02** (`tests/test_cu02_realizar_compra.py`)

| Prueba | Flujo | Propósito |
| --- | --- | --- |
| `test_cu02_fp_catalogo_muestra_seis_productos` | FP paso 1 | El catálogo tiene los 6 productos de la tienda. |
| `test_cu02_fp_agregar_producto_actualiza_carrito` | FP paso 2 | Al agregar un producto el carrito pasa a tener 1 y muestra «1». |
| `test_cu02_fp_resumen_calcula_subtotal_impuesto_y_total` | FP paso 5 | El resumen muestra item total, impuesto (8 %) y total. |
| `test_cu02_fp_finish_confirma_orden_y_vacia_carrito` | FP pasos 6-7 | Finish registra la orden y deja el carrito vacío. |
| `test_cu02_fp_back_home_vuelve_al_catalogo_con_carrito_vacio` | FP paso 8 | Back Home lleva al catálogo listo para otra compra. |
| `test_cu02_fa01_ordenar_catalogo_pone_primero_el_producto_correcto` (4 variantes) | FA-01 | Cada opción del filtro coloca primero el producto que corresponde. |
| `test_cu02_fa01_orden_precio_mayor_a_menor_completo` | FA-01 | «Price (high to low)» ordena los 6 precios de mayor a menor. |
| `test_cu02_fa02_eliminar_ultimo_producto_deja_carrito_vacio` | FA-02 | Quitar el único producto devuelve el carrito al estado vacío. |
| `test_cu02_fa03_cancelar_checkout_conserva_los_productos` | FA-03 | Cancel en el checkout vuelve al carrito sin perder productos. |
| `test_cu02_fa04_resumen_en_los_valores_limite_del_carrito` (4 variantes) | FA-04 | El resumen es correcto con 1, 2, 5 y 6 productos (valores límite). |
| `test_cu02_fa04_tres_productos_coincide_con_lo_observado_en_la_app` | FA-04 | Reproduce la compra real del Laboratorio 01 ($95.97 + $7.68 = $103.65). |
| `test_cu02_fa05_boton_atras_antes_de_confirmar_esta_permitido` | FA-05 | Antes de confirmar, volver atrás no altera el carrito ni el estado. |
| `test_cu02_fe01_no_se_puede_iniciar_checkout_con_carrito_vacio` | FE-01 | Con el carrito vacío, Checkout no avanza (supuesto AMB-04). |
| `test_cu02_fe02_a_fe04_datos_obligatorios_del_comprador` (5 variantes) | FE-02 a FE-04 | Cada campo vacío muestra su error, en orden nombre → apellido → código. |
| `test_cu02_fe05_codigo_postal_con_formato_invalido` (4 variantes) | FE-05 | El código postal debe tener solo dígitos (supuesto AMB-03, defecto DEF-06 en la app). |
| `test_cu02_fe06_no_se_agrega_el_mismo_producto_dos_veces` | FE-06 | Cada producto se agrega una sola vez; no existe un séptimo producto distinto. |
| `test_cu02_fe06_producto_inexistente_no_se_agrega` | FE-06 | Un producto que no está en el catálogo se rechaza. |
| `test_cu02_fe06_eliminar_producto_que_no_esta_en_el_carrito` | FE-06 | Quitar algo que no está en el carrito produce un error controlado. |
| `test_cu02_fe07_finish_sin_revisar_el_resumen` | FE-07 | No se puede confirmar sin haber pasado por el resumen. |
| `test_cu02_fe08_carrito_cambia_despues_del_resumen` | FE-08 | Si el carrito cambia tras el resumen (otra pestaña), no se confirma (AMB-07). |
| `test_cu02_fe09_no_se_puede_recomprar_una_orden_completada` | FE-09 | Tras confirmar, el botón atrás y un segundo Finish se rechazan (AMB-06). |
| `test_cu02_fe10_acciones_fuera_de_orden_se_rechazan` | FE-10 | Sin iniciar sesión no se puede comprar, ni iniciar sesión dos veces. |
| `test_cu02_fe10_opcion_de_orden_invalida` | FE-10 | Una opción de orden que no existe en el filtro se rechaza. |

## 5. Cobertura

| Módulo | Líneas | Ramas | Cobertura |
| --- | --- | --- | --- |
| auth.py | 29 | 10 | 100 % |
| cart.py | 26 | 4 | 100 % |
| catalog.py | 20 | 10 | 100 % |
| checkout.py | 34 | 10 | 100 % |
| order.py | 63 | 10 | 100 % |
| **Total** | **172** | **44** | **100 %** |

Resumen por caso de uso:

| Caso de uso | Pruebas | Flujo principal | Flujos alternativos | Flujos de excepción |
| --- | --- | --- | --- | --- |
| CU-01 Iniciar sesión | 21 | Cubierto | FA-01 a FA-03 | FE-01 a FE-05 |
| CU-02 Realizar compra | 36 | Cubierto (pasos 1 a 8) | FA-01 a FA-05 | FE-01 a FE-10 |

## 6. Supuestos y diferencias con la aplicación real

Algunas reglas no están documentadas en Swag Labs. El modelo implementa los supuestos
definidos en el Laboratorio 03; donde la aplicación real se comporta distinto, la diferencia
se registró como defecto.

| Supuesto | Comportamiento del modelo | Aplicación real |
| --- | --- | --- |
| AMB-03 Formato del código postal | Solo dígitos | Acepta letras (defecto DEF-06) |
| AMB-04 Checkout con carrito vacío | Lo impide | Por verificar |
| AMB-05 Impuesto | 8 % redondeado a 2 decimales | Coincide con lo observado |
| AMB-06 Botón «atrás» tras comprar | No permite recomprar | Por verificar |
| AMB-07 Carrito cambiado en otra pestaña | No confirma | Por verificar |
