"""
Tests for the native Django integration, i.e. the composition of
``PanelASGI`` with Django's own ASGI application.
"""
import asyncio

import pytest

pytest.importorskip("django")
pytest.importorskip("httpx")

from django.conf import settings  # isort: skip

if not settings.configured:
    # Must be configured before django.setup() runs, i.e. before the ASGI
    # application is built, and the urlconf below lives in this module.
    settings.configure(
        DEBUG=True,
        ALLOWED_HOSTS=['*'],
        DATABASES={},
        INSTALLED_APPS=['django.contrib.staticfiles'],
        ROOT_URLCONF=__name__,
        SECRET_KEY='panel-test',
        STATIC_URL='/static/',
        STATICFILES_FINDERS=[
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'panel.io.django.PanelExtensionFinder',
        ],
        USE_TZ=True,
    )

import django

from django.http import HttpResponse
from django.urls import path, re_path
from starlette.testclient import TestClient

from panel.config import config
from panel.io import django as django_module
from panel.io.django import (
    AutoloadJsConsumer, PanelExtensionFinder, RoutingConfiguration, autoload,
    directory, document, get_asgi_application, with_request, with_url_args,
)
from panel.io.state import state
from panel.pane import Markdown

#---------------------------------------------------------------------
# Django project
#---------------------------------------------------------------------

def django_index(request):
    return HttpResponse('django index')


def django_embedded(request):
    return HttpResponse('django embedded')


def django_static(request, path):
    return HttpResponse(f'django static {path}')


urlpatterns = [
    path('', django_index),
    path('embedded', django_embedded),
    re_path(r'^static/custom/(?P<path>.*)$', django_static),
]


def markdown_app(doc):
    Markdown('# Test app').server_doc(doc)


#---------------------------------------------------------------------
# Fixtures
#---------------------------------------------------------------------

@pytest.fixture(scope='module', autouse=True)
def django_setup():
    django.setup()


@pytest.fixture
def django_apps():
    apps = []

    def create(routings, **kwargs):
        asgi = get_asgi_application(routings, **kwargs)
        apps.append(asgi)
        return asgi

    yield create
    for asgi in apps:
        state._server_config.pop(asgi, None)


@pytest.fixture
def django_client(django_apps):
    def create(routings, **kwargs):
        return TestClient(django_apps(routings, **kwargs))
    return create


#---------------------------------------------------------------------
# Routing
#---------------------------------------------------------------------

def test_django_document_url_normalization():
    assert document('sliders', markdown_app).url == '/sliders'
    assert document('/sliders/', markdown_app).url == '/sliders'
    assert document('^$', markdown_app).url == '/'


def test_django_regex_route_converted(monkeypatch):
    warnings = []
    monkeypatch.setattr(
        django_module.logger, 'warning',
        lambda msg, *args: warnings.append(msg % args)
    )
    routing = document(r'^user/(?P<name>[\w-]+)$', markdown_app)
    assert routing.url == '/user/{name}'
    assert 'Converted regex route' in warnings[0]


def test_django_directory(tmp_path):
    (tmp_path / 'app.py').write_text('import panel as pn; pn.panel("app").servable()')
    (tmp_path / '_hidden.py').write_text('raise RuntimeError()')
    (tmp_path / 'notes.txt').write_text('not an app')
    routings = directory(tmp_path)
    assert [routing.url for routing in routings] == ['/app']
    assert all(routing.document for routing in routings)


def test_django_directory_missing_path(tmp_path, monkeypatch):
    warnings = []
    monkeypatch.setattr(
        django_module.logger, 'warning',
        lambda msg, *args: warnings.append(msg % args)
    )
    assert directory(tmp_path / 'nope') == []
    assert "doesn't exist" in warnings[0]


def test_django_duplicate_urls(django_apps):
    with pytest.raises(ValueError, match='Multiple applications'):
        django_apps([document('app', markdown_app), autoload('app', markdown_app)])


def test_django_invalid_routing(django_apps):
    with pytest.raises(ValueError, match='declare applications with'):
        django_apps([markdown_app])


#---------------------------------------------------------------------
# Dispatch
#---------------------------------------------------------------------

def test_django_serves_document(django_client):
    with django_client(document('app', markdown_app)) as client:
        r = client.get('/app')
    assert r.status_code == 200
    assert 'Bokeh.safely' in r.text


def test_django_serves_root_from_django(django_client):
    with django_client(document('app', markdown_app)) as client:
        assert client.get('/').text == 'django index'


def test_django_autoload_document_route_deferred(django_client):
    """
    An application declared with ``autoload`` is embedded in a Django view,
    so Django must win on the application path itself.
    """
    with django_client(autoload('embedded', markdown_app)) as client:
        assert client.get('/embedded').text == 'django embedded'
        r = client.get('/embedded/autoload.js?bokeh-autoload-element=1000')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('application/javascript')
    assert 'bokeh.min.js' in r.text


def test_django_document_route_not_deferred(django_client):
    with django_client(document('embedded', markdown_app)) as client:
        assert 'Bokeh.safely' in client.get('/embedded').text


def test_django_websocket_route(django_client):
    with django_client(document('app', markdown_app)) as client:
        r = client.get('/app/ws')
    assert r.status_code == 400
    assert 'WebSocket' in r.text


def test_django_metadata_route(django_client):
    with django_client(document('app', markdown_app)) as client:
        assert 'data' in client.get('/app/metadata').json()


def test_django_serves_favicon(django_client):
    with django_client(document('app', markdown_app)) as client:
        r = client.get('/favicon.ico')
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/x-icon'


def test_django_serves_bokehjs(django_client):
    with django_client(document('app', markdown_app)) as client:
        r = client.get('/static/js/bokeh.min.js')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('application/javascript')


def test_django_static_falls_through(django_client):
    with django_client(document('app', markdown_app)) as client:
        assert client.get('/static/custom/style.css').text == 'django static style.css'


def test_django_unknown_route(django_client):
    with django_client(document('app', markdown_app)) as client:
        assert client.get('/nonexistent').status_code == 404


def test_django_handles_scope(django_apps):
    asgi = django_apps([document('app', markdown_app), autoload('embedded', markdown_app)])

    def scope(path, type='http'):
        return {'type': type, 'path': path, 'root_path': '', 'method': 'GET'}

    assert asgi.handles(scope('/app'))
    assert asgi.handles(scope('/app/ws', type='websocket'))
    assert asgi.handles(scope('/embedded/autoload.js'))
    assert asgi.handles(scope('/embedded/ws', type='websocket'))
    assert asgi.handles(scope('/static/js/bokeh.min.js'))
    assert not asgi.handles(scope('/embedded'))
    assert not asgi.handles(scope('/'))
    assert not asgi.handles(scope('/static/custom/style.css'))
    assert not asgi.handles(scope('/admin/'))
    assert not asgi.handles({'type': 'lifespan'})


def test_django_prefix(django_client):
    with django_client(document('app', markdown_app), prefix='/panel') as client:
        assert client.get('/panel/app').status_code == 200
        assert client.get('/app').status_code == 404


def test_django_websocket_closed_when_unowned(django_client):
    with django_client(document('app', markdown_app)) as client:
        with pytest.raises(Exception):  # noqa: B017 - closed without accept
            with client.websocket_connect('/embedded/ws'):
                pass


def test_django_with_request(django_client):
    paths = []

    def app(doc, request):
        paths.append(request.path)
        Markdown('# Request').server_doc(doc)

    with django_client(document('app', with_request(app))) as client:
        assert client.get('/app').status_code == 200
    assert paths == ['/app']


def test_django_async_app(django_client):
    docs = []

    async def app(doc):
        await asyncio.sleep(0)
        docs.append(state.curdoc)
        Markdown('# Async').server_doc(doc)

    with django_client(document('app', app)) as client:
        assert 'Bokeh.safely' in client.get('/app').text
    assert len(docs) == 1
    assert docs[0] is not None


def test_django_with_url_args(django_client):
    params = []

    def app(doc, **kwargs):
        params.append(kwargs)
        Markdown('# Wildcard').server_doc(doc)

    routing = document('/user/{name}', with_url_args(app))
    with django_client(routing) as client:
        assert client.get('/user/alice').status_code == 200
    assert params == [{'name': 'alice'}]


#---------------------------------------------------------------------
# Static file handling
#---------------------------------------------------------------------

def test_django_extension_finder(tmp_path):
    from bokeh.embed.bundle import extension_dirs
    (tmp_path / 'panel.css').write_text('.panel {}')
    extension_dirs['test_ext'] = tmp_path
    try:
        finder = PanelExtensionFinder()
        assert finder.check() == []
        assert finder.find('extensions/test_ext/panel.css') == str(tmp_path / 'panel.css')
        assert finder.find('extensions/test_ext/panel.css', find_all=True) == [
            str(tmp_path / 'panel.css')
        ]
        assert finder.find('extensions/test_ext/missing.css') == []
        assert finder.find('css/other.css') == []
        assert PanelExtensionFinder.find_location(
            'extensions/test_ext/panel.css', 'extensions/', as_components=True
        ) == (tmp_path, 'panel.css')
        listed = [
            name for name, storage in finder.list([])
            if storage.prefix == 'extensions/test_ext'
        ]
        assert listed == ['panel.css']
    finally:
        del extension_dirs['test_ext']


def test_django_extension_finder_escapes_root(tmp_path):
    from bokeh.embed.bundle import extension_dirs
    (tmp_path / 'secret.txt').write_text('secret')
    (tmp_path / 'ext').mkdir()
    extension_dirs['test_ext'] = tmp_path / 'ext'
    try:
        assert PanelExtensionFinder().find('extensions/test_ext/../secret.txt') == []
    finally:
        del extension_dirs['test_ext']


def test_django_static_extensions_urlpatterns():
    from panel.io.django import static_extensions
    patterns = static_extensions()
    assert len(patterns) == 1
    assert patterns[0].pattern.match('static/extensions/panel/panel.css')


#---------------------------------------------------------------------
# Authentication
#---------------------------------------------------------------------

def test_django_basic_auth(django_client):
    values = {name: getattr(config, name) for name in ('_basic_auth', '_cookie_secret')}
    try:
        with django_client(
            document('app', markdown_app), basic_auth='password',
            cookie_secret='cookie-secret'
        ) as client:
            r = client.get('/app', follow_redirects=False)
            assert r.status_code == 302
            assert r.headers['location'] == '/login?next=%2Fapp'

            # Django's own views are not affected by Panel's authentication
            assert client.get('/').text == 'django index'

            assert 'name="username"' in client.get('/login').text
            r = client.post(
                '/login', data={'username': 'user', 'password': 'password'},
                follow_redirects=False
            )
            assert r.status_code == 302
            assert 'user' in r.cookies
            assert client.get('/app').status_code == 200
    finally:
        config.param.update(**values)
        state.encryption = None


#---------------------------------------------------------------------
# Removed API
#---------------------------------------------------------------------

def test_django_removed_channels_api():
    with pytest.raises(RuntimeError, match='no longer available'):
        RoutingConfiguration({})
    with pytest.raises(RuntimeError, match='no longer available'):
        AutoloadJsConsumer()
