"""
Tests for embedding Panel applications in a FastAPI application, i.e. the
routing precedence between the FastAPI routes and the routes ``PanelASGI``
serves and the composition of their lifespans.
"""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.testclient import TestClient

from panel.io.fastapi import (
    PanelDispatchMiddleware, add_application, add_applications,
)
from panel.io.state import state
from panel.pane import Markdown


@pytest.fixture
def fastapi_app():
    """
    Yields a factory building FastAPI applications with Panel applications
    added to them and cleans up the global state they register in.
    """
    added = []

    def create(*args, app=None, **kwargs):
        panel_app = add_applications(*args, app=app or FastAPI(), **kwargs)
        added.append(panel_app)
        return panel_app

    yield create
    for panel_app in added:
        state._server_config.pop(panel_app.asgi, None)


def markdown_app():
    return Markdown('# Panel app')


def test_fastapi_serves_panel_and_fastapi_routes(fastapi_app):
    app = FastAPI()

    @app.get('/api/data')
    def data():
        return {'value': 1}

    fastapi_app({'/app': markdown_app}, app=app)

    with TestClient(app) as client:
        assert client.get('/api/data').json() == {'value': 1}
        r = client.get('/app')
    assert r.status_code == 200
    assert 'Bokeh.safely' in r.text


def test_fastapi_serves_panel_index(fastapi_app):
    panel_app = fastapi_app({'/app1': markdown_app, '/app2': markdown_app})

    with TestClient(panel_app.app) as client:
        r = client.get('/')
    assert r.status_code == 200
    assert '/app1' in r.text
    assert '/app2' in r.text


@pytest.mark.parametrize('route', ['/', '/favicon.ico'])
def test_fastapi_route_wins_over_deferred_panel_route(fastapi_app, route):
    """
    Panel serves an index page and a favicon as a convenience, but they must
    not take over these routes from the application it is embedded in.
    """
    app = FastAPI()

    @app.get(route)
    def declared():
        return {'owner': 'fastapi'}

    fastapi_app({'/app1': markdown_app, '/app2': markdown_app}, app=app)

    with TestClient(app) as client:
        r = client.get(route)
        # The Panel routes are unaffected
        assert client.get('/app1').status_code == 200
    assert r.json() == {'owner': 'fastapi'}


def test_fastapi_route_does_not_shadow_panel_application(fastapi_app):
    """
    Only the deferred convenience routes are handed back to FastAPI; an
    application route Panel owns is served by Panel even if FastAPI declares
    the same path.
    """
    app = FastAPI()

    @app.get('/app')
    def declared():
        return {'owner': 'fastapi'}

    fastapi_app({'/app': markdown_app}, app=app)

    with TestClient(app) as client:
        r = client.get('/app')
    assert r.status_code == 200
    assert 'Bokeh.safely' in r.text


def test_fastapi_unhandled_route_is_a_fastapi_404(fastapi_app):
    panel_app = fastapi_app({'/app': markdown_app})

    with TestClient(panel_app.app) as client:
        r = client.get('/missing')
    assert r.status_code == 404
    assert r.json() == {'detail': 'Not Found'}


def test_fastapi_lifespan_is_wrapped_not_replaced(fastapi_app):
    events = []

    @asynccontextmanager
    async def lifespan(app):
        events.append('startup')
        yield
        events.append('shutdown')

    app = FastAPI(lifespan=lifespan)
    panel_app = fastapi_app({'/app': markdown_app}, app=app)

    with TestClient(app) as client:
        assert client.get('/app').status_code == 200
        assert events == ['startup']
        assert panel_app.asgi._panel_started
    assert events == ['startup', 'shutdown']
    assert not panel_app.asgi._panel_started


def test_fastapi_multiple_add_applications_share_middleware(fastapi_app):
    app = FastAPI()
    first = fastapi_app({'/app1': markdown_app}, app=app)
    second = fastapi_app({'/app2': markdown_app}, app=app)

    middleware = [m for m in app.user_middleware if m.cls is PanelDispatchMiddleware]
    assert len(middleware) == 1
    assert middleware[0].kwargs['panel_apps'] == [first.asgi, second.asgi]

    with TestClient(app) as client:
        assert client.get('/app1').status_code == 200
        assert client.get('/app2').status_code == 200
        # Both applications are started, i.e. the second lifespan wrapper did
        # not replace the first
        assert first.asgi._panel_started
        assert second.asgi._panel_started
    assert not first.asgi._panel_started
    assert not second.asgi._panel_started


def test_fastapi_prefix_must_be_absolute(fastapi_app):
    with pytest.raises(ValueError, match="prefix must start with '/'"):
        fastapi_app({'/app': markdown_app}, prefix='prefix')


def test_fastapi_prefix_routes_applications(fastapi_app):
    panel_app = fastapi_app({'/app': markdown_app}, prefix='/prefix')

    with TestClient(panel_app.app) as client:
        assert client.get('/prefix/app').status_code == 200
        assert client.get('/app').status_code == 404


def test_fastapi_forwards_core_configuration(fastapi_app):
    panel_app = fastapi_app({'/app': markdown_app}, session_token_expiration=20)

    assert panel_app.core is panel_app.asgi.core
    assert set(panel_app.applications) == {'/app'}
    # Attribute access falls through to the BokehServerCore configuration
    assert panel_app.session_token_expiration == 20
    assert panel_app.sign_sessions == panel_app.core.sign_sessions


def test_fastapi_add_application_decorator():
    app = FastAPI()

    @add_application('/app', app=app, title='Decorated')
    def declared():
        return Markdown('# Decorated')

    try:
        with TestClient(app) as client:
            r = client.get('/app')
    finally:
        for asgi in list(state._server_config):
            state._server_config.pop(asgi, None)

    assert r.status_code == 200
    assert '<title>Decorated</title>' in r.text
    # The decorated function is still callable
    assert isinstance(declared(), Markdown)
