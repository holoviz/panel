import asyncio
import datetime as dt
import importlib
import logging
import os
import pathlib
import time
import weakref

from functools import partial

import param
import pytest
import requests

from bokeh.events import ButtonClick

from panel.config import config
from panel.io import state
from panel.io.resources import DIST_DIR, JS_VERSION
from panel.io.server import INDEX_HTML, get_server, set_curdoc
from panel.layout import Row
from panel.models import HTML as BkHTML
from panel.models.tabulator import TableEditEvent
from panel.pane import Markdown
from panel.param import ParamFunction
from panel.reactive import ReactiveHTML
from panel.template import BootstrapTemplate
from panel.tests.util import (
    get_open_ports, reverse_proxy_available, serve_and_request, serve_and_wait,
    wait_until,
)
from panel.widgets import (
    Button, Tabulator, Terminal, TextInput,
)


@pytest.fixture(params=["tornado", "fastapi"])
def server_implementation(request):
    try:
        importlib.import_module(request.param)
    except Exception:
        pytest.skip(f'{request.param!r} is not installed')
    old = serve_and_wait.server_implementation
    serve_and_wait.server_implementation = request.param
    try:
        yield request.param
    finally:
        serve_and_wait.server_implementation = old


@pytest.mark.xdist_group(name="server")
def test_get_server(html_server_session):
    html, server, session, port = html_server_session

    assert server.port == port
    root = session.document.roots[0]
    assert isinstance(root, BkHTML)
    assert root.text == '&lt;h1&gt;Title&lt;/h1&gt;'

@pytest.mark.xdist_group(name="server")
def test_server_update(html_server_session):
    html, server, session, port = html_server_session

    html.object = '<h1>New Title</h1>'
    session.pull()
    root = session.document.roots[0]
    assert isinstance(root, BkHTML)
    assert root.text == '&lt;h1&gt;New Title&lt;/h1&gt;'

@pytest.mark.xdist_group(name="server")
def test_server_change_io_state(html_server_session):
    html, server, session, port = html_server_session

    def handle_event(event):
        assert state.curdoc is session.document

    html.param.watch(handle_event, 'object')
    html._server_change(session.document, None, None, 'text', '<h1>Title</h1>', '<h1>New Title</h1>')


def test_server_static_dirs():
    html = Markdown('# Title')

    static = {'tests': os.path.dirname(__file__)}

    r = serve_and_request(html, static_dirs=static, suffix="/tests/test_server.py")

    with open(__file__, encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_root_handler():
    html = Markdown('# Title')

    r = serve_and_request(
        {'app': html}, use_index=True, index=INDEX_HTML, redirect_root=False
    )

    assert 'href="./app"' in r.content.decode('utf-8')

@pytest.mark.parametrize('path', ["/app", "/nested/app"])
def test_server_ico_handling(path, port):
    md = Markdown('# Favicon test')

    ico_path = DIST_DIR / "images" / "icon-32x32.png"
    r = serve_and_request(
        {path: md}, ico_path=ico_path, port=port, suffix=path
    )

    dots = path.count('/')*'.'
    assert f'<link rel="icon" href="{dots}/favicon.ico"' in r.content.decode('utf-8')
    ico = requests.get(f"http://localhost:{port}/favicon.ico")
    assert ico.content == ico_path.read_bytes()

def test_server_ico_handling_with_prefix(port):
    md = Markdown('# Favicon test')

    ico_path = DIST_DIR / "images" / "icon-32x32.png"
    r = serve_and_request(
        {'app': md}, ico_path=ico_path, port=port, prefix='/prefix', suffix='/prefix/app'
    )

    assert '<link rel="icon" href="./favicon.ico"' in r.content.decode('utf-8')
    ico = requests.get(f"http://localhost:{port}/favicon.ico")
    assert ico.content == ico_path.read_bytes()

@pytest.mark.parametrize('path', ["/app", "/nested/app"])
def test_server_template_ico_handling(path, port):
    def app():
        return BootstrapTemplate()

    ico_path = DIST_DIR / "images" / "icon-32x32.png"
    r = serve_and_request(
        {path: app}, ico_path=ico_path, port=port, suffix=path
    )

    dots = path.count('/')*'.'
    assert f'<link rel="icon" href="{dots}/favicon.ico"' in r.content.decode('utf-8')
    ico = requests.get(f"http://localhost:{port}/favicon.ico")
    assert ico.content == ico_path.read_bytes()

def test_server_template_static_resources(server_implementation):
    template = BootstrapTemplate()

    r = serve_and_request({'template': template}, suffix="/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")

    with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


#@pytest.mark.parametrize('server_implementation', ["tornado", "fastapi"], indirect=True)
def test_server_template_static_resources_with_prefix():
    template = BootstrapTemplate()

    r = serve_and_request({'template': template}, prefix="/prefix", suffix="/prefix/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")

    with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


#@pytest.mark.parametrize('server_implementation', ["tornado", "fastapi"], indirect=True)
def test_server_template_static_resources_with_prefix_relative_url():
    template = BootstrapTemplate()

    r = serve_and_request({'template': template}, prefix='/prefix', suffix="/prefix/template")

    assert f'href="static/extensions/panel/bundled/bootstraptemplate/bootstrap.css?v={JS_VERSION}"' in r.content.decode('utf-8')


def test_server_template_static_resources_with_subpath_and_prefix_relative_url():
    template = BootstrapTemplate()

    r = serve_and_request({'/subpath/template': template}, prefix='/prefix', suffix="/prefix/subpath/template")

    assert f'href="../static/extensions/panel/bundled/bootstraptemplate/bootstrap.css?v={JS_VERSION}"' in r.content.decode('utf-8')


def test_server_extensions_on_root(server_implementation):
    md = Markdown('# Title')
    assert serve_and_request(md).ok


def test_autoload_js(port):
    html = Markdown('# Title')
    app_name = 'test'
    args = f"bokeh-autoload-element=1002&bokeh-app-path=/{app_name}&bokeh-absolute-url=http://localhost:{port}/{app_name}"
    r = serve_and_request({app_name: html}, port=port, suffix=f"/{app_name}/autoload.js?{args}")

    assert r.status_code == 200
    assert f"http://localhost:{port}/static/extensions/panel/panel.min.js" in r.content.decode('utf-8')


def test_server_async_callbacks(server_implementation):
    button = Button(name='Click')

    counts = []

    async def cb(event, count=[0]):
        count[0] += 1
        counts.append(count[0])
        await asyncio.sleep(1)
        count[0] -= 1

    button.on_click(cb)

    serve_and_request(button)

    doc = list(button._models.values())[0][0].document
    with set_curdoc(doc):
        for _ in range(5):
            button.clicks += 1

    # Checks whether Button on_click callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_async_local_state(server_implementation, bokeh_curdoc):
    docs = {}

    async def task():
        await asyncio.sleep(0.5)
        docs[state.curdoc] = []
        for _ in range(5):
            await asyncio.sleep(0.1)
            docs[state.curdoc].append(state.curdoc)

    def app():
        state.execute(task)
        return 'My app'

    serve_and_request(app, n=3)

    # Ensure state.curdoc was consistent despite asyncio context switching
    wait_until(lambda: len(docs) == 3)
    wait_until(lambda: all([len(set(docs)) == 1 and docs[0] is doc for doc, docs in docs.items()]))


def test_server_async_local_state_nested_tasks(server_implementation, bokeh_curdoc):
    docs = {}
    _tasks = set()

    async def task(depth=1):
        await asyncio.sleep(0.5)
        if depth > 0:
            _task = asyncio.ensure_future(task(depth-1))
            _tasks.add(_task)
            _task.add_done_callback(_tasks.discard)
        docs[state.curdoc] = []
        for _ in range(10):
            await asyncio.sleep(0.1)
            docs[state.curdoc].append(state.curdoc)

    def app():
        state.execute(task)
        return 'My app'

    serve_and_request(app, n=3)

    # Ensure state.curdoc was consistent despite asyncio context switching
    wait_until(lambda: len(docs) == 3)
    wait_until(lambda: all(len(set(docs)) == 1 and docs[0] is doc for doc, docs in docs.items()))


def test_serve_config_per_session_state(server_implementation):
    CSS1 = 'body { background-color: red }'
    CSS2 = 'body { background-color: green }'
    def app1():
        config.raw_css = [CSS1]
    def app2():
        config.raw_css = [CSS2]

    port1, port2 = get_open_ports(n=2)
    serve_and_wait(app1, port=port1)
    serve_and_wait(app2, port=port2)

    r1 = requests.get(f"http://localhost:{port1}/").content.decode('utf-8')
    r2 = requests.get(f"http://localhost:{port2}/").content.decode('utf-8')

    assert CSS1 not in config.raw_css
    assert CSS2 not in config.raw_css
    assert CSS1 in r1
    assert CSS2 not in r1
    assert CSS1 not in r2
    assert CSS2 in r2


def test_server_on_session_created(server_implementation):
    session_contexts = []
    def append_session(session_context):
        session_contexts.append(session_context)
    state.on_session_created(append_session)

    html = Markdown('# Title')

    serve_and_request(html, n=3)

    assert len(session_contexts) == 3


#@pytest.mark.parametrize('server_implementation', ["tornado", "fastapi"], indirect=True)
def test_server_on_session_destroyed():
    session_contexts = []
    def append_session(session_context):
        session_contexts.append(session_context)
    state.on_session_destroyed(append_session)

    html = Markdown('# Title')

    serve_and_request(html, n=3, check_unused_sessions_milliseconds=500, unused_session_lifetime_milliseconds=500)

    wait_until(lambda: len(session_contexts) == 3)


# This test seem to fail if run after:
# - test_server_async_local_state_nested_tasks
# - test_server_async_local_state
def test_server_session_info():
    with config.set(session_history=-1):
        html = Markdown('# Title')

        serve_and_request(html)

        assert state.session_info['total'] == 1
        assert len(state.session_info['sessions']) == 1
        sid, session = list(state.session_info['sessions'].items())[0]
        assert session['user_agent'].startswith('python-requests')
        assert state.session_info['live'] == 0

        doc = list(html._documents.keys())[0]
        session_context = param.Parameterized()
        request = param.Parameterized()
        request.arguments = {}
        session_context.request = request
        session_context._document = doc
        session_context.id = sid
        doc._session_context = weakref.ref(session_context)
        with set_curdoc(doc):
            state._init_session(None)
            assert state.session_info['live'] == 1

    html._server_destroy(session_context)
    state._destroy_session(session_context)
    assert state.session_info['live'] == 0


def test_server_periodic_async_callback(server_implementation, threads):
    counts = []

    async def cb(count=[0]):
        counts.append(count[0])
        count[0] += 1

    def app():
        button = Button(name='Click')
        state.add_periodic_callback(cb, 100)
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)
        return button

    serve_and_request(app)

    wait_until(lambda: len(counts) >= 5 and counts == list(range(len(counts))))


def test_server_cancel_task(server_implementation):
    state.cache['count'] = 0
    def periodic_cb():
        state.cache['count'] += 1

    def app():
        state.schedule_task('periodic', periodic_cb, period='0.1s')
        return '# state.schedule test'

    serve_and_request(app)

    wait_until(lambda: state.cache['count'] > 0)
    state.cancel_task('periodic')
    count = state.cache['count']
    time.sleep(0.5)
    assert state.cache['count'] == count


async def _async_erroring_cb():
    raise ValueError("An erroring callback")

def _sync_erroring_cb():
    raise ValueError("An erroring callback")

@pytest.mark.parametrize(
    'threadpool, cb', [
        (2, _async_erroring_cb),
        (None, _async_erroring_cb),
        (2, _sync_erroring_cb),
        (None, _sync_erroring_cb)
])
def test_server_periodic_callback_error_logged(caplog, server_implementation, threadpool, cb):
    """Ensure errors in periodic callbacks appear in the logs"""
    loggers_to_check = [logging.getLogger(x) for x in ('panel','bokeh')]
    orig_level_propagate = [(l.level,l.propagate) for l in loggers_to_check]
    orig_threads = config.nthreads
    repeats = 3

    try:
        config.nthreads = threadpool
        for l in loggers_to_check:
            l.propagate = True
            l.setLevel(logging.WARNING)

        def app():
            state.add_periodic_callback(cb, 100, repeats)
            def loaded():
                state._schedule_on_load(state.curdoc, None)
            state.execute(loaded, schedule=True)
            return Row()

        serve_and_request(app)
        time.sleep(1)
        num_errors_logged = caplog.text.count('ValueError: An erroring callback')
        assert num_errors_logged == repeats
    finally:
        for l,level_prop in zip(loggers_to_check,orig_level_propagate):
            l.setLevel(level_prop[0])
            l.propagate = level_prop[1]
        config.nthreads = orig_threads


def test_server_schedule_repeat(server_implementation):
    state.cache['count'] = 0
    def periodic_cb():
        state.cache['count'] += 1

    def app():
        state.schedule_task('periodic', periodic_cb, period='0.5s')
        return '# state.schedule test'

    serve_and_request(app)

    wait_until(lambda: state.cache['count'] > 0)


def test_server_schedule_threaded(server_implementation, threads):
    counts = []
    def periodic_cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] += -1

    def app():
        state.schedule_task('periodic1', periodic_cb, period='0.5s', threaded=True)
        state.schedule_task('periodic2', periodic_cb, period='0.5s', threaded=True)
        return '# state.schedule test'

    serve_and_request(app)

    # Checks whether scheduled callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_schedule_at(server_implementation):
    def periodic_cb():
        state.cache['at'] = dt.datetime.now()

    scheduled = []

    def app():
        scheduled.append(dt.datetime.now() + dt.timedelta(seconds=0.57))
        state.schedule_task('periodic', periodic_cb, at=scheduled[0])
        return '# state.schedule test'

    serve_and_request(app)

    # Check callback was executed within small margin of error
    wait_until(lambda: 'at' in state.cache)
    assert abs(state.cache['at'] - scheduled[0]) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0


def test_server_schedule_at_iterator(server_implementation):
    state.cache['at'] = []
    def periodic_cb():
        state.cache['at'].append(dt.datetime.now())

    scheduled = []

    def schedule():
        yield from scheduled

    def app():
        scheduled.extend([
            dt.datetime.now() + dt.timedelta(seconds=0.57),
            dt.datetime.now() + dt.timedelta(seconds=0.86)
        ])
        state.schedule_task('periodic', periodic_cb, at=schedule())
        return '# state.schedule test'

    serve_and_request(app)

    # Check callbacks were executed within small margin of error
    wait_until(lambda: len(state.cache['at']) == 2)
    assert abs(state.cache['at'][0] - scheduled[0]) < dt.timedelta(seconds=0.2)
    assert abs(state.cache['at'][1] - scheduled[1]) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0


def test_server_schedule_at_callable(server_implementation):
    state.cache['at'] = []
    def periodic_cb():
        state.cache['at'].append(dt.datetime.now())

    scheduled = []

    def schedule(siter, utcnow):
        return next(siter)

    def app():
        scheduled[:] = [
            dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=s)
            for s in (0.57, 0.86)
        ]
        state.schedule_task('periodic', periodic_cb, at=partial(schedule, iter(scheduled)))
        return '# state.schedule test'

    serve_and_request(app)

    # Check callbacks were executed within small margin of error
    wait_until(lambda: len(state.cache['at']) == 2)

    # Convert scheduled times to local time
    converted = [s.replace(tzinfo=dt.timezone.utc).astimezone().replace(tzinfo=None) for s in scheduled]
    assert abs(state.cache['at'][0] - converted[0]) < dt.timedelta(seconds=0.2)
    assert abs(state.cache['at'][1] - converted[1]) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0


@pytest.mark.xdist_group(name="server")
def test_server_reuse_sessions(reuse_sessions):
    def app(counts=[0]):
        content = f'# Count {counts[0]}'
        counts[0] += 1
        return content

    r1, r2 = serve_and_request(app, n=2)

    assert len(state._sessions) == 1
    assert ('/', 'default') in state._sessions

    session = state._sessions[('/', 'default')]

    assert session.token in r1.content.decode('utf-8')
    assert session.token not in r2.content.decode('utf-8')


@pytest.mark.xdist_group(name="server")
def test_server_reuse_sessions_with_session_key_func(port, reuse_sessions):
    config.session_key_func = lambda r: (r.path, r.arguments.get('arg', [''])[0])
    def app(counts=[0]):
        if 'arg' in state.session_args:
            title = state.session_args['arg'][0].decode('utf-8')
        else:
            title = 'Empty'
        content = f"# Count {counts[0]}"
        tmpl = BootstrapTemplate(title=title)
        tmpl.main.append(content)
        counts[0] += 1
        return tmpl

    serve_and_wait(app, port=port)

    r1 = requests.get(f"http://localhost:{port}/?arg=foo")
    r2 = requests.get(f"http://localhost:{port}/?arg=bar")

    assert len(state._sessions) == 2
    assert ('/', b'foo') in state._sessions
    assert ('/', b'bar') in state._sessions

    session1, session2 = state._sessions.values()
    assert session1.token in r1.content.decode('utf-8')
    assert session2.token in r2.content.decode('utf-8')


@pytest.mark.xdist_group(name="server")
def test_show_server_info(html_server_session, markdown_server_session):
    *_, html_port = html_server_session
    *_, markdown_port = markdown_server_session
    server_info = repr(state)
    assert f"localhost:{html_port} - HTML" in server_info
    assert f"localhost:{markdown_port} - Markdown" in server_info


@pytest.mark.xdist_group(name="server")
def test_kill_all_servers(html_server_session, markdown_server_session):
    _, server_1, *_ = html_server_session
    _, server_2, *_ = markdown_server_session
    state.kill_all_servers()
    assert server_1._stopped
    assert server_2._stopped


@pytest.mark.xdist_group(name="server")
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


def test_serve_can_serve_panel_app_from_file(server_implementation):
    path = pathlib.Path(__file__).parent / "io"/"panel_app.py"
    server = get_server({"panel-app": path})
    assert "/panel-app" in server._tornado.applications


def test_serve_can_serve_bokeh_app_from_file(server_implementation):
    path = pathlib.Path(__file__).parent / "io"/"bk_app.py"
    server = get_server({"bk-app": path})
    assert "/bk-app" in server._tornado.applications



def test_server_on_load_after_init_with_threads(server_implementation, threads):
    loaded = []

    def cb():
        loaded.append((state.curdoc, state.loaded))

    def app():
        state.onload(cb)
        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)
        return 'App'

    serve_and_request(app)

    wait_until(lambda: len(loaded) == 1)

    doc = loaded[0][0]
    with set_curdoc(doc):
        state.onload(cb)

    wait_until(lambda: len(loaded) == 2)
    assert loaded == [(doc, False), (doc, True)]


def test_server_on_load_after_init(server_implementation):
    loaded = []

    def cb():
        loaded.append((state.curdoc, state.loaded))

    def app():
        state.onload(cb)
        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)
        return 'App'

    serve_and_request(app)

    wait_until(lambda: len(loaded) == 1)

    doc = loaded[0][0]
    with set_curdoc(doc):
        state.onload(cb)

    wait_until(lambda: len(loaded) == 2)
    assert loaded == [(doc, False), (doc, True)]


def test_server_on_load_during_load(server_implementation, threads):
    loaded = []

    def cb():
        loaded.append(state.loaded)

    def cb2():
        state.onload(cb)

    def app():
        state.onload(cb)
        state.onload(cb2)
        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)
        return 'App'

    serve_and_request(app)

    # Checks whether onload callback was executed twice once before and once during load
    wait_until(lambda: loaded == [False, False])


def test_server_thread_pool_on_load(server_implementation, threads):
    counts = []

    def cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    def app():
        state.onload(cb, threaded=True)
        state.onload(cb, threaded=True)

        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)

        return 'App'

    serve_and_request(app)

    # Checks whether onload callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_execute(server_implementation, threads):
    counts = []

    def cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    def app():
        state.execute(cb, schedule='thread')
        state.execute(cb, schedule='thread')
        return 'App'

    serve_and_request(app)

    # Checks whether execute was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_defer_load(server_implementation, threads):
    counts = []

    def cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        value = counts[-1]
        count[0] -= 1
        return value

    def app():
        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)

        return Row(
            ParamFunction(cb, defer_load=True),
            ParamFunction(cb, defer_load=True),
        )

    serve_and_request(app)

    # Checks whether defer_load callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_change_event(server_implementation, threads):
    button = Button(name='Click')
    button2 = Button(name='Click')

    counts = []

    def cb(event, count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    button.on_click(cb)
    button2.on_click(cb)
    layout = Row(button, button2)

    serve_and_request(layout)

    model = list(layout._models.values())[0][0]
    doc = model.document
    with set_curdoc(doc):
        button._server_change(doc, model.ref['id'], None, 'clicks', 0, 1)
        button2._server_change(doc, model.ref['id'], None, 'clicks', 0, 1)

    # Checks whether Button on_click callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_bokeh_event(server_implementation, threads):
    import pandas as pd

    df = pd.DataFrame([[1, 1], [2, 2]], columns=['A', 'B'])

    tabulator = Tabulator(df)

    counts = []

    def cb(event, count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    tabulator.on_edit(cb)

    serve_and_request(tabulator)

    model = list(tabulator._models.values())[0][0]
    event = TableEditEvent(model, 'A', 0)
    for _ in range(5):
        tabulator._server_event(model.document, event)

    # Checks whether Tabulator on_edit callback was executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_periodic(server_implementation, threads):
    counts = []

    def cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    def app():
        button = Button(name='Click')
        state.add_periodic_callback(cb, 100)
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)
        return button

    serve_and_request(app)

    # Checks whether periodic callbacks were executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_onload(threads):
    counts = []

    def app(count=[0]):
        button = Button(name='Click')
        def onload():
            count[0] += 1
            counts.append(count[0])
            time.sleep(2)
            count[0] -= 1

        state.onload(onload)

        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)

        return button

    serve_and_request(app, n=2)

    # Checks whether onload callbacks were executed concurrently
    wait_until(lambda: len(counts) > 0 and max(counts) > 1)


def test_server_thread_pool_busy(server_implementation, threads):
    button = Button(name='Click')
    clicks = []

    def cb(event):
        time.sleep(0.5)

    def simulate_click():
        click = ButtonClick(model=None)
        clicks.append(click)
        button._comm_event(state.curdoc, click)

    button.on_click(cb)

    def app():
        state.curdoc.add_next_tick_callback(simulate_click)
        state.curdoc.add_next_tick_callback(simulate_click)
        state.curdoc.add_next_tick_callback(simulate_click)
        return button

    serve_and_request(app, suffix="/")

    wait_until(lambda: len(clicks) == 3 and state._busy_counter == 0 and not state.busy)


def test_server_async_onload(threads):
    counts = []

    def app(count=[0]):
        button = Button(name='Click')
        async def onload():
            count[0] += 1
            counts.append(count[0])
            await asyncio.sleep(2)
            count[0] -= 1

        state.onload(onload)

        # Simulate rendering
        def loaded():
            state._schedule_on_load(state.curdoc, None)
        state.execute(loaded, schedule=True)

        return button

    serve_and_request(app, n=2)

    # Checks whether onload callbacks were executed concurrently
    wait_until(lambda: len(counts) and max(counts) >= 2)


class CustomBootstrapTemplate(BootstrapTemplate):

    _css = ['./assets/custom.css']


def test_server_template_custom_resources(port):
    template = CustomBootstrapTemplate()

    r = serve_and_request({'template': template}, suffix="/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css")

    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')

@reverse_proxy_available
def test_server_template_custom_resources_on_proxy(reverse_proxy):
    template = CustomBootstrapTemplate()

    port, proxy = reverse_proxy
    r = serve_and_request(
        {'template': template}, port=port, proxy=proxy,
        suffix="/proxy/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"
    )

    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')

@reverse_proxy_available
def test_server_ico_path_on_proxy(reverse_proxy):
    md = Markdown('# Favicon test')

    ico_path = DIST_DIR / "images" / "icon-32x32.png"
    port, proxy = reverse_proxy
    r = serve_and_request(
        {'app': md}, port=port, proxy=proxy, ico_path=ico_path,
        suffix="/proxy/app"
    )

    assert '<link rel="icon" href="./favicon.ico"' in r.content.decode('utf-8')
    ico = requests.get(f"http://localhost:{proxy}/proxy/favicon.ico")
    assert ico.content == ico_path.read_bytes()

def test_server_template_custom_resources_with_prefix(port):
    template = CustomBootstrapTemplate()

    path = "/prefix/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"
    r = serve_and_request({'template': template}, prefix='/prefix', suffix=path)
    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')

@reverse_proxy_available
def test_server_template_custom_resources_with_prefix_and_proxy(reverse_proxy):
    (port, proxy) = reverse_proxy
    template = CustomBootstrapTemplate()

    path = "/proxy/prefix/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"
    r = serve_and_request({'template': template}, port=port, proxy=proxy, prefix='/prefix', suffix=path)

    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')

def test_server_template_custom_resources_with_prefix_relative_url(port):
    template = CustomBootstrapTemplate()

    r = serve_and_request({'template': template}, prefix='/prefix', port=port, suffix='/prefix/template')

    assert 'href="components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in r.content.decode('utf-8')

@reverse_proxy_available
def test_server_template_custom_resources_with_prefix_and_proxy_relative_url(reverse_proxy):
    template = CustomBootstrapTemplate()

    (port, proxy) = reverse_proxy
    r = serve_and_request({'template': template}, prefix='/prefix', port=port, proxy=proxy, suffix='/proxy/prefix/template')

    assert 'href="components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in r.content.decode('utf-8')

def test_server_template_custom_resources_with_subpath_and_prefix_relative_url(port):
    template = CustomBootstrapTemplate()

    r = serve_and_request({'/subpath/template': template}, port=port, prefix='/prefix', suffix='/prefix/subpath/template')

    assert 'href="../components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in r.content.decode('utf-8')

@reverse_proxy_available
def test_server_template_custom_resources_with_subpath_and_prefix_and_proxy_relative_url(reverse_proxy):
    template = CustomBootstrapTemplate()

    port, proxy = reverse_proxy
    r = serve_and_request({'/subpath/template': template}, port=port, proxy=proxy, prefix='/prefix', suffix='/proxy/prefix/subpath/template')

    assert 'href="../components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in r.content.decode('utf-8')


class CustomComponent(ReactiveHTML):

    _extension_name = 'custom'

    __css__ = ['./assets/custom.css']


def test_server_component_custom_resources(port):
    component = CustomComponent()

    path = "/components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css"
    r = serve_and_request({'component': component}, suffix=path, port=port)

    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_component_custom_resources_with_prefix(port):
    component = CustomComponent()

    r = serve_and_request(
        {'component': component}, prefix='/prefix', port=port,
        suffix="/prefix/components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css"
    )

    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_component_custom_resources_with_prefix_relative_url(port):
    component = CustomComponent()

    r = serve_and_request({'component': component}, port=port, prefix='/prefix', suffix='/prefix/component')

    assert f'href="components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css?v={JS_VERSION}"' in r.content.decode('utf-8')


def test_server_component_custom_resources_with_subpath_and_prefix_relative_url(port):
    component = CustomComponent()

    r = serve_and_request({'/subpath/component': component}, port=port, prefix='/prefix', suffix='/prefix/subpath/component')

    assert f'href="../components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css?v={JS_VERSION}"' in r.content.decode('utf-8')


def test_server_component_css_with_prefix_relative_url(port):
    component = Terminal()

    r = serve_and_request({'component': component}, suffix='/component', port=port)

    assert 'href="static/extensions/panel/bundled/terminal/xterm@4.11.0/css/xterm.css' in r.content.decode('utf-8')


def test_server_component_css_with_subpath_and_prefix_relative_url(port):
    component = Terminal()

    r = serve_and_request({'/subpath/component': component}, prefix='/prefix', suffix='/prefix/subpath/component', port=port)

    assert 'href="../static/extensions/panel/bundled/terminal/xterm@4.11.0/css/xterm.css' in r.content.decode('utf-8')


def synchronous_handler(event=None):
    raise Exception()

async def async_handler(event=None):
    raise Exception()

@pytest.mark.parametrize(
    'threads, handler', [
        ('threads', synchronous_handler),
        ('nothreads', synchronous_handler),
        ('threads', async_handler),
        ('nothreads', async_handler)
])
def test_server_exception_handler_bokeh_event(threads, handler, request):
    request.getfixturevalue(threads)

    exceptions = []

    def exception_handler(e):
        exceptions.append(e)

    def simulate_click():
        button._comm_event(state.curdoc, ButtonClick(model=None))

    button = Button()
    button.on_click(handler)

    def app():
        config.exception_handler = exception_handler
        state.curdoc.add_next_tick_callback(simulate_click)
        return button

    serve_and_request(app)

    wait_until(lambda: len(exceptions) == 1)


@pytest.mark.parametrize(
    'threads, handler', [
        ('threads', synchronous_handler),
        ('nothreads', synchronous_handler),
        ('threads', async_handler),
        ('nothreads', async_handler)
])
def test_server_exception_handler_async_change_event(threads, handler, request):
    request.getfixturevalue(threads)

    exceptions = []

    def exception_handler(e):
        exceptions.append(e)

    def simulate_input():
        text_input._server_change(state.curdoc, ref=None, subpath=None, attr='value', old='', new='foo')

    text_input = TextInput()
    text_input.param.watch(handler, 'value')

    def app():
        config.exception_handler = exception_handler
        state.curdoc.add_next_tick_callback(simulate_input)
        return text_input

    serve_and_request(app)

    wait_until(lambda: len(exceptions) == 1)


@pytest.mark.parametrize(
    'threads, handler', [
        ('threads', synchronous_handler),
        ('nothreads', synchronous_handler),
        ('threads', async_handler),
        ('nothreads', async_handler)
])
def test_server_exception_handler_async_onload_event(threads, handler, request):
    request.getfixturevalue(threads)

    exceptions = []

    def exception_handler(e):
        exceptions.append(e)

    def loaded():
        state._schedule_on_load(state.curdoc, None)

    text_input = TextInput()

    def app():
        config.exception_handler = exception_handler
        state.onload(handler)
        state.curdoc.add_next_tick_callback(loaded)
        return text_input

    serve_and_request(app)

    wait_until(lambda: len(exceptions) == 1)


def test_server_no_warning_empty_layout(caplog):

    bk_logger = logging.getLogger('bokeh')
    old_level = bk_logger.level
    old_propagate = bk_logger.propagate
    try:
        # Test pretty dependent on how Bokeh sets up its logging system
        bk_logger.propagate = True
        bk_logger.setLevel(logging.WARNING)

        app = Row()

        serve_and_request(app)

        time.sleep(1)

        for rec in caplog.records:
            if rec.levelname == 'WARNING':
                assert 'EMPTY_LAYOUT' not in rec.message
    finally:
        bk_logger.setLevel(old_level)
        bk_logger.propagate = old_propagate


def test_server_threads_save(threads, tmp_path):
    # https://github.com/holoviz/panel/issues/5957

    button = Button()
    fsave = tmp_path / 'button.html'

    def cb(event):
        button.save(fsave)

    def simulate_click():
        button._comm_event(state.curdoc, ButtonClick(model=None))

    button.on_click(cb)

    def app():
        state.curdoc.add_next_tick_callback(simulate_click)
        return button

    serve_and_request(app)

    wait_until(lambda: fsave.exists())
