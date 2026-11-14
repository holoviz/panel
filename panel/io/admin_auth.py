"""
Access control for the admin panel, shared by the Tornado and ASGI servers.

Two independent checks apply. ``config.admin_users`` restricts the admin
panel to users authenticated by the server's auth provider, while
``config.admin_password`` requires a password entered on the admin panel's
own login page and therefore also works without server authentication.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
import typing as t

from http.cookies import SimpleCookie

from ..config import config
from .resources import CDN_DIST, _env

if t.TYPE_CHECKING:
    from bokeh.application import Application

ADMIN_COOKIE = 'panel_admin'

LOGIN_ENDPOINT = 'login'

LOGOUT_ENDPOINT = 'logout'

INVALID_PASSWORD = 'Invalid password!'

ADMIN_LOGIN_TEMPLATE = _env.get_template('admin_login.html')

# Signs the admin cookie when no cookie secret is configured, so the cookie
# cannot be forged, at the cost of logging admins out on restart.
_PROCESS_SECRET = secrets.token_bytes(32)


class AdminAccess(t.NamedTuple):
    """
    Outcome of checking a request against the admin access configuration.
    """

    allowed: bool
    login: bool = False
    error: str | None = None


def mark_admin_application(app: Application) -> Application:
    """
    Marks an application as the admin panel, the servers enforce the admin
    access configuration on its routes.
    """
    app._panel_admin = True  # type: ignore[attr-defined]
    return app


def is_admin_application(app: t.Any) -> bool:
    return bool(getattr(app, '_panel_admin', False))


def admin_protected() -> bool:
    return bool(config.admin_password or config.admin_users)


def _signature(issued: str) -> str:
    secret = config.cookie_secret
    key = secret.encode('utf-8') if secret else _PROCESS_SECRET
    # Binding the password invalidates issued cookies when it changes.
    password = hashlib.sha256((config.admin_password or '').encode('utf-8')).hexdigest()
    return hmac.new(key, f'{issued}:{password}'.encode(), hashlib.sha256).hexdigest()


def create_admin_token(now: float | None = None) -> str:
    issued = str(int(time.time() if now is None else now))
    return f'{issued}.{_signature(issued)}'


def validate_admin_token(token: str | None) -> bool:
    if not token:
        return False
    issued, _, signature = token.partition('.')
    if not issued.isdigit() or not hmac.compare_digest(signature, _signature(issued)):
        return False
    return time.time() - int(issued) < config.oauth_expiry * 86400


def validate_admin_password(password: str) -> bool:
    expected = config.admin_password
    if not expected:
        return False
    return hmac.compare_digest(password.encode('utf-8'), expected.encode('utf-8'))


def check_admin_access(user: str | None, token: str | None) -> AdminAccess:
    """
    Checks whether a request may access the admin panel.

    Parameters
    ----------
    user: str | None
        The user authenticated by the server's auth provider.
    token: str | None
        The value of the admin cookie.
    """
    users = config.admin_users
    if users and user not in users:
        return AdminAccess(
            False, error=f'User {user!r} is not authorized to access the admin panel.'
        )
    if config.admin_password and not validate_admin_token(token):
        return AdminAccess(False, login=True)
    return AdminAccess(True)


def relative_endpoint(path: str, endpoint: str) -> str:
    """
    The URL of an admin endpoint relative to the admin document at ``path``,
    which keeps redirects working behind proxies that rewrite the prefix.
    """
    if path.endswith('/'):
        return endpoint
    return f"{path.rsplit('/', 1)[-1]}/{endpoint}"


def admin_document_url(login_path: str) -> str:
    """
    The URL of the admin document relative to its login page at
    ``login_path``. It omits the trailing slash, under which the document's
    relative resource URLs would not resolve.
    """
    segments = login_path.rstrip('/').split('/')
    return f'../{segments[-2]}' if len(segments) > 2 else '/'


def admin_cookie(token: str | None, secure: bool = False) -> str:
    """
    The ``Set-Cookie`` header value storing ``token``, or clearing the
    cookie if it is None. The path is left to the browser, which scopes the
    cookie to the admin endpoint the login page is served under.
    """
    cookie: SimpleCookie = SimpleCookie()
    cookie[ADMIN_COOKIE] = token or ''
    morsel = cookie[ADMIN_COOKIE]
    morsel['httponly'] = True
    morsel['samesite'] = 'Lax'
    if secure:
        morsel['secure'] = True
    if token is None:
        morsel['max-age'] = 0
    else:
        morsel['max-age'] = int(config.oauth_expiry * 86400)
    return morsel.OutputString()


def render_admin_login(error: str = '') -> str:
    return ADMIN_LOGIN_TEMPLATE.render(
        login_endpoint=LOGIN_ENDPOINT, errormessage=error, PANEL_CDN=CDN_DIST
    )
