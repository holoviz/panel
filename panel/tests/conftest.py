"""
A module containing testing utilities and fixtures.
"""
import os
import re
import shutil

import pytest

from contextlib import contextmanager

from bokeh.document import Document
from bokeh.client import pull_session
from pyviz_comms import Comm

from panel.pane import HTML, Markdown
from panel.io import state
from panel import serve


@pytest.fixture
def document():
    return Document()


@pytest.fixture
def comm():
    return Comm()


@pytest.fixture
def dataframe():
    import pandas as pd
    return pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'str': ['A', 'B', 'C']
    }, index=[1, 2, 3], columns=['int', 'float', 'str'])


@pytest.fixture
def hv_bokeh():
    import holoviews as hv
    hv.renderer('bokeh')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'bokeh'
    yield
    hv.Store.current_backend = prev_backend


@pytest.fixture
def get_display_handle():
    cleanup = []
    def display_handle(model):
        cleanup.append(model.ref['id'])
        handle = {}
        state._handles[model.ref['id']] = (handle, [])
        return handle
    yield display_handle
    for ref in cleanup:
        if ref in state._handles:
            del state._handles[ref]


@pytest.fixture
def hv_mpl():
    import holoviews as hv
    hv.renderer('matplotlib')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'matplotlib'
    yield
    hv.Store.current_backend = prev_backend


@pytest.fixture
def tmpdir(request, tmpdir_factory):
    name = request.node.name
    name = re.sub(r"[\W]", "_", name)
    MAXVAL = 30
    if len(name) > MAXVAL:
        name = name[:MAXVAL]
    tmp_dir = tmpdir_factory.mktemp(name, numbered=True)
    yield tmp_dir
    shutil.rmtree(str(tmp_dir))


@pytest.fixture()
def html_server_session():
    html = HTML('<h1>Title</h1>')
    server = serve(html, port=5006, show=False, start=False)
    session = pull_session(
        session_id='Test',
        url="http://localhost:{:d}/".format(server.port),
        io_loop=server.io_loop
    )
    yield html, server, session
    try:
        server.stop()
    except AssertionError:
        pass  # tests may already close this


@pytest.fixture()
def markdown_server_session():
    html = Markdown('#Title')
    server = serve(html, port=5007, show=False, start=False)
    session = pull_session(
        session_id='Test',
        url="http://localhost:{:d}/".format(server.port),
        io_loop=server.io_loop
    )
    yield html, server, session
    try:
        server.stop()
    except AssertionError:
        pass  # tests may already close this


@pytest.fixture
def multiple_apps_server_sessions():
    """Serve multiple apps and yield a factory to allow
    parameterizing the slugs and the titles."""
    servers = []
    def create_sessions(slugs, titles):
        app1_slug, app2_slug = slugs
        apps = {
            app1_slug: Markdown('First app'),
            app2_slug: Markdown('Second app')
        }
        server = serve(apps, port=5008, title=titles, show=False, start=False)
        servers.append(server)
        session1 = pull_session(
            url=f"http://localhost:{server.port:d}/app1",
            io_loop=server.io_loop
        )
        session2 = pull_session(
            url=f"http://localhost:{server.port:d}/app2",
            io_loop=server.io_loop
        )
        return session1, session2
    yield create_sessions
    for server in servers:
        try:
            server.stop()
        except AssertionError:
            continue  # tests may already close this


@pytest.fixture
def with_curdoc():
    old_curdoc = state.curdoc
    state.curdoc = Document()
    yield
    state.curdoc = old_curdoc
        

@contextmanager
def set_env_var(env_var, value):
    old_value = os.environ.get(env_var)
    os.environ[env_var] = value
    yield
    if old_value is None:
        del os.environ[env_var]
    else:
        os.environ[env_var] = old_value


@pytest.fixture(autouse=True)
def server_cleanup():
    """
    Clean up after test fails
    """
    yield
    state.kill_all_servers()
    state._indicators.clear()
    state._locations.clear()
