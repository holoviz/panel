from panel.models import HTML as BkHTML
from panel.io import state


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
