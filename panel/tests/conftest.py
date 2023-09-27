"""
A module containing testing utilities and fixtures.
"""
import atexit
import os
import pathlib
import re
import shutil
import signal
import socket
import tempfile
import time
import unittest

from contextlib import contextmanager
from subprocess import PIPE, Popen

import pandas as pd
import pytest

from bokeh.client import pull_session
from bokeh.document import Document
from pyviz_comms import Comm

from panel import config, serve
from panel.config import panel_extension
from panel.io.state import set_curdoc, state
from panel.pane import HTML, Markdown

CUSTOM_MARKS = ('ui', 'jupyter', 'subprocess')

config.apply_signatures = False

JUPYTER_PORT = 8887
JUPYTER_TIMEOUT = 15 # s
JUPYTER_PROCESS = None

def port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    is_open = sock.connect_ex(("127.0.0.1", port)) == 0
    sock.close()
    return is_open

def get_default_port():
    # to get a different starting port per worker for pytest-xdist
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "0")
    n = int(re.sub(r"\D", "", worker_id))
    return 6000 + n * 30

def start_jupyter():
    global JUPYTER_PORT, JUPYTER_PROCESS
    args = ['jupyter', 'server', '--port', str(JUPYTER_PORT), "--NotebookApp.token=''"]
    JUPYTER_PROCESS = process = Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1, encoding='utf-8')
    deadline = time.monotonic() + JUPYTER_TIMEOUT
    while True:
        line = process.stderr.readline()
        time.sleep(0.02)
        if "http://127.0.0.1:" in line:
            host = "http://127.0.0.1:"
            break
        if "http://localhost:" in line:
            host = "http://localhost:"
            break
        if time.monotonic() > deadline:
            raise TimeoutError(
                'jupyter server did not start within {timeout} seconds.'
            )
    JUPYTER_PORT = int(line.split(host)[-1][:4])

def cleanup_jupyter():
    if JUPYTER_PROCESS is not None:
        os.kill(JUPYTER_PROCESS.pid, signal.SIGTERM)

@pytest.fixture
def jupyter_preview(request):
    path = pathlib.Path(request.fspath.dirname)
    rel = path.relative_to(pathlib.Path(request.config.invocation_dir).absolute())
    return f'http://localhost:{JUPYTER_PORT}/panel-preview/render/{str(rel)}'

atexit.register(cleanup_jupyter)
optional_markers = {
    "ui": {
        "help": "<Command line help text for flag1...>",
        "marker-descr": "UI test marker",
        "skip-reason": "Test only runs with the --ui option."
    },
    "jupyter": {
        "help": "Runs Jupyter related tests",
        "marker-descr": "Jupyter test marker",
        "skip-reason": "Test only runs with the --jupyter option."
    },
    "subprocess": {
        "help": "Runs tests that fork the process",
        "marker-descr": "Subprocess test marker",
        "skip-reason": "Test only runs with the --subprocess option."
    },
    "docs": {
        "help": "Runs docs specific tests",
        "marker-descr": "Docs test marker",
        "skip-reason": "Test only runs with the --docs option."
    }
}


def pytest_addoption(parser):
    for marker, info in optional_markers.items():
        parser.addoption("--{}".format(marker), action="store_true",
                         default=False, help=info['help'])


def pytest_configure(config):
    for marker, info in optional_markers.items():
        config.addinivalue_line("markers",
                                "{}: {}".format(marker, info['marker-descr']))
    if getattr(config.option, 'jupyter') and not port_open(JUPYTER_PORT):
        start_jupyter()


def pytest_collection_modifyitems(config, items):
    skipped, selected = [], []
    markers = [m for m in optional_markers if config.getoption(f"--{m}")]
    empty = not markers
    for item in items:
        if empty and any(m in item.keywords for m in optional_markers):
            skipped.append(item)
        elif empty:
            selected.append(item)
        elif not empty and any(m in item.keywords for m in markers):
            selected.append(item)
        else:
            skipped.append(item)

    config.hook.pytest_deselected(items=skipped)
    items[:] = selected


@pytest.fixture
def context(context):
    # Set the default timeout to 20 secs
    context.set_default_timeout(20_000)
    yield context

PORT = [get_default_port()]

@pytest.fixture
def document():
    return Document()


@pytest.fixture
def server_document():
    doc = Document()
    session_context = unittest.mock.Mock()
    doc._session_context = lambda: session_context
    with set_curdoc(doc):
        yield doc

@pytest.fixture
def comm():
    return Comm()


@pytest.fixture
def port():
    PORT[0] += 1
    return PORT[0]


@pytest.fixture
def dataframe():
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
    port = 5050
    html = HTML('<h1>Title</h1>')
    server = serve(html, port=port, show=False, start=False)
    session = pull_session(
        session_id='Test',
        url="http://localhost:{:d}/".format(server.port),
        io_loop=server.io_loop
    )
    yield html, server, session, port
    try:
        server.stop()
    except AssertionError:
        pass  # tests may already close this


@pytest.fixture()
def markdown_server_session():
    port = 5051
    html = Markdown('#Title')
    server = serve(html, port=port, show=False, start=False)
    session = pull_session(
        session_id='Test',
        url="http://localhost:{:d}/".format(server.port),
        io_loop=server.io_loop
    )
    yield html, server, session, port
    try:
        server.stop()
    except AssertionError:
        pass  # tests may already close this


@pytest.fixture
def multiple_apps_server_sessions(port):
    """Serve multiple apps and yield a factory to allow
    parameterizing the slugs and the titles."""
    servers = []
    def create_sessions(slugs, titles):
        app1_slug, app2_slug = slugs
        apps = {
            app1_slug: Markdown('First app'),
            app2_slug: Markdown('Second app')
        }
        server = serve(apps, port=port, title=titles, show=False, start=False)
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
    try:
        yield
    finally:
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
def module_cleanup():
    """
    Cleanup Panel extensions after each test.
    """
    from bokeh.core.has_props import _default_resolver
    to_reset = list(panel_extension._imports.values())

    _default_resolver._known_models = {
        name: model for name, model in _default_resolver._known_models.items()
        if not any(model.__module__.startswith(tr) for tr in to_reset)
    }

@pytest.fixture(autouse=True)
def server_cleanup():
    """
    Clean up server state after each test.
    """
    try:
        yield
    finally:
        state.reset()

@pytest.fixture(autouse=True)
def cache_cleanup():
    state.clear_caches()

@pytest.fixture
def py_file():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.py')
    try:
        yield tf
    finally:
        tf.close()

@pytest.fixture
def html_file():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.html')
    try:
        yield tf
    finally:
        tf.close()

@pytest.fixture
def threads():
    config.nthreads = 4
    try:
        yield 4
    finally:
        config.nthreads = None

@pytest.fixture
def reuse_sessions():
    config.reuse_sessions = True
    try:
        yield
    finally:
        config.reuse_sessions = False
        config.session_key_func = None
        state._sessions.clear()
        state._session_key_funcs.clear()

@pytest.fixture
def nothreads():
    yield

@pytest.fixture
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)
