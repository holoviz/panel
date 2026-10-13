import json
import pathlib
import time

from urllib.parse import unquote

import pytest
import requests

pytest.importorskip("playwright")

from playwright.sync_api import TimeoutError, expect

from panel.io.resources import CDN_DIST, DIST_DIR

pytestmark = [pytest.mark.ui, pytest.mark.jupyter, pytest.mark.flaky(reruns=3)]


_notebooks: list[str] = []


@pytest.fixture
def nbclassic_server(jupyter_preview):
    """Use nbclassic as an extension of the shared Jupyter Server."""
    host, _ = jupyter_preview.split('/panel-preview/', 1)
    yield f'{host}/nbclassic'
    # A kernel outlives its notebook page, and the kernels left running
    # starved new ones on small runners.
    paths = {f'{name}.ipynb' for name in _notebooks}
    _notebooks.clear()
    session = requests.Session()
    session.get(f'{host}/nbclassic/tree', timeout=10).raise_for_status()
    headers = {'X-XSRFToken': session.cookies.get('_xsrf', '')}
    for notebook_session in session.get(f'{host}/api/sessions', timeout=10).json():
        if notebook_session['path'] in paths:
            session.delete(f'{host}/api/sessions/{notebook_session["id"]}', headers=headers, timeout=10)


def _record_kernel_frames(page):
    frames = []

    def on_websocket(ws):
        if '/api/kernels/' not in ws.url:
            return
        ws.on('framesent', lambda payload: frames.append((time.monotonic(), 'sent', payload)))
        ws.on('framereceived', lambda payload: frames.append((time.monotonic(), 'received', payload)))

    page.on('websocket', on_websocket)
    return frames


def _describe_frames(frames):
    t0 = frames[0][0] if frames else 0
    lines = []
    for t, direction, payload in frames:
        try:
            msg = json.loads(payload)
            what = f"{msg['header']['msg_type']} {msg.get('content', {}).get('execution_state', '')}"
        except Exception:
            what = f'<{len(payload)} bytes>'
        lines.append(f'{t - t0:7.2f}s {direction:8} {what}')
    return '\n'.join(lines[-40:])


def run_notebook(page, nbclassic_server, notebook_name, cells):
    """Open a notebook in nbclassic and run every cell through its UI."""
    _notebooks.append(notebook_name)
    host = nbclassic_server
    api_host = host.removesuffix('/nbclassic')
    notebook = {
        'cells': [
            {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': cell.splitlines(keepends=True),
            }
            for cell in cells
        ],
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python'},
        },
        'nbformat': 4,
        'nbformat_minor': 5,
    }
    session = requests.Session()
    session.get(f'{host}/tree', timeout=10).raise_for_status()
    response = session.put(
        f'{api_host}/api/contents/{notebook_name}.ipynb',
        json={'type': 'notebook', 'format': 'json', 'content': notebook},
        headers={'X-XSRFToken': session.cookies['_xsrf']},
        timeout=10,
    )
    response.raise_for_status()
    # Tells a stalled server or kernel apart from a request that was never sent.
    frames = _record_kernel_frames(page)
    page.goto(f'{host}/notebooks/{notebook_name}.ipynb')
    expect(page.locator('#notebook-container .code_cell').first).to_be_visible()
    # Cells executed before the kernel is ready never run.
    ready = (
        "window.Jupyter?.notebook?._fully_loaded && "
        "window.Jupyter.notebook.kernel?.is_connected() && "
        "Object.keys(window.Jupyter.notebook.kernel.info_reply).length > 0 && "
        "!window.Jupyter.notebook.kernel_busy"
    )
    try:
        page.wait_for_function(ready, timeout=5000)
    except TimeoutError:
        # nbclassic only asks a kernel for its info when it connects or starts,
        # so a request lost while the kernel starts leaves it waiting.
        page.evaluate("""() => {
            const kernel = window.Jupyter?.notebook?.kernel
            if (kernel?.is_connected() && Object.keys(kernel.info_reply).length === 0) {
                kernel.kernel_info((reply) => {
                    kernel.info_reply = reply.content
                    kernel.events.trigger('kernel_ready.Kernel', {kernel})
                })
            }
        }""")
        try:
            page.wait_for_function(ready)
        except TimeoutError as error:
            raise AssertionError(f'The kernel did not get ready, kernel frames:\n{_describe_frames(frames)}') from error
    page.evaluate('Jupyter.notebook.execute_all_cells()')
    # A queued cell has "*" as its prompt number.
    try:
        page.wait_for_function(
            "Jupyter.notebook.get_cells().every((cell) => typeof cell.input_prompt_number === 'number')"
        )
    except TimeoutError as error:
        raise AssertionError(f'The cells did not run, kernel frames:\n{_describe_frames(frames)}') from error
    page.wait_for_function("window.Jupyter && !window.Jupyter.notebook.kernel_busy")
    errors = page.locator('.output_error').all_inner_texts()
    assert not errors, '\n'.join(errors)


#: Hosts the bundled libraries originally come from. Panel must not need
#: them, so a notebook on a network that blocks them still renders.
PUBLIC_CDNS = ('cdn.jsdelivr.net', 'unpkg.com', 'cdn.plot.ly', 'api.mapbox.com')


def _serve_local_dist(page):
    """
    Serves Panel's CDN urls from the local build, so modes that resolve
    resources against the CDN (comms='ipywidgets', like VS Code) exercise
    this checkout rather than the last release.
    """
    dist = pathlib.Path(DIST_DIR)

    def fulfill(route):
        path = dist / unquote(route.request.url.split('?')[0].removeprefix(CDN_DIST))
        if path.is_file():
            route.fulfill(path=str(path))
        else:
            route.fallback()

    page.route(f'{CDN_DIST}**', fulfill)


def _enable_jupyter_bokeh(page):
    """
    Maps the widget module the way jupyter_bokeh's nbextension does, which
    is not necessarily enabled where the tests run.
    """
    page.add_init_script("""
    const timer = setInterval(() => {
      if (window.requirejs == null) {
        return
      }
      clearInterval(timer)
      window.requirejs.config({map: {'*': {'@bokeh/jupyter_bokeh': 'nbextensions/jupyter_bokeh/index'}}})
    }, 1)
    """)


@pytest.mark.parametrize('comms', ['default', 'ipywidgets'])
@pytest.mark.parametrize('mode', ['eager', 'inline', 'lazy'])
@pytest.mark.parametrize(
    ('extension', 'component', 'selector'),
    [
        ('tabulator', "pn.widgets.Tabulator(pd.DataFrame({'x': [1, 2, 3]}), height=160)", '.pnx-tabulator.tabulator'),
        ('perspective', "pn.pane.Perspective(pd.DataFrame({'x': [1, 2, 3]}), height=200)", 'perspective-viewer'),
        ('filedropper', 'pn.widgets.FileDropper(height=100)', '.filepond--root'),
        ('codeeditor', "pn.widgets.CodeEditor(value='print(1)', height=100)", '.ace_editor'),
        ('jsoneditor', "pn.widgets.JSONEditor(value={'answer': 42}, height=160)", '.jsoneditor'),
        ('echarts', "pn.pane.ECharts({'xAxis': {}, 'yAxis': {}, 'series': []}, height=180)", '[_echarts_instance_]'),
        ('vega', "pn.pane.Vega({'$schema': 'https://vega.github.io/schema/vega-lite/v5.json', 'mark': 'bar', 'data': {'values': []}}, height=180)", '.vega-embed'),
        ('deckgl', "pn.pane.DeckGL({'initialViewState': {'longitude': 0, 'latitude': 0, 'zoom': 1}, 'layers': []}, height=180)", '.deckgl canvas'),
        ('terminal', 'pn.widgets.Terminal(height=100)', '.xterm'),
        ('katex', "pn.pane.LaTeX(r'$E = mc^2$')", '.katex'),
        ('plotly', "pn.pane.Plotly({'data': [{'type': 'bar', 'y': [1, 2, 3]}], 'layout': {}}, height=200)", '.js-plotly-plot'),
    ],
    ids=[
        'tabulator', 'perspective', 'filedropper', 'codeeditor', 'jsoneditor',
        'echarts', 'vega', 'deckgl', 'terminal', 'katex', 'plotly',
    ],
)
def test_nbclassic_component_resources(page, nbclassic_server, extension, component, selector, mode, comms):
    """
    Load each bundled component independently through nbclassic resources,
    declared up front (eager), inlined, or only requested on render (lazy).

    comms='ipywidgets' renders through jupyter_bokeh's widget, the way VS
    Code renders Panel output.

    See https://github.com/holoviz/panel/issues/8750.
    """
    if comms == 'ipywidgets':
        pytest.importorskip('jupyter_bokeh')
        _enable_jupyter_bokeh(page)
    _serve_local_dist(page)
    for host in PUBLIC_CDNS:
        page.route(f'**://{host}/**', lambda route: route.abort())
    console_errors = []
    page.on('console', lambda message: console_errors.append(message.text) if message.type == 'error' else None)
    page.on('pageerror', lambda error: console_errors.append(str(error)))
    if mode == 'lazy':
        load = f"pn.extension(comms='{comms}', inline=False)"
    else:
        load = f"pn.extension('{extension}', comms='{comms}', inline={mode == 'inline'})"
    run_notebook(page, nbclassic_server, f'{extension}_{mode}_{comms}', [
        'import pandas as pd\nimport panel as pn',
        load,
        component,
    ])

    try:
        expect(page.locator(selector)).to_have_count(1, timeout=10000)
    except AssertionError as error:
        raise AssertionError(f'{error}\nConsole errors:\n' + '\n'.join(console_errors)) from error


def test_nbclassic_component_comm(page, nbclassic_server):
    """Verify that a nbclassic browser event reaches Panel's notebook comm."""
    counter_cell = (
        "button = pn.widgets.Button(name='Increment')\n"
        "counter = pn.pane.Markdown('0', css_classes=['nbclassic-counter'])\n"
        "button.on_click(lambda event: setattr(counter, 'object', str(int(counter.object) + 1)))\n"
        "pn.Row(button, counter)"
    )
    run_notebook(page, nbclassic_server, 'component_comm', [
        'import panel as pn\npn.extension(comms="default", inline=False)',
        counter_cell,
    ])

    page.get_by_role('button', name='Increment').click()
    expect(page.locator('.nbclassic-counter')).to_have_text('1')


def test_nbclassic_warns_when_extension_missing(page, nbclassic_server):
    """
    The proactive liveness check must warn even when nothing else on the
    page happens to request a panel-preview resource that would otherwise
    trigger the reactive error path.
    """
    page.route(
        '**/panel-preview/static/extensions/panel/**',
        lambda route: route.fulfill(status=404, body='Not Found'),
    )
    run_notebook(page, nbclassic_server, 'extensioncheck', [
        "import panel as pn\npn.extension(comms='default', inline=False)",
    ])

    alert = page.locator('.output_area [role="alert"]')
    expect(alert).to_be_visible(timeout=15000)
    expect(alert).to_contain_text('Jupyter server extension')


def test_nbclassic_component_renders_when_other_library_fails(page, nbclassic_server):
    page.route('**/bundled/katex/**', lambda route: route.fulfill(status=404, body='Not Found'))
    run_notebook(page, nbclassic_server, 'failedlibrary', [
        'import panel as pn',
        "pn.extension('filedropper', 'katex', comms='default', inline=False)",
        'pn.widgets.FileDropper(height=100)',
    ])

    expect(page.locator('.filepond--root')).to_have_count(1, timeout=12000)
