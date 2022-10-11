import asyncio
import datetime as dt
import os
import pathlib
import time
import weakref

import param
import pytest
import requests

from bokeh.events import ButtonClick

from panel.config import config
from panel.io import state
from panel.io.resources import DIST_DIR
from panel.io.server import (
    INDEX_HTML, get_server, serve, set_curdoc,
)
from panel.layout import Row
from panel.models import HTML as BkHTML
from panel.models.tabulator import TableEditEvent
from panel.pane import Markdown
from panel.reactive import ReactiveHTML
from panel.template import BootstrapTemplate
from panel.tests.util import wait_until
from panel.widgets import (
    Button, Tabulator, Terminal, TextInput,
)


def test_get_server(html_server_session):
    html, server, session = html_server_session

    assert server.port == 6000
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


def test_server_static_dirs(port):
    html = Markdown('# Title')

    static = {'tests': os.path.dirname(__file__)}
    serve(html, port=port, threaded=True, static_dirs=static, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/tests/test_server.py")
    with open(__file__, encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_root_handler(port):
    html = Markdown('# Title')

    serve(
        {'app': html}, port=port, threaded=True, show=False, use_index=True,
        index=INDEX_HTML, redirect_root=False
    )

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/")

    assert 'href="./app"' in r.content.decode('utf-8')


def test_server_template_static_resources(port):
    template = BootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")
    with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_template_static_resources_with_prefix(port):
    template = BootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/static/extensions/panel/bundled/bootstraptemplate/bootstrap.css")
    with open(DIST_DIR / 'bundled' / 'bootstraptemplate' / 'bootstrap.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_template_static_resources_with_prefix_relative_url(port):
    template = BootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/template")
    content = r.content.decode('utf-8')
    assert 'href="static/extensions/panel/bundled/bootstraptemplate/bootstrap.css"' in content


def test_server_template_static_resources_with_subpath_and_prefix_relative_url(port):
    template = BootstrapTemplate()

    serve({'/subpath/template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/subpath/template")
    content = r.content.decode('utf-8')
    assert 'href="../static/extensions/panel/bundled/bootstraptemplate/bootstrap.css"' in content


def test_server_extensions_on_root(port):
    html = Markdown('# Title')

    serve(html, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/static/extensions/panel/css/loading.css")
    assert r.ok


def test_autoload_js(port):
    html = Markdown('# Title')
    app_name = 'test'
    serve({app_name: html}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(0.5)

    args = f"bokeh-autoload-element=1002&bokeh-app-path=/{app_name}&bokeh-absolute-url=http://localhost:{port}/{app_name}"
    r = requests.get(f"http://localhost:{port}/{app_name}/autoload.js?{args}")

    assert r.status_code == 200
    assert f"http://localhost:{port}/static/extensions/panel/css/alerts.css" in r.content.decode('utf-8')


def test_server_async_callbacks(port):
    button = Button(name='Click')

    counts = []

    async def cb(event, count=[0]):
        count[0] += 1
        counts.append(count[0])
        await asyncio.sleep(1)
        count[0] -= 1

    button.on_click(cb)

    serve(button, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    doc = list(button._models.values())[0][0].document
    with set_curdoc(doc):
        for _ in range(5):
            button.clicks += 1

    # Wait for callbacks to be scheduled
    time.sleep(2)

    # Ensure multiple callbacks started concurrently
    assert max(counts) > 1


def test_server_async_local_state(port):
    docs = {}

    async def task():
        curdoc = state.curdoc
        await asyncio.sleep(0.5)
        docs[curdoc] = []
        for i in range(5):
            await asyncio.sleep(0.1)
            docs[curdoc].append(state.curdoc)

    def app():
        state.execute(task)
        return 'My app'

    serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    for i in range(3):
        requests.get(f"http://localhost:{port}/")

    # Wait for callbacks to be scheduled
    time.sleep(2)

    # Ensure state.curdoc was consistent despite asyncio context switching
    assert len(docs) == 3
    assert all([len(set(docs)) == 1 and docs[0] is doc for doc, docs in docs.items()])


def test_server_async_local_state_nested_tasks(port):
    docs = {}

    async def task(depth=1):
        curdoc = state.curdoc
        await asyncio.sleep(0.5)
        if depth > 0:
            asyncio.ensure_future(task(depth-1))
        docs[curdoc] = []
        for i in range(10):
            await asyncio.sleep(0.1)
            docs[curdoc].append(state.curdoc)

    def app():
        state.execute(task)
        return 'My app'

    serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    for i in range(3):
        requests.get(f"http://localhost:{port}/")

    # Wait for callbacks to be scheduled
    time.sleep(2)

    # Ensure state.curdoc was consistent despite asyncio context switching
    assert len(docs) == 3
    assert all(len(set(docs)) == 1 and docs[0] is doc for doc, docs in docs.items())


def test_serve_config_per_session_state():
    CSS1 = 'body { background-color: red }'
    CSS2 = 'body { background-color: green }'
    def app1():
        config.raw_css = [CSS1]
    def app2():
        config.raw_css = [CSS2]


    port1, port2 = 7001, 7002
    serve(app1, port=port1, threaded=True, show=False)
    serve(app2, port=port2, threaded=True, show=False)

    # Wait for servers to start
    time.sleep(1)

    r1 = requests.get(f"http://localhost:{port1}/").content.decode('utf-8')
    r2 = requests.get(f"http://localhost:{port2}/").content.decode('utf-8')

    assert CSS1 not in config.raw_css
    assert CSS2 not in config.raw_css
    assert CSS1 in r1
    assert CSS2 not in r1
    assert CSS1 not in r2
    assert CSS2 in r2


def test_server_session_info(port):
    with config.set(session_history=-1):
        html = Markdown('# Title')

        serve(html, port=port, threaded=True, show=False)

        # Wait for server to start
        time.sleep(1)

        requests.get(f"http://localhost:{port}/")

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

    state.curdoc = None
    html._server_destroy(session_context)
    state._destroy_session(session_context)
    assert state.session_info['live'] == 0


def test_server_schedule_repeat(port):
    state.cache['count'] = 0
    def periodic_cb():
        state.cache['count'] += 1

    def app():
        state.schedule_task('periodic', periodic_cb, period='0.5s')
        return '# state.schedule test'

    server = serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    # Wait for periodic execution
    time.sleep(1)

    assert state.cache['count']

    server.stop()


def test_server_schedule_at(port):
    def periodic_cb():
        state.cache['at'] = dt.datetime.now()

    scheduled = dt.datetime.now() + dt.timedelta(seconds=1.57)

    def app():
        state.schedule_task('periodic', periodic_cb, at=scheduled)
        return '# state.schedule test'

    server = serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    # Wait for callback to be executed
    time.sleep(1)

    # Check callback was executed within small margin of error
    assert 'at' in state.cache
    assert abs(state.cache['at'] - scheduled) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0

    server.stop()


def test_server_schedule_at_iterator(port):
    state.cache['at'] = []
    def periodic_cb():
        state.cache['at'].append(dt.datetime.now())

    scheduled1 = dt.datetime.now() + dt.timedelta(seconds=1.57)
    scheduled2 = dt.datetime.now() + dt.timedelta(seconds=1.86)

    def schedule():
        yield scheduled1
        yield scheduled2

    def app():
        state.schedule_task('periodic', periodic_cb, at=schedule())
        return '# state.schedule test'

    server = serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    # Wait for callbacks to be executed
    time.sleep(1)

    # Check callbacks were executed within small margin of error
    assert len(state.cache['at']) == 2
    assert abs(state.cache['at'][0] - scheduled1) < dt.timedelta(seconds=0.2)
    assert abs(state.cache['at'][1] - scheduled2) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0

    server.stop()


def test_server_schedule_at_callable(port):
    state.cache['at'] = []
    def periodic_cb():
        state.cache['at'].append(dt.datetime.now())

    scheduled = [
        dt.datetime.utcnow() + dt.timedelta(seconds=1.57),
        dt.datetime.utcnow() + dt.timedelta(seconds=1.86)
    ]
    siter = iter(scheduled)

    def schedule(utcnow):
        return next(siter)

    def app():
        state.schedule_task('periodic', periodic_cb, at=schedule)
        return '# state.schedule test'

    server = serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    # Wait for callback to be executed
    time.sleep(1)

    # Convert scheduled times to local time
    scheduled = [
        s.replace(tzinfo=dt.timezone.utc).astimezone().replace(tzinfo=None)
        for s in scheduled
    ]

    # Check callbacks were executed within small margin of error
    assert len(state.cache['at']) == 2
    assert abs(state.cache['at'][0] - scheduled[0]) < dt.timedelta(seconds=0.2)
    assert abs(state.cache['at'][1] - scheduled[1]) < dt.timedelta(seconds=0.2)
    assert len(state._scheduled) == 0

    server.stop()


def test_show_server_info(html_server_session, markdown_server_session):
    server_info = repr(state)
    assert "localhost:6000 - HTML" in server_info
    assert "localhost:6001 - Markdown" in server_info


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


def test_server_thread_pool_change_event(threads, port):
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

    serve(layout, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    model = list(layout._models.values())[0][0]
    doc = model.document
    with set_curdoc(doc):
        button._server_change(doc, model.ref['id'], None, 'clicks', 0, 1)
        button2._server_change(doc, model.ref['id'], None, 'clicks', 0, 1)

    # Checks whether Button on_click callback was executed concurrently
    wait_until(lambda: len(counts) > 0)
    wait_until(lambda: max(counts) == 2)


def test_server_thread_pool_bokeh_event(threads, port):
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

    serve(tabulator, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    model = list(tabulator._models.values())[0][0]
    event = TableEditEvent(model, 'A', 0)
    for _ in range(5):
        tabulator._server_event(model.document, event)

    # Wait for callbacks to be scheduled
    time.sleep(1)

    # Checks whether Tabulator on_edit callback was executed concurrently
    assert max(counts) > 1


def test_server_thread_pool_periodic(threads, port):
    counts = []

    def cb(count=[0]):
        count[0] += 1
        counts.append(count[0])
        time.sleep(0.5)
        count[0] -= 1

    def app():
        button = Button(name='Click')
        state.add_periodic_callback(cb, 100)
        return button

    serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    # Wait for callbacks to be scheduled
    time.sleep(1)

    # Checks whether periodic callbacks were executed concurrently
    assert max(counts) >= 2


def test_server_thread_pool_onload(threads, port):
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

    serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")
    requests.get(f"http://localhost:{port}/")

    time.sleep(1)

    # Checks whether onload callbacks were executed concurrently
    assert max(counts) >= 2


def test_server_async_onload(threads, port):
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

    serve(app, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")
    requests.get(f"http://localhost:{port}/")

    time.sleep(1)

    # Checks whether onload callbacks were executed concurrently
    assert max(counts) >= 2


class CustomBootstrapTemplate(BootstrapTemplate):

    _css = './assets/custom.css'


def test_server_template_custom_resources(port):
    template = CustomBootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css")
    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_template_custom_resources_with_prefix(port):
    template = CustomBootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css")
    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_template_custom_resources_with_prefix_relative_url(port):
    template = CustomBootstrapTemplate()

    serve({'template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/template")
    content = r.content.decode('utf-8')
    assert 'href="components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in content


def test_server_template_custom_resources_with_subpath_and_prefix_relative_url(port):
    template = CustomBootstrapTemplate()

    serve({'/subpath/template': template}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/subpath/template")
    content = r.content.decode('utf-8')
    assert 'href="../components/panel.tests.test_server/CustomBootstrapTemplate/_css/assets/custom.css"' in content


class CustomComponent(ReactiveHTML):

    __css__ = ['./assets/custom.css']


def test_server_component_custom_resources(port):
    component = CustomComponent()

    serve({'component': component}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css")
    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_component_custom_resources_with_prefix(port):
    component = CustomComponent()

    serve({'component': component}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css")
    with open(pathlib.Path(__file__).parent / 'assets' / 'custom.css', encoding='utf-8') as f:
        assert f.read() == r.content.decode('utf-8').replace('\r\n', '\n')


def test_server_component_custom_resources_with_prefix_relative_url(port):
    component = CustomComponent()

    serve({'component': component}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/component")
    content = r.content.decode('utf-8')
    assert 'href="components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css"' in content


def test_server_component_custom_resources_with_subpath_and_prefix_relative_url(port):
    component = CustomComponent()

    serve({'/subpath/component': component}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/subpath/component")
    content = r.content.decode('utf-8')
    assert 'href="../components/panel.tests.test_server/CustomComponent/__css__/assets/custom.css"' in content


def test_server_component_css_with_prefix_relative_url(port):
    component = Terminal()

    serve({'component': component}, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/component")
    content = r.content.decode('utf-8')
    assert 'href="static/extensions/panel/bundled/terminal/xterm@4.11.0/css/xterm.css' in content


def test_server_component_css_with_subpath_and_prefix_relative_url(port):
    component = Terminal()

    serve({'/subpath/component': component}, port=port, threaded=True, show=False, prefix='prefix')

    # Wait for server to start
    time.sleep(1)

    r = requests.get(f"http://localhost:{port}/prefix/subpath/component")
    content = r.content.decode('utf-8')
    assert 'href="../static/extensions/panel/bundled/terminal/xterm@4.11.0/css/xterm.css' in content


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
def test_server_exception_handler_bokeh_event(threads, handler, port, request):
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

    serve(app, port=port, threaded=True, show=False)

    time.sleep(1)

    requests.get(f"http://localhost:{port}")

    time.sleep(0.5)

    assert len(exceptions) == 1

@pytest.mark.parametrize(
    'threads, handler', [
        ('threads', synchronous_handler),
        ('nothreads', synchronous_handler),
        ('threads', async_handler),
        ('nothreads', async_handler)
])
def test_server_exception_handler_async_change_event(threads, handler, port, request):
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

    serve(app, port=port, threaded=True, show=False)

    time.sleep(1)

    requests.get(f"http://localhost:{port}")

    time.sleep(0.5)

    assert len(exceptions) == 1


@pytest.mark.parametrize(
    'threads, handler', [
        ('threads', synchronous_handler),
        ('nothreads', synchronous_handler),
        ('threads', async_handler),
        ('nothreads', async_handler)
])
def test_server_exception_handler_async_onload_event(threads, handler, port, request):
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

    serve(app, port=port, threaded=True, show=False)

    time.sleep(1)

    requests.get(f"http://localhost:{port}")

    time.sleep(0.5)

    assert len(exceptions) == 1
