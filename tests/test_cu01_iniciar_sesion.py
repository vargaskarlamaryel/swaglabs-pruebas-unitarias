"""Pruebas unitarias del caso de uso CU-01 Iniciar sesión.

Cada prueba indica en su nombre el flujo del caso de uso que verifica:
FP = flujo principal, FA = flujo alternativo, FE = flujo de excepción.
"""
import pytest

from swaglabs import auth

CONTRASENA = "secret_sauce"


# ---------- Flujo principal ----------

def test_cu01_fp_login_valido_crea_sesion_activa():
    """FP: un usuario registrado con su contraseña obtiene una sesión activa."""
    sesion = auth.login("standard_user", CONTRASENA)
    assert sesion.username == "standard_user"
    assert sesion.active is True


def test_cu01_fp_con_sesion_activa_accede_al_catalogo():
    """FP paso 4: con sesión activa, /inventory.html se muestra sin error."""
    sesion = auth.login("standard_user", CONTRASENA)
    assert auth.access("/inventory.html", sesion) == ("/inventory.html", None)


# ---------- Flujos alternativos ----------

@pytest.mark.parametrize("usuario", [
    "problem_user", "performance_glitch_user", "error_user", "visual_user",
])
def test_cu01_fa01_otros_usuarios_validos_inician_sesion(usuario):
    """FA-01: los demás usuarios de la lista también pueden iniciar sesión."""
    assert auth.login(usuario, CONTRASENA).username == usuario


def test_cu01_fa02_logout_cierra_la_sesion():
    """FA-02: al pulsar Logout la sesión deja de estar activa."""
    sesion = auth.login("standard_user", CONTRASENA)
    sesion.logout()
    assert sesion.active is False


def test_cu01_fa03_pagina_publica_no_requiere_sesion():
    """FA-03: la página de login ("/") se puede abrir sin sesión."""
    assert auth.access("/") == ("/", None)


# ---------- Flujos de excepción ----------

def test_cu01_fe01_usuario_vacio():
    """FE-01: sin usuario, el sistema muestra «Username is required»."""
    with pytest.raises(auth.LoginError) as error:
        auth.login("", CONTRASENA)
    assert str(error.value) == "Epic sadface: Username is required"


def test_cu01_fe02_contrasena_vacia():
    """FE-02: sin contraseña, el sistema muestra «Password is required»."""
    with pytest.raises(auth.LoginError) as error:
        auth.login("standard_user", "")
    assert str(error.value) == "Epic sadface: Password is required"


def test_cu01_fe01_ambos_campos_vacios_valida_primero_el_usuario():
    """FE-01: con los dos campos vacíos se informa primero el usuario."""
    with pytest.raises(auth.LoginError, match="Username is required"):
        auth.login("", "")


@pytest.mark.parametrize("usuario, contrasena", [
    ("standard_user", "contraseña_errada"),   # contraseña incorrecta
    ("usuario_inventado", CONTRASENA),         # usuario no registrado
    ("Standard_User", CONTRASENA),             # distingue mayúsculas
])
def test_cu01_fe03_credenciales_no_coinciden(usuario, contrasena):
    """FE-03: usuario o contraseña incorrectos producen el mismo mensaje."""
    with pytest.raises(auth.LoginError) as error:
        auth.login(usuario, contrasena)
    assert str(error.value) == (
        "Epic sadface: Username and password do not match any user in this service"
    )


def test_cu01_fe04_usuario_bloqueado():
    """FE-04: locked_out_user tiene credenciales correctas pero está bloqueado."""
    with pytest.raises(auth.LoginError) as error:
        auth.login("locked_out_user", CONTRASENA)
    assert str(error.value) == "Epic sadface: Sorry, this user has been locked out."


@pytest.mark.parametrize("pagina", auth.PROTECTED_PAGES)
def test_cu01_fe05_pagina_protegida_sin_sesion_redirige_al_login(pagina):
    """FE-05: sin sesión, toda página protegida redirige al login con aviso."""
    destino, mensaje = auth.access(pagina)
    assert destino == "/"
    assert mensaje == f"Epic sadface: You can only access '{pagina}' when you are logged in."


def test_cu01_fe05_despues_de_logout_no_se_accede_al_catalogo():
    """FE-05: tras cerrar sesión, pegar /inventory.html vuelve al login."""
    sesion = auth.login("standard_user", CONTRASENA)
    sesion.logout()
    assert auth.access("/inventory.html", sesion)[0] == "/"
