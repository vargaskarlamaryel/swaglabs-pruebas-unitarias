"""Inicio de sesión y control de acceso (RF-01, RF-07)."""

PASSWORD = "secret_sauce"
USERS = (
    "standard_user",
    "locked_out_user",
    "problem_user",
    "performance_glitch_user",
    "error_user",
    "visual_user",
)

MSG_USER_REQUIRED = "Epic sadface: Username is required"
MSG_PASSWORD_REQUIRED = "Epic sadface: Password is required"
MSG_NO_MATCH = "Epic sadface: Username and password do not match any user in this service"
MSG_LOCKED = "Epic sadface: Sorry, this user has been locked out."
MSG_NO_SESSION = "Epic sadface: You can only access '{page}' when you are logged in."

PROTECTED_PAGES = (
    "/inventory.html",
    "/cart.html",
    "/checkout-step-one.html",
    "/checkout-step-two.html",
    "/checkout-complete.html",
)


class LoginError(Exception):
    """Se lanza cuando el inicio de sesión es rechazado."""


class Session:
    """Sesión autenticada de un usuario."""

    def __init__(self, username):
        self.username = username
        self.active = True

    def logout(self):
        self.active = False


def login(username, password):
    """Valida las credenciales y devuelve una Session.

    El orden de validación es el que muestra la aplicación:
    usuario vacío, contraseña vacía, credenciales, usuario bloqueado.
    """
    if not username:
        raise LoginError(MSG_USER_REQUIRED)
    if not password:
        raise LoginError(MSG_PASSWORD_REQUIRED)
    if username not in USERS or password != PASSWORD:
        raise LoginError(MSG_NO_MATCH)
    if username == "locked_out_user":
        raise LoginError(MSG_LOCKED)
    return Session(username)


def access(page, session=None):
    """Devuelve la página a la que llega el usuario y el mensaje mostrado.

    Sin sesión activa, una página protegida redirige al login ("/").
    """
    if page in PROTECTED_PAGES and (session is None or not session.active):
        return "/", MSG_NO_SESSION.format(page=page)
    return page, None
