"""
A module containing testing utilities and fixtures.
"""
import asyncio
import atexit
import datetime as dt
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
from functools import cache
from subprocess import PIPE, Popen

import pandas as pd
import pytest

from bokeh.client import pull_session
from bokeh.document import Document
from bokeh.io.doc import curdoc, set_curdoc as set_bkdoc
from pyviz_comms import Comm

from panel import config, serve
from panel.config import panel_extension
from panel.io.reload import (
    _local_modules, _modules, _watched_files, async_file_watcher, watch,
)
from panel.io.state import set_curdoc, state
from panel.pane import HTML, Markdown
from panel.tests.util import get_open_ports
from panel.theme import Design

CUSTOM_MARKS = ('ui', 'jupyter', 'subprocess', 'docs')

config.apply_signatures = False

JUPYTER_PORT = 8887
JUPYTER_TIMEOUT = 15 # s
JUPYTER_PROCESS = None

if os.name != 'nt':
    import resource

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))


for e in os.environ:
    if e.startswith(('BOKEH_', "PANEL_")) and e not in ("PANEL_LOG_LEVEL", ):
        os.environ.pop(e, None)

@cache
def internet_available(host="8.8.8.8", port=53, timeout=3):
    """Check if the internet connection is available."""
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((host, port))
        return True
    except OSError:
        return False

def port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    is_open = sock.connect_ex(("127.0.0.1", port)) == 0
    sock.close()
    return is_open


def get_default_port():
    worker_count = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1"))
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "0")
    worker_idx = int(re.sub(r"\D", "", worker_id))
    return 9001 + (worker_idx * worker_count * 10)

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
                f'jupyter server did not start within {JUPYTER_TIMEOUT} seconds.'
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
        "help": "Runs UI related tests",
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
        parser.addoption(f"--{marker}", action="store_true",
                         default=False, help=info['help'])
    parser.addoption('--repeat', action='store',
        help='Number of times to repeat each test')

def pytest_configure(config):
    for marker, info in optional_markers.items():
        config.addinivalue_line("markers",
                                "{}: {}".format(marker, info['marker-descr']))
    if config.option.jupyter and not port_open(JUPYTER_PORT):
        start_jupyter()

    config.addinivalue_line("markers", "internet: mark test as requiring an internet connection")

def pytest_generate_tests(metafunc):
    repeat = getattr(metafunc.config.option, 'repeat', None)
    if repeat is not None:
        count = int(repeat)

        # We're going to duplicate these tests by parametrizing them,
        # which requires that each test has a fixture to accept the parameter.
        # We can add a new fixture like so:
        metafunc.fixturenames.append('tmp_ct')

        # Now we parametrize. This is what happens when we do e.g.,
        # @pytest.mark.parametrize('tmp_ct', range(count))
        # def test_foo(): pass
        metafunc.parametrize('tmp_ct', range(count))

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


def pytest_runtest_setup(item):
    if "internet" in item.keywords and not internet_available():
        pytest.skip("Skipping test: No internet connection")


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
    try:
        with set_curdoc(doc):
            yield doc
    finally:
        doc._session_context = None

@pytest.fixture
def bokeh_curdoc():
    old_doc = curdoc()
    doc = Document()
    session_context = unittest.mock.Mock()
    doc._session_context = lambda: session_context
    set_bkdoc(doc)
    try:
        yield doc
    finally:
        set_bkdoc(old_doc)

@pytest.fixture
def comm():
    return Comm()

@pytest.fixture
def stop_event():
    event = asyncio.Event()
    try:
        yield event
    finally:
        event.set()

@pytest.fixture
def asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(asyncio.new_event_loop())
    yield
    loop.stop()
    loop.close()

@pytest.fixture
async def watch_files():
    tasks = []
    stop_event = asyncio.Event()
    def watch_files(*files):
        watch(*files)
        tasks.append(asyncio.create_task(async_file_watcher(stop_event)))
    try:
        yield watch_files
    finally:
        if tasks:
            try:
                stop_event.set()
                await tasks[0]
            except FileNotFoundError:
                # Watched files may be deleted before autoreloader
                # is shut down, therefore we catch the error on deletion.
                pass

@pytest.fixture
def port():
    return get_open_ports()[0]


@pytest.fixture
def dataframe():
    return pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'str': ['A', 'B', 'C']
    }, index=[1, 2, 3], columns=['int', 'float', 'str'])


@pytest.fixture
def df_mixed():
    df = pd.DataFrame({
        'int': [1, 2, 3, 4],
        'float': [3.14, 6.28, 9.42, -2.45],
        'str': ['A', 'B', 'C', 'D'],
        'bool': [True, True, True, False],
        'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10), dt.date(2019, 1, 10)],
        'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13), dt.datetime(2020, 1, 15, 13)]
    }, index=['idx0', 'idx1', 'idx2', 'idx3'])
    return df


@pytest.fixture
def df_multiindex(df_mixed):
    df_mi = df_mixed.copy()
    df_mi.index = pd.MultiIndex.from_tuples([
        ('group0', 'subgroup0'),
        ('group0', 'subgroup1'),
        ('group1', 'subgroup0'),
        ('group1', 'subgroup1'),
    ], names=['groups', 'subgroups'])
    return df_mi


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
def hv_plotly():
    import holoviews as hv
    hv.renderer('plotly')
    prev_backend = hv.Store.current_backend
    hv.Store.current_backend = 'plotly'
    yield
    hv.Store.current_backend = prev_backend


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

@pytest.fixture
def html_server_session(asyncio_loop):
    port = 5050
    html = HTML('<h1>Title</h1>')
    server = serve(html, port=port, show=False, start=False)
    session = pull_session(
        session_id='Test',
        url=f"http://localhost:{server.port:d}/",
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
        url=f"http://localhost:{server.port:d}/",
        io_loop=server.io_loop
    )
    yield html, server, session, port
    try:
        server.stop()
    except AssertionError:
        pass  # tests may already close this


@pytest.fixture
def multiple_apps_server_sessions(asyncio_loop, port):
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

    from panel.reactive import ReactiveMetaBase

    to_reset = list(panel_extension._imports.values())
    _default_resolver._known_models = {
        name: model for name, model in _default_resolver._known_models.items()
        if not any(model.__module__.startswith(tr) for tr in to_reset)
    }
    ReactiveMetaBase._loaded_extensions = set()

@pytest.fixture(autouse=True)
def server_cleanup():
    """
    Clean up server state after each test.
    """
    try:
        yield
    finally:
        state.reset()
        _watched_files.clear()
        _modules.clear()
        _local_modules.clear()

@pytest.fixture(autouse=True)
def cache_cleanup():
    state.clear_caches()
    Design._resolve_modifiers.cache_clear()
    Design._cache.clear()

@pytest.fixture
def autoreload():
    config.autoreload = True
    def watch(files):
        if isinstance(files, (str, os.PathLike)):
            files = [files]
        _watched_files.update({str(f) for f in files})
    try:
        yield watch
    finally:
        config.autoreload = False

@pytest.fixture
def py_file():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    try:
        yield tf
    finally:
        tf.close()
        os.unlink(tf.name)

@pytest.fixture
def js_file():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
    try:
        yield tf
    finally:
        tf.close()
        os.unlink(tf.name)

@pytest.fixture
def py_files():
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    tf2 = tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=os.path.split(tf.name)[0], delete=False)
    try:
        yield tf, tf2
    finally:
        tf.close()
        tf2.close()
        os.unlink(tf.name)
        os.unlink(tf2.name)

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

@pytest.fixture
def exception_handler_accumulator():
    exceptions = []

    def eh(exception):
        exceptions.append(exception)

    old_eh = config.exception_handler
    config.exception_handler = eh
    try:
        yield exceptions
    finally:
        config.exception_handler = old_eh


@pytest.fixture
def df_strings():
    descr = [
        'Under the Weather',
        'Top Drawer',
        'Happy as a Clam',
        'Cut To The Chase',
        'Knock Your Socks Off',
        'A Cold Day in Hell',
        'All Greek To Me',
        'A Cut Above',
        'Cut The Mustard',
        'Up In Arms',
        'Playing For Keeps',
        'Fit as a Fiddle',
    ]

    code = [f'{i:02d}' for i in range(len(descr))]

    return pd.DataFrame(dict(code=code, descr=descr))
