import os
import time

from tempfile import NamedTemporaryFile

import pytest
import requests

from panel.io import state
from panel.models import HTML as BkHTML
from panel.pane import Markdown
from panel.io.server import serve
from panel.template import Template


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
    with open(__file__) as f:
        assert f.read() == r.content.decode('utf-8')
    server.stop()


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


def test_template_css():
    t = Template("{% extends base %}")
    t.add_panel('A', 1)
    css = ".test { color: 'green' }"
    ntf = NamedTemporaryFile()
    with open(ntf.name, 'w') as f:
        f.write(css)
    t.add_variable('template_css_files', [ntf.name])

    server = serve(t, port=5009, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get("http://localhost:5009/")
    assert css in r.content.decode('utf-8')
    server.stop()
