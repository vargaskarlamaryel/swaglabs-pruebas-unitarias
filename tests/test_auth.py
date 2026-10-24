"""RF-01 Inicio de sesión y RF-07 Control de acceso."""
import pytest

from swaglabs import auth


def test_cp001_login_standard_user_crea_sesion():
    session = auth.login("standard_user", "secret_sauce")
    assert session.username == "standard_user" and session.active


@pytest.mark.parametrize("user", ["problem_user", "performance_glitch_user", "error_user", "visual_user"])
def test_cp001_login_otros_usuarios_validos(user):
    assert auth.login(user, "secret_sauce").username == user


def test_cp002_username_vacio():
    with pytest.raises(auth.LoginError, match="Username is required"):
        auth.login("", "secret_sauce")


def test_password_vacia():
    with pytest.raises(auth.LoginError, match="Password is required"):
        auth.login("standard_user", "")


def test_cp003_password_incorrecta():
    with pytest.raises(auth.LoginError) as exc:
        auth.login("standard_user", "contraseña_errada")
    assert str(exc.value) == auth.MSG_NO_MATCH


def test_usuario_no_registrado():
    with pytest.raises(auth.LoginError, match="do not match"):
        auth.login("usuario_inventado", "secret_sauce")


def test_cp004_usuario_bloqueado():
    with pytest.raises(auth.LoginError) as exc:
        auth.login("locked_out_user", "secret_sauce")
    assert str(exc.value) == auth.MSG_LOCKED


def test_cp020_inventory_sin_sesion_redirige_al_login():
    page, message = auth.access("/inventory.html")
    assert page == "/"
    assert message == "Epic sadface: You can only access '/inventory.html' when you are logged in."


def test_cp020_inventory_despues_de_logout_redirige():
    session = auth.login("standard_user", "secret_sauce")
    session.logout()
    assert auth.access("/inventory.html", session)[0] == "/"


def test_inventory_con_sesion_activa_permite_acceso():
    session = auth.login("standard_user", "secret_sauce")
    assert auth.access("/inventory.html", session) == ("/inventory.html", None)
