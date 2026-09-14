import re

import pytest

pytest.importorskip("IPython")

from bokeh.models import ImportedStyleSheet, InlineStyleSheet

from panel.config import config, panel_extension
from panel.io import resources as resources_module
from panel.io.notebook import (
    LOAD_MIME, ipywidget, load_notebook, replace_inline_css,
    require_components,
)
from panel.io.resource_spec import _SPEC_CACHE, resource_spec
from panel.io.resources import (
    CDN_DIST, CDN_ROOT, JS_VERSION, set_resource_mode,
)
from panel.layout import Column
from panel.models.echarts import ECharts
from panel.models.perspective import Perspective
from panel.models.tabulator import DataTabulator
from panel.pane import Str
from panel.widgets import TextEditor

from ..util import jb_available


@pytest.fixture
def nb_loaded():
    old = panel_extension._loaded
    panel_extension._loaded = True
    try:
        yield
    finally:
        panel_extension._loaded = old


@pytest.fixture
def notebook_bootstrap():
    """
    Runs the notebook bootstrap, undoing the global state it sets.
    """
    from bokeh.io.state import curstate
    state, mode = curstate(), resources_module.RESOURCE_MODE
    notebook_resources = resources_module.NOTEBOOK_RESOURCES
    notebook, notebook_type = state.notebook, state.notebook_type
    # `_SPEC_CACHE` is keyed in part on `RESOURCE_MODE`/`NOTEBOOK_RESOURCES`,
    # so it must not leak a spec between this bootstrap and other tests.
    _SPEC_CACHE.clear()
    try:
        load_notebook(inline=True)
        yield
    finally:
        resources_module.RESOURCE_MODE = mode
        resources_module.NOTEBOOK_RESOURCES = notebook_resources
        state._notebook, state._notebook_type = notebook, notebook_type
        _SPEC_CACHE.clear()


@jb_available
def test_ipywidget(document):
    pane = Str('A')
    widget = ipywidget(pane, doc=document)

    assert widget._view_count == 0
    assert len(pane._models) == 1

    init_id = list(pane._models)[0]

    widget._view_count = 1

    assert widget._view_count == 1
    assert init_id in pane._models

    widget._view_count = 0

    assert len(pane._models) == 0

    widget._view_count = 1

    assert len(pane._models) == 1
    prev_id = list(pane._models)[0]

    widget.notify_change({'new': 1, 'old': 1, 'name': '_view_count',
                          'type': 'change', 'model': widget})
    assert prev_id in pane._models
    assert len(pane._models) == 1

    widget._view_count = 2

    assert prev_id in pane._models
    assert len(pane._models) == 1

def test_notebook_cdn_css_stylesheets(nb_loaded):
    widget = TextEditor()
    with config.set(inline=False):
        widget._repr_mimebundle_()
    with set_resource_mode('cdn'):
        stylesheets = widget._widget_type.__css__
    model = list(widget._models.values())[0][0]
    for stylesheet, url in zip(model.stylesheets, stylesheets):
        assert isinstance(stylesheet, ImportedStyleSheet)
        assert url.startswith(CDN_ROOT)
        assert stylesheet.url == url

def test_notebook_inline_css_stylesheets(nb_loaded):
    widget = TextEditor()
    with config.set(inline=True):
        widget._repr_mimebundle_()
    model = list(widget._models.values())[0][0]
    for stylesheet in model.stylesheets[:len(model.__css__)]:
        assert isinstance(stylesheet, InlineStyleSheet)


def test_notebook_inline_resources_shadow_amd_globals(monkeypatch, notebook_bootstrap):
    """
    Inline UMD bundles must assign their browser globals on RequireJS pages.

    See https://github.com/holoviz/panel/issues/8750.
    """
    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)

    load_notebook(inline=True)

    bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
    assert 'function(Bokeh, define, module, exports)' in bootstrap
    assert 'window.requirejs.config' in bootstrap


def test_require_components_only_includes_active_panel_extensions(monkeypatch):
    """Classic notebook RequireJS setup must not load inactive extensions."""
    from bokeh.core.has_props import _default_resolver

    monkeypatch.setattr(panel_extension, '_loaded_extensions', ['echarts'])
    # model_class_reverse_map is derived from Bokeh's resolver rather than being
    # a plain dict, so registering has to go through the resolver. The autouse
    # module_cleanup fixture unregisters Panel's models before every test and
    # they are only registered when their class is defined, which has already
    # happened, so re-registering here is what puts them back.
    monkeypatch.setitem(
        _default_resolver._known_models, 'panel.models.echarts.ECharts', ECharts
    )
    monkeypatch.setitem(
        _default_resolver._known_models, 'panel.models.perspective.Perspective', Perspective
    )

    configs, requirements, *_ = require_components()

    assert 'echarts' in requirements
    assert not any(name.startswith('perspective') for name in requirements)
    assert any('echarts' in config['paths'] for config in configs)


def test_notebook_endpoint_alert_stays_in_notebook_output(monkeypatch, notebook_bootstrap):
    """
    Endpoint failures must update Panel's output rather than the notebook UI.
    """
    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)

    load_notebook(inline=False)

    bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
    html = next(data['text/html'] for data in published if 'text/html' in data)
    error_id = re.search(r'<div id="([^"]+)" role="alert" hidden>', html).group(1)
    assert f'document.getElementById("{error_id}")' in bootstrap
    assert '(document.body || document.documentElement)' not in bootstrap
    assert 'function fallback_to_cdn(element, url, attribute, parent)' in bootstrap
    assert 'element.dataset.panelCdnFallback != null' in bootstrap
    assert 'const CDN_DIST = "https://cdn.holoviz.org/panel/' in bootstrap


def test_notebook_vscode_resources_use_cdn(monkeypatch, notebook_bootstrap):
    """
    VS Code has no Jupyter extension endpoint to serve Panel resources.
    """
    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)

    with config.set(comms='vscode'):
        load_notebook(inline=False)

    bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
    js_urls = next(line for line in bootstrap.splitlines() if 'const js_urls' in line)
    assert '/panel-preview/static/extensions/panel/' not in js_urls
    assert 'https://cdn.holoviz.org/panel/' in js_urls


def test_notebook_resources_use_jupyter_extension_endpoint(notebook_bootstrap):
    """
    A component rendered in a later cell builds its specification outside
    any resource mode block, so it has to preserve the Jupyter extension
    endpoint selected by the notebook bootstrap.
    """
    spec = resource_spec(DataTabulator)
    urls = [url for lib in spec['libs'] for url in lib['js']] + spec['css']

    assert urls
    assert all(url.startswith('/panel-preview/static/extensions/panel/') for url in urls)


def test_notebook_dynamic_component_resources_use_jupyter_extension_endpoint(
    nb_loaded, notebook_bootstrap
):
    column = Column()
    column._repr_mimebundle_()
    editor = TextEditor()
    column.append(editor)

    (model, _) = list(editor._models.values())[0]
    urls = [url for lib in model.external_resources['libs'] for url in lib['js']]

    assert urls
    assert all(url.startswith('/panel-preview/static/extensions/panel/') for url in urls)


@pytest.mark.filterwarnings(
    "ignore:Attempted to send message over Jupyter Comm.*:UserWarning"
)
def test_notebook_resources_do_not_reuse_spec_cached_before_bootstrap(nb_loaded):
    """
    Regression test for a CI failure under xdist: a spec cached by an
    earlier, unrelated test under the same resolved mode was handed back
    unchanged to a notebook test, dropping the Jupyter extension endpoint.
    ``resource_spec``'s cache key must include the effective notebook
    default, not just the resolved mode.

    The filter is unrelated to what this checks: Python only raises that
    warning the first time it's hit in the process, so whether it surfaces
    here depends on what other tests already ran.
    """
    from bokeh.io.state import curstate
    state, mode = curstate(), resources_module.RESOURCE_MODE
    notebook_resources = resources_module.NOTEBOOK_RESOURCES
    notebook, notebook_type = state.notebook, state.notebook_type
    try:
        # Simulates the "earlier, unrelated test": mode 'cdn', no notebook.
        resources_module.RESOURCE_MODE = 'cdn'
        widget = TextEditor()
        outside_notebook_urls = [
            url for lib in (widget.get_root().external_resources or {}).get('libs', [])
            for url in lib['js']
        ]
        assert not any('panel-preview' in url for url in outside_notebook_urls)

        # The notebook bootstrap now runs, selecting that same 'cdn' mode.
        load_notebook(inline=True)

        column = Column()
        column._repr_mimebundle_()
        editor = TextEditor()
        column.append(editor)

        (model, _) = list(editor._models.values())[0]
        urls = [url for lib in model.external_resources['libs'] for url in lib['js']]

        assert urls
        assert all(url.startswith('/panel-preview/static/extensions/panel/') for url in urls)
    finally:
        resources_module.RESOURCE_MODE = mode
        resources_module.NOTEBOOK_RESOURCES = notebook_resources
        state._notebook, state._notebook_type = notebook, notebook_type
        _SPEC_CACHE.clear()


def test_replace_inline_css_ignores_version_query():
    url = f'{CDN_DIST}css/loading.css'
    unversioned = replace_inline_css(ImportedStyleSheet(url=url))
    versioned = replace_inline_css(ImportedStyleSheet(url=f'{url}?v={JS_VERSION}'))

    assert isinstance(unversioned, InlineStyleSheet)
    assert isinstance(versioned, InlineStyleSheet)
    assert versioned.css == unversioned.css
