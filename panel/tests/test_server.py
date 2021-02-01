import os
import pathlib
import time

import param
import pytest
import requests

from panel.config import config
from panel.io import state
from panel.models import HTML as BkHTML
from panel.pane import Markdown
from panel.io.server import get_server, serve, set_curdoc
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
    html._server_change(session.document, None, 'text', '<h1>Title</h1>', '<h1>New Title</h1>')


def test_server_static_dirs():
    html = Markdown('# Title')

    static = {'tests': os.path.dirname(__file__)}
    server = serve(html, port=5008, threaded=True, static_dirs=static, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get("http://localhost:5008/tests/test_server.py")

    try:
        with open(__file__, encoding='utf-8') as f:
            assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')
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

    server = serve(button, port=5008, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get("http://localhost:5008/")

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


def test_server_session_info():
    with config.set(session_history=-1):
        html = Markdown('# Title')

        server = serve(html, port=5009, threaded=True, show=False)

        # Wait for server to start
        time.sleep(1)

        requests.get("http://localhost:5009/")

        assert state.session_info['total'] == 1
        assert len(state.session_info['sessions']) == 1
        sid, session = list(state.session_info['sessions'].items())[0]
        assert session['user_agent'].startswith('python-requests')
        assert state.session_info['live'] == 0

        doc = list(html._documents.keys())[0]
        session_context = param.Parameterized()
        session_context._document = doc
        session_context.id = sid
        doc._session_context = session_context
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