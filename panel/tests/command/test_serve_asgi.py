"""
In-process tests for the ``panel serve --server asgi|fastapi`` argument
handling. The subprocess based tests in ``test_serve.py`` can only observe
the running server, so the mapping from commandline arguments onto the ASGI
application and the uvicorn configuration is asserted here instead.
"""
import argparse

import pytest

pytest.importorskip('uvicorn')

import uvicorn

from bokeh.server.tornado import DEFAULT_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES

from panel.command import serve as serve_module
from panel.command.serve import Serve
from panel.config import config
from panel.io.asgi import PanelASGI
from panel.io.state import state
from panel.util import edit_readonly


class _Config:
    """Stands in for uvicorn.Config, which reconfigures logging on init."""

    def __init__(self, app, **kwargs):
        self.app = app
        self.kwargs = kwargs


@pytest.fixture
def invoke_asgi(monkeypatch, tmp_path):
    """
    Runs ``panel serve`` up to the point uvicorn takes over and returns the
    captured uvicorn configuration.
    """
    py = tmp_path / 'app.py'
    py.write_text("import panel as pn; pn.Row('# Example').servable(title='A')")

    captured: dict = {}

    class _Server:
        def __init__(self, config, on_started):
            captured['config'] = config
            captured['on_started'] = on_started

        def run(self):
            captured['ran'] = True

    monkeypatch.setattr(uvicorn, 'Config', _Config)
    monkeypatch.setattr(serve_module, '_uvicorn_server', _Server)

    def run(*argv, server='asgi'):
        parser = argparse.ArgumentParser()
        subcommand = Serve(parser=parser)
        args = parser.parse_args(
            [str(py), '--port', '0', '--server', server, *argv]
        )
        subcommand.invoke(args)
        assert captured['ran']
        return captured['config']

    base_url = state.base_url
    try:
        yield run
    finally:
        with edit_readonly(state):
            state.base_url = base_url
        config.autoreload = False
        config.session_history = 0
        config.basic_auth = None
        config.cookie_path = '/'
        Serve._static_dirs = {}
        for app in list(state._server_config):
            if isinstance(app, PanelASGI):
                state._server_config.pop(app, None)


def _panel_asgi(uv_config):
    app = uv_config.app
    if isinstance(app, PanelASGI):
        return app
    return app.state._panel_asgi_apps[0]


@pytest.mark.parametrize('args', [
    ['--plugins', 'some.module'],
    ['--rest-provider', 'param'],
    ['--rest-session-info'],
    ['--enable-xsrf-cookies'],
])
def test_serve_asgi_rejects_tornado_only_args(invoke_asgi, args, capsys):
    with pytest.raises(SystemExit):
        invoke_asgi(*args)
    err = capsys.readouterr().err
    assert args[0] in err
    assert '--server tornado' in err


def test_serve_asgi_rejects_num_procs(invoke_asgi, capsys):
    with pytest.raises(SystemExit):
        invoke_asgi('--num-procs', '2')
    assert '--num-procs is not supported' in capsys.readouterr().err


def test_serve_asgi_defaults(invoke_asgi):
    uv_config = invoke_asgi()
    asgi = _panel_asgi(uv_config)

    assert isinstance(asgi, PanelASGI)
    assert list(asgi.core.applications) == ['/app']
    assert uv_config.kwargs == {
        'host': '0.0.0.0',  # noqa: S104
        'port': 0,
        'ws_max_size': DEFAULT_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES,
    }


def test_serve_asgi_server_arguments(invoke_asgi):
    asgi = _panel_asgi(invoke_asgi(
        '--prefix', 'sub/path',
        '--session-token-expiration', '20',
        '--keep-alive', '1000',
        '--unused-session-lifetime', '5000',
        '--allow-websocket-origin', 'example.com',
    ))
    core = asgi.core

    assert core.prefix == '/sub/path'
    assert core.session_token_expiration == 20
    assert core._keep_alive_milliseconds == 1000
    assert core._unused_session_lifetime_milliseconds == 5000
    assert 'example.com:80' in core.websocket_origins


def test_serve_asgi_filters_tornado_only_kwargs(invoke_asgi):
    """
    ``_configure_panel`` returns arguments only the Tornado server accepts,
    e.g. the cookie settings backing Tornado's secure cookies. Passing them
    on would raise a TypeError, so serving has to succeed without them.
    """
    asgi = _panel_asgi(invoke_asgi('--cookie-path', '/sub'))
    assert isinstance(asgi, PanelASGI)
    assert config.cookie_path == '/sub'


def test_serve_asgi_static_dirs_and_liveness(invoke_asgi, tmp_path):
    assets = tmp_path / 'assets'
    assets.mkdir()
    asgi = _panel_asgi(invoke_asgi(
        '--static-dirs', f'assets={assets}', '--liveness',
        '--liveness-endpoint', 'alive'
    ))

    assert asgi._static_dirs == {'/assets': str(assets)}
    patterns = [pattern.pattern for pattern, _ in asgi._extra_routes]
    assert any('alive' in pattern for pattern in patterns)


def test_serve_asgi_index_and_redirect_arguments(invoke_asgi):
    asgi = _panel_asgi(invoke_asgi('--disable-index', '--disable-index-redirect'))
    assert not asgi._index_enabled
    assert not asgi._redirect_root


def test_serve_asgi_uvicorn_arguments(invoke_asgi):
    uv_config = invoke_asgi(
        '--address', '127.0.0.1', '--root-path', '/proxy',
        '--websocket-max-message-size', '1000', '--use-xheaders'
    )
    assert uv_config.kwargs == {
        'host': '127.0.0.1',
        'port': 0,
        'root_path': '/proxy',
        'ws_max_size': 1000,
        'proxy_headers': True,
        'forwarded_allow_ips': '*',
    }


def test_serve_asgi_root_path_sets_base_url(invoke_asgi):
    invoke_asgi('--root-path', '/proxy')
    # Relative paths are resolved against the base URL, so the trailing
    # slash has to be added, i.e. /app must not become /proxyapp.
    assert state.base_url == '/proxy/'


def test_serve_asgi_root_path_must_be_absolute(invoke_asgi):
    with pytest.raises(ValueError, match='must start with a leading slash'):
        invoke_asgi('--root-path', 'proxy')


def test_serve_asgi_unix_socket(invoke_asgi, tmp_path):
    socket = str(tmp_path / 'panel.sock')
    uv_config = invoke_asgi('--unix-socket', socket)
    assert uv_config.kwargs == {
        'uds': socket, 'ws_max_size': DEFAULT_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES
    }


def test_serve_asgi_basic_auth_installs_auth_policy(invoke_asgi):
    from panel.auth import BasicAuthProvider
    from panel.io.auth import PanelAuthPolicy

    asgi = _panel_asgi(invoke_asgi('--basic-auth', 'my_password'))

    assert isinstance(asgi._auth_policy, PanelAuthPolicy)
    assert isinstance(asgi._auth_policy.provider, BasicAuthProvider)
    assert config.basic_auth == 'my_password'


def test_serve_asgi_admin(invoke_asgi):
    asgi = _panel_asgi(invoke_asgi('--admin'))
    assert '/admin' in asgi.core.applications
    # The admin dashboard depends on the periodic cleanup callback its own
    # ApplicationContext adds, so the context must not be the generic one.
    assert asgi.core._applications['/admin'] is state._admin_context


def test_serve_fastapi_wraps_panel_asgi(invoke_asgi):
    pytest.importorskip('fastapi')
    from fastapi import FastAPI

    uv_config = invoke_asgi(server='fastapi')

    assert isinstance(uv_config.app, FastAPI)
    assert isinstance(_panel_asgi(uv_config), PanelASGI)
