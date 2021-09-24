import os
import pathlib
import time
import weakref

import param
import pytest
import requests

from panel.config import config
from panel.io import state
from panel.models import HTML as BkHTML
from panel.pane import Markdown
from panel.io.resources import DIST_DIR
from panel.io.server import get_server, serve, set_curdoc
from panel.template import BootstrapTemplate
from panel.widgets import Button


def test_get_server(html_server_session):
    html, server, session = html_server_session

    assert server.port == 5006
    root = session.document.roots[0]
    assert isinstance(root, BkHTML)
    assert root.text == '&lt;h1&gt;Title&lt;/h1&gt;'


def test_server_update(html_server_session):
    html, server, session = html_server_session

    html.object = '<h1>New Title</h1>'
    session.pull()
    root = session.document.roots[0]
    assert isinstance(root, BkHTML)
    assert root.text == '&lt;h1&gt;New Title&lt;/h1&gt;'


def test_server_change_io_state(html_server_session):
    html, server, session = html_server_session

    def handle_event(event):
        assert state.curdoc is session.document

    html.param.watch(handle_event, 'object')
    html._server_change(session.document, None, None, 'text', '<h1>Title</h1>', '<h1>New Title</h1>')


def test_server_static_dirs():
    html = Markdown('# Title')

    static = {'tests': os.path.dirname(__file__)}
    server = serve(html, port=6000, threaded=True, static_dirs=static, show=False)

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6000/tests/test_server.py")
        with open(__file__, encoding='utf-8') as f:
            assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')
    finally:
        server.stop()


def test_server_template_static_resources():
    template = BootstrapTemplate()

    server = serve({'template': template}, port=6001, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6001/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")
        with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
            assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')
    finally:
        server.stop()


def test_server_template_static_resources_with_prefix():
    template = BootstrapTemplate()

    server = serve({'template': template}, port=6004, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6004/prefix/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")
        with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
            assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')
    finally:
        server.stop()


def test_server_template_static_resources_with_prefix_relative_url():
    template = BootstrapTemplate()

    server = serve({'template': template}, port=6005, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6005/prefix/template")
        content = r.content.decode('utf-8')
        assert 'href="static/extensions/panel/bundled/bootstraptemplate/bootstrap.css"' in content
    finally:
        server.stop()


def test_server_template_static_resources_with_subpath_and_prefix_relative_url():
    template = BootstrapTemplate()

    server = serve({'/subpath/template': template}, port=6005, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6005/prefix/subpath/template")
        content = r.content.decode('utf-8')
        assert 'href="../static/extensions/panel/bundled/bootstraptemplate/bootstrap.css"' in content
    finally:
        server.stop()


def test_server_extensions_on_root():
    html = Markdown('# Title')

    server = serve(html, port=6006, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    try:
        r = requests.get("http://localhost:6006/static/extensions/panel/css/loading.css")
        assert r.ok
    finally:
        server.stop()


def test_autoload_js():
    html = Markdown('# Title')
    port = 6007
    app_name = 'test'
    server = serve({app_name: html}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(0.5)

    args = f"bokeh-autoload-element=1002&bokeh-app-path=/{app_name}&bokeh-absolute-url=http://localhost:{port}/{app_name}"
    r = requests.get(f"http://localhost:{port}/{app_name}/autoload.js?{args}")

    try:
        assert r.status_code == 200
        assert f"http://localhost:{port}/static/extensions/panel/css/alerts.css" in r.content.decode('utf-8')
    finally:
        server.stop()


def test_server_async_callbacks():
    button = Button(name='Click')

    counts = []

    async def cb(event, count=[0]):
        import asyncio
        count[0] += 1
        counts.append(count[0])
        await asyncio.sleep(1)
        count[0] -= 1

    button.on_click(cb)

    server = serve(button, port=6002, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get("http://localhost:6002/")

    doc = list(button._models.values())[0][0].document
    with set_curdoc(doc):
        for _ in range(5):
            button.clicks += 1

    # Wait for callbacks to be scheduled
    time.sleep(2)

    # Ensure multiple callbacks started concurrently
    try:
        assert max(counts) > 1
    finally:
        server.stop()


def test_serve_config_per_session_state():
    CSS1 = 'body { background-color: red }'
    CSS2 = 'body { background-color: green }'
    def app1():
        config.raw_css = [CSS1]
    def app2():
        config.raw_css = [CSS2]

    server1 = serve(app1, port=6004, threaded=True, show=False)
    server2 = serve(app2, port=6005, threaded=True, show=False)

    r1 = requests.get("http://localhost:6004/").content.decode('utf-8')
    r2 = requests.get("http://localhost:6005/").content.decode('utf-8')

    try:
        assert CSS1 not in config.raw_css
        assert CSS2 not in config.raw_css
        assert CSS1 in r1
        assert CSS2 not in r1
        assert CSS1 not in r2
        assert CSS2 in r2
    finally:
        server1.stop()
        server2.stop()


def test_server_session_info():
    with config.set(session_history=-1):
        html = Markdown('# Title')

        server = serve(html, port=6003, threaded=True, show=False)

        # Wait for server to start
        time.sleep(1)

        requests.get("http://localhost:6003/")

        assert state.session_info['total'] == 1
        assert len(state.session_info['sessions']) == 1
        sid, session = list(state.session_info['sessions'].items())[0]
        assert session['user_agent'].startswith('python-requests')
        assert state.session_info['live'] == 0

        doc = list(html._documents.keys())[0]
        session_context = param.Parameterized()
        session_context._document = doc
        session_context.id = sid
        doc._session_context = weakref.ref(session_context)
        state.curdoc = doc
        state._init_session(None)
        assert state.session_info['live'] == 1

    server.stop()
    state.curdoc = None
    html._server_destroy(session_context)
    assert state.session_info['live'] == 0


def test_show_server_info(html_server_session, markdown_server_session):
    server_info = repr(state)
    assert "localhost:5006 - HTML" in server_info
    assert "localhost:5007 - Markdown" in server_info


def test_kill_all_servers(html_server_session, markdown_server_session):
    _, server_1, _ = html_server_session
    _, server_2, _ = markdown_server_session
    state.kill_all_servers()
    assert server_1._stopped
    assert server_2._stopped


def test_multiple_titles(multiple_apps_server_sessions):
    """Serve multiple apps with a title per app."""
    session1, session2 = multiple_apps_server_sessions(
        slugs=('app1', 'app2'), titles={'app1': 'APP1', 'app2': 'APP2'})
    assert session1.document.title == 'APP1'
    assert session2.document.title == 'APP2'

    # Slug names and title keys should match
    with pytest.raises(KeyError):
        session1, session2 = multiple_apps_server_sessions(
            slugs=('app1', 'app2'), titles={'badkey': 'APP1', 'app2': 'APP2'})


def test_serve_can_serve_panel_app_from_file():
    path = pathlib.Path(__file__).parent / "io"/"panel_app.py"
    server = get_server({"panel-app": path})
    assert "/panel-app" in server._tornado.applications

def test_serve_can_serve_bokeh_app_from_file():
    path = pathlib.Path(__file__).parent / "io"/"bk_app.py"
    server = get_server({"bk-app": path})
    assert "/bk-app" in server._tornado.applications
