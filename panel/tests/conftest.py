"""
A module containing testing utilities and fixtures.
"""
from __future__ import absolute_import, division, unicode_literals

import re
import shutil

import pytest

from bokeh.document import Document
from bokeh.client import pull_session
from pyviz_comms import Comm

from panel.pane import HTML, Markdown


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


@pytest.yield_fixture
def hv_bokeh():
    import holoviews as hv
    hv.renderer('bokeh')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'bokeh'
    yield
    hv.Store.current_backend = prev_backend


@pytest.yield_fixture
def hv_mpl():
    import holoviews as hv
    hv.renderer('matplotlib')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'matplotlib'
    yield
    hv.Store.current_backend = prev_backend


@pytest.yield_fixture
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
    server = html._get_server(port=5006)
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
    server = html._get_server(port=5007)
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
