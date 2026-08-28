"""
End-to-end coverage for on-demand loading of component resources.

Every app here calls ``pn.extension()`` without arguments, which is what
puts the page on the lazy path: with an empty extension list nothing is
written into the page up front, so whatever renders got its libraries at
render time.
"""
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.config import panel_extension as extension
from panel.custom import JSComponent
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def _tabulator():
    import pandas as pd
    return pn.widgets.Tabulator(pd.DataFrame({'x': [1, 2, 3]}), height=200)


def _perspective():
    import pandas as pd
    return pn.pane.Perspective(pd.DataFrame({'x': [1, 2, 3]}), height=300)


def _plotly():
    return pn.pane.Plotly({
        'data': [{'type': 'scatter', 'x': [1, 2, 3], 'y': [1, 2, 3]}],
        'layout': {'width': 400, 'height': 300},
    })


def _vega():
    return pn.pane.Vega({
        '$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
        'data': {'values': [{'a': 'A', 'b': 28}, {'a': 'B', 'b': 55}]},
        'mark': 'bar',
        'encoding': {'x': {'field': 'a', 'type': 'nominal'}, 'y': {'field': 'b', 'type': 'quantitative'}},
    })


def _echarts():
    return pn.pane.ECharts({
        'xAxis': {'type': 'category', 'data': ['A', 'B', 'C']},
        'yAxis': {'type': 'value'},
        'series': [{'data': [1, 2, 3], 'type': 'bar'}],
    }, height=300, width=400)


def _vizzu():
    return pn.pane.Vizzu(
        {'Name': ['Alice', 'Bob'], 'Weight': [50, 60]},
        config={'geometry': 'rectangle', 'x': 'Name', 'y': 'Weight'},
        height=300, width=400,
    )


def _jsoneditor():
    return pn.widgets.JSONEditor(value={'a': 1}, height=300)


def _codeeditor():
    return pn.widgets.CodeEditor(value='x = 1', height=200)


def _texteditor():
    return pn.widgets.TextEditor(value='<p>text</p>', height=200)


def _katex():
    return pn.pane.LaTeX(r'$\frac{1}{2}$', renderer='katex')


def _filedropper():
    return pn.widgets.FileDropper()


def _terminal():
    return pn.widgets.Terminal(height=200, width=400)


def _modal():
    return pn.layout.Modal(pn.pane.Markdown('in modal'), open=True)


# name -> (factory, selector that only exists once the library ran)
COMPONENTS = {
    'codeeditor': (_codeeditor, '.ace_editor'),
    'echarts': (_echarts, 'canvas'),
    'filedropper': (_filedropper, '.filepond--root'),
    'jsoneditor': (_jsoneditor, '.jsoneditor'),
    'katex': (_katex, '.katex'),
    'modal': (_modal, '.pnx-dialog-close'),
    'perspective': (_perspective, 'perspective-viewer'),
    'plotly': (_plotly, '.js-plotly-plot'),
    'tabulator': (_tabulator, '.pnx-tabulator.tabulator'),
    'terminal': (_terminal, '.xterm'),
    'texteditor': (_texteditor, '.ql-container'),
    'vega': (_vega, '.vega-embed'),
    'vizzu': (_vizzu, 'canvas'),
}


def _errors(msgs):
    return [
        msg for msg in msgs
        if msg.type == 'error' and 'favicon' not in msg.location['url']
    ]


def _script_count(page, fragment):
    return page.evaluate(
        """(fragment) => document.querySelectorAll(`script[src*="${fragment}"]`).length""",
        fragment
    )


def _assert_no_duplicates(page):
    urls = page.evaluate(
        """() => [
            ...[...document.querySelectorAll('script[src]')].map((el) => el.src),
            ...[...document.querySelectorAll('link[href]')].map((el) => el.href),
        ]"""
    )
    duplicates = {url for url in urls if urls.count(url) > 1}
    assert not duplicates, f'resources loaded more than once: {sorted(duplicates)}'


@pytest.mark.parametrize('name', list(COMPONENTS))
def test_undeclared_component_renders(page, name):
    factory, selector = COMPONENTS[name]

    def app():
        extension()
        factory().servable()

    msgs, _ = serve_component(page, app)

    expect(page.locator(selector).first).to_be_visible(timeout=20000)
    assert _errors(msgs) == []


@pytest.mark.parametrize('name', list(COMPONENTS))
def test_undeclared_component_renders_after_load(page, name):
    """
    The case the eager path cannot reach: the component does not exist
    when the page is built, so its libraries can only arrive at render
    time.
    """
    factory, selector = COMPONENTS[name]

    def app():
        extension()
        column = pn.Column()
        pn.state.onload(lambda: column.append(factory()))
        return column

    msgs, _ = serve_component(page, app)

    expect(page.locator(selector).first).to_be_visible(timeout=20000)
    assert _errors(msgs) == []


def test_component_renders_from_button_callback(page):
    def app():
        extension()
        column = pn.Column()
        button = pn.widgets.Button()
        button.on_click(lambda event: column.append(_tabulator()))
        return pn.Column(button, column)

    msgs, _ = serve_component(page, app)

    page.click('.bk-btn')

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1)
    assert _script_count(page, 'tabulator.min.js') == 1
    assert _errors(msgs) == []


def test_two_components_share_one_script(page):
    def app():
        extension()
        return pn.Column(_tabulator(), _tabulator())

    msgs, _ = serve_component(page, app)

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(2)
    assert _script_count(page, 'tabulator.min.js') == 1
    assert _script_count(page, 'luxon.min.js') == 1
    assert _errors(msgs) == []


def test_late_component_reuses_loaded_library(page):
    def app():
        extension()
        column = pn.Column(_tabulator())
        button = pn.widgets.Button()
        button.on_click(lambda event: column.append(_tabulator()))
        return pn.Column(button, column)

    msgs, _ = serve_component(page, app)

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1, timeout=20000)

    page.click('.bk-btn')

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(2)
    assert _script_count(page, 'tabulator.min.js') == 1
    assert _errors(msgs) == []


def test_esm_components_share_one_shim(page):
    def app():
        extension()
        return pn.Column(_vizzu(), _perspective())

    msgs, _ = serve_component(page, app)

    expect(page.locator('canvas').first).to_be_visible(timeout=20000)
    expect(page.locator('perspective-viewer')).to_have_count(1, timeout=20000)
    assert _script_count(page, 'es-module-shims') == 1
    assert _errors(msgs) == []


def test_declared_extension_loads_scripts_once(page):
    def app():
        extension('tabulator')
        pn.Column(_tabulator(), _tabulator()).servable()

    msgs, _ = serve_component(page, app)

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(2)
    assert _script_count(page, 'tabulator.min.js') == 1
    assert _script_count(page, 'luxon.min.js') == 1
    _assert_no_duplicates(page)
    assert _errors(msgs) == []


def test_declared_extension_shared_with_late_component(page):
    """
    A preloaded library must be recognised as loaded, not fetched again.
    """
    def app():
        extension('tabulator')
        column = pn.Column()
        pn.state.onload(lambda: column.append(_tabulator()))
        return column

    msgs, _ = serve_component(page, app)

    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1)
    assert _script_count(page, 'tabulator.min.js') == 1
    assert _errors(msgs) == []


class BrokenResources(JSComponent):
    """
    Component whose library cannot be fetched.

    ``_extension_name`` names an extension nobody declares, which keeps
    the unreachable url out of the eager path for the rest of the test
    session.
    """

    _extension_name = 'lazy-broken'

    _esm = """
    export function render() {
      const div = document.createElement('div')
      div.className = 'broken-rendered'
      return div
    }
    """

    __javascript__ = ['http://localhost:9/panel-missing-resource.js']


def test_failed_resource_renders_error_and_spares_siblings(page):
    def app():
        extension()
        pn.config.resource_timeout = 4000
        return pn.Column(
            BrokenResources(),
            pn.pane.Markdown('sibling', css_classes=['sibling']),
            _tabulator(),
        )

    serve_component(page, app)

    wait_until(lambda: page.locator('.pn-resource-error').count() == 1, page)
    expect(page.locator('.sibling').locator('div')).to_have_text('sibling\n')
    expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1)
    expect(page.locator('.broken-rendered')).to_have_count(0)


def test_declared_extension_renders_with_lazy_resources_disabled(page):
    """
    The pre-1.10 path: nothing loads on demand, so a declared extension
    has to be enough on its own.
    """
    def app():
        extension('tabulator')
        pn.config.lazy_resources = False
        pn.Column(_tabulator()).servable()

    try:
        msgs, _ = serve_component(page, app)

        expect(page.locator('.pnx-tabulator.tabulator')).to_have_count(1)
        assert _script_count(page, 'tabulator.min.js') == 1
        _assert_no_duplicates(page)
        assert _errors(msgs) == []
    finally:
        pn.config.lazy_resources = True
