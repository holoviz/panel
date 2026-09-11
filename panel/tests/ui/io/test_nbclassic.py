import pytest
import requests

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = [pytest.mark.ui, pytest.mark.jupyter]


@pytest.fixture
def nbclassic_server(jupyter_preview):
    """Use nbclassic as an extension of the shared Jupyter Server."""
    host, _ = jupyter_preview.split('/panel-preview/', 1)
    return f'{host}/nbclassic'


def run_notebook(page, nbclassic_server, notebook_name, cells):
    """Open a notebook in nbclassic and run every cell through its UI."""
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
    page.goto(f'{host}/notebooks/{notebook_name}.ipynb')
    expect(page.locator('#notebook-container .code_cell').first).to_be_visible()
    page.wait_for_function(
        "window.Jupyter?.notebook?._fully_loaded && "
        "window.Jupyter.notebook.kernel && !window.Jupyter.notebook.kernel_busy"
    )
    page.evaluate('Jupyter.notebook.execute_all_cells()')
    page.wait_for_function(
        'Jupyter.notebook.get_cells().every((cell) => cell.input_prompt_number != null)'
    )
    page.wait_for_function("window.Jupyter && !window.Jupyter.notebook.kernel_busy")
    errors = page.locator('.output_error').all_inner_texts()
    assert not errors, '\n'.join(errors)


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
        pytest.param(
            'deckgl',
            "pn.pane.DeckGL({'initialViewState': {'longitude': 0, 'latitude': 0, 'zoom': 1}, 'layers': []}, height=180)",
            '.deckgl canvas',
            marks=pytest.mark.xfail(
                reason=(
                    "deck.gl's json and carto bundles each call define() more than "
                    "once anonymously, because they embed UMD copies of their own "
                    "dependencies (long.js). RequireJS can attribute only one "
                    "anonymous define per script and rejects the rest with "
                    "'Mismatched anonymous define()', so window.deck never gains "
                    "JSONConverter. No paths/shim/exports configuration can fix a "
                    "script that defines more than one anonymous module; loading "
                    "them outside RequireJS is the only remedy."
                ),
                strict=True,
            ),
        ),
        ('terminal', 'pn.widgets.Terminal(height=100)', '.xterm'),
        ('katex', "pn.pane.LaTeX(r'$E = mc^2$')", '.katex'),
    ],
    ids=[
        'tabulator', 'perspective', 'filedropper', 'codeeditor', 'jsoneditor',
        'echarts', 'vega', 'deckgl', 'terminal', 'katex',
    ],
)
def test_nbclassic_component_resources(page, nbclassic_server, extension, component, selector):
    """Load each bundled component independently through nbclassic resources."""
    console_errors = []
    page.on('console', lambda message: console_errors.append(message.text) if message.type == 'error' else None)
    page.on('pageerror', lambda error: console_errors.append(str(error)))
    run_notebook(page, nbclassic_server, extension, [
        'import pandas as pd\nimport panel as pn',
        f"pn.extension('{extension}', comms='default', inline=False)",
        component,
    ])

    try:
        expect(page.locator(selector)).to_have_count(1, timeout=10000)
    except AssertionError as error:
        globals_ = page.evaluate("""() => ({
            vega: typeof window.vega,
            vegaLiteCompile: typeof window.vegaLite?.compile,
            vlCompile: typeof window.vl?.compile,
            vegaEmbed: typeof window.vegaEmbed,
        })""")
        raise AssertionError(f'{error}\nVega globals: {globals_}\nConsole errors:\n' + '\n'.join(console_errors)) from error


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
