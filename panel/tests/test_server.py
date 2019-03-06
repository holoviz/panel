from bokeh.client import pull_session
from bokeh.models import Div
from panel.io import state
from panel.pane import HTML


def test_get_server():
    html = HTML('<h1>Title</h1>')

    server = html.get_server(port=5006)
    assert server.port == 5006

    url = "http://localhost:" + str(server.port) + "/"
    session = pull_session(session_id='Test', url=url, io_loop=server.io_loop)
    root = session.document.roots[0]
    assert isinstance(root, Div)
    assert root.text == '<h1>Title</h1>'
    server.stop()


def test_server_update():
    html = HTML('<h1>Title</h1>')

    server = html.get_server(port=5006)
    url = "http://localhost:" + str(server.port) + "/"
    session = pull_session(session_id='Test', url=url, io_loop=server.io_loop)

    html.object = '<h1>New Title</h1>'

    session.pull()
    root = session.document.roots[0]
    assert isinstance(root, Div)
    assert root.text == '<h1>New Title</h1>'
    server.stop()


def test_server_change_io_state():
    html = HTML('<h1>Title</h1>')

    server = html.get_server(port=5006)
    url = "http://localhost:" + str(server.port) + "/"
    session = pull_session(session_id='Test', url=url, io_loop=server.io_loop)

    def handle_event(event):
        assert state.curdoc is session.document

    html.param.watch(handle_event, 'object')
    html._server_change(session.document, 'text', '<h1>Title</h1>', '<h1>New Title</h1>')

    server.stop()
