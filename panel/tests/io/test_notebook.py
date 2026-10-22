import json
import re

import pytest

pytest.importorskip("IPython")

from bokeh.models import ImportedStyleSheet, InlineStyleSheet

from panel.config import config, panel_extension
from panel.io import resources as resources_module
from panel.io.notebook import (
    LOAD_MIME, _autoload_js, _bundled_require_path, _cdn_url_key, ipywidget,
    load_notebook, replace_inline_css, require_components,
)
from panel.io.resource_spec import _SPEC_CACHE, resource_spec
from panel.io.resources import (
    CDN_DIST, CDN_ROOT, JS_VERSION, Bundle, Resources, set_resource_mode,
)
from panel.layout import Column
from panel.models.echarts import ECharts
from panel.models.perspective import Perspective
from panel.models.tabulator import DataTabulator
from panel.pane import DataFrame, Str
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
def notebook_bootstrap(jupyter_endpoint):
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

def test_notebook_inline_css_stylesheets_kept_on_update(nb_loaded):
    pd = pytest.importorskip('pandas')
    pane = DataFrame(pd.DataFrame({'a': [1, 2]}))
    with config.set(inline=True):
        pane._repr_mimebundle_()
    model = list(pane._models.values())[0][0]
    stylesheets = list(model.stylesheets)
    assert not any(isinstance(sts, ImportedStyleSheet) for sts in stylesheets)

    pane.object = pd.DataFrame({'a': [3, 4]})

    assert model.stylesheets == stylesheets

def test_notebook_cdn_css_stylesheets_not_inlined_on_update(nb_loaded):
    pd = pytest.importorskip('pandas')
    pane = DataFrame(pd.DataFrame({'a': [1, 2]}))
    with config.set(inline=False):
        pane._repr_mimebundle_()
    model = list(pane._models.values())[0][0]

    pane.object = pd.DataFrame({'a': [3, 4]})

    assert not any(isinstance(sts, InlineStyleSheet) for sts in model.stylesheets)


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


def _tabulator_require(monkeypatch, mode, notebook):
    from bokeh.core.has_props import _default_resolver
    from bokeh.resources import CDN, INLINE

    monkeypatch.setattr(panel_extension, '_loaded_extensions', ['tabulator'])
    monkeypatch.setitem(
        _default_resolver._known_models, 'panel.models.tabulator.DataTabulator', DataTabulator
    )
    base = INLINE if mode == 'inline' else CDN
    with set_resource_mode(mode):
        resources = Resources.from_bokeh(base, notebook=notebook)
        return require_components(resources)


@pytest.mark.parametrize('notebook', [True, False])
def test_require_components_load_bundled_copies(monkeypatch, jupyter_endpoint, notebook):
    """
    RequireJS must load Panel's bundled copies rather than the npm CDN,
    which a notebook on a restricted network cannot reach.

    See https://github.com/holoviz/panel/issues/8750.
    """
    configs, requirements, _, _, require_skip = _tabulator_require(monkeypatch, 'cdn', notebook)

    paths = next(config['paths'] for config in configs if 'tabulator' in config['paths'])
    bundled, original = paths['tabulator']
    dist = '/panel-preview/static/extensions/panel/' if notebook else CDN_DIST
    assert bundled == f'{dist}bundled/datatabulator/tabulator-tables@6.4.0/dist/js/tabulator.min'
    assert original == DataTabulator.__js_require__['paths']['tabulator']
    assert f'{bundled}.js' in require_skip
    assert 'tabulator' in requirements
    # The class-level declaration must not be rewritten in place.
    assert isinstance(DataTabulator.__js_require__['paths']['tabulator'], str)


def test_require_components_skip_inlined_libraries(monkeypatch):
    """
    Inlined libraries assign their globals themselves, so RequireJS must not
    fetch them a second time from the network.
    """
    configs, requirements, exports, _, require_skip = _tabulator_require(monkeypatch, 'inline', True)

    assert not any('tabulator' in config['paths'] for config in configs)
    assert 'tabulator' not in requirements
    assert 'tabulator' not in exports
    assert require_skip == []


@pytest.mark.parametrize(('path', 'raw', 'url', 'expected'), [
    # The same file
    (
        'https://cdn.jsdelivr.net/npm/echarts@6.0.0/dist/echarts.min',
        'https://cdn.jsdelivr.net/npm/echarts@6.0.0/dist/echarts.min.js',
        '/bundled/echarts/echarts@6.0.0/dist/echarts.min.js',
        '/bundled/echarts/echarts@6.0.0/dist/echarts.min',
    ),
    # A package resolved to its default file, bundled without `.js`
    (
        'https://cdn.jsdelivr.net/npm/vega@6.1.2/build/vega.min',
        'https://cdn.jsdelivr.net/npm/vega@6.1.2',
        '/bundled/vegaplot/vega@6.1.2',
        '/bundled/vegaplot/vega@6.1.2?',
    ),
    # A path naming the directory the bundled files live in
    (
        '//cdn.jsdelivr.net/npm/ace-builds@1.40.1/src-min-noconflict',
        'https://cdn.jsdelivr.net/npm/ace-builds@1.40.1/src-min-noconflict/ace.js',
        '/bundled/aceplot/ace-builds@1.40.1/src-min-noconflict/ace.js',
        '/bundled/aceplot/ace-builds@1.40.1/src-min-noconflict',
    ),
    # Unrelated files that only share a prefix
    (
        'https://cdn.jsdelivr.net/npm/@deck.gl/carto@^9.1.14/dist.min',
        'https://cdn.jsdelivr.net/npm/@loaders.gl/3d-tiles@4.2.2/dist/dist.min.js',
        '/bundled/deckglplot/@loaders.gl/3d-tiles@4.2.2/dist/dist.min.js',
        None,
    ),
], ids=['file', 'package', 'directory', 'unrelated'])
def test_bundled_require_path(path, raw, url, expected):
    assert _bundled_require_path(_cdn_url_key(path), _cdn_url_key(raw), url) == expected


def test_autoload_js_preserves_inline_source():
    """
    Characters Python's splitlines() treats as line breaks (xterm.js has
    them in string literals) must reach the page untouched, otherwise the
    whole bootstrap is a syntax error.
    """
    source = 'var C0 = {FS: "\x1c", GS: "\x1d", RS: "\x1e", NEL: "\x85", LS: "\u2028"};'
    bundle = Bundle(js_raw=[source])
    bootstrap = _autoload_js(
        bundle=bundle, configs=[], requirements=[], exports={}, error_id='error',
        skip_imports={}, require_skip=[], ipywidget=False
    )
    assert source in bootstrap


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
    assert "root.Jupyter?.notebook != null || document.querySelector('.jp-LabShell') != null" in bootstrap
    assert 'if (live_notebook) {' in bootstrap
    assert 'if (!live_notebook) {' in bootstrap
    assert 'element.src = resource_url(url)' in bootstrap
    assert 'element.href = resource_url(url)' in bootstrap
    assert 'new URL(resource_url(url), document.baseURI)' in bootstrap
    assert 'require_config.paths[name] = (Array.isArray(path) ? path : [path]).flatMap(require_urls)' in bootstrap
    cdn_map = json.loads(re.search(r'const CDN_MAP = (.*);', bootstrap).group(1))
    assert ['static/extensions/panel/', CDN_DIST] in cdn_map
    assert any(path.startswith('static/js/bokeh') for path, _ in cdn_map)
    assert 'root.__panel_endpoint_failed__ = true;' in bootstrap


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


@pytest.mark.parametrize('notebook_resources', ['cdn', 'jupyter'])
def test_notebook_resources_option(monkeypatch, notebook_resources, notebook_bootstrap):
    """
    `notebook_resources` overrides whether the server announced the Jupyter
    extension endpoint, for Panel's own resources and BokehJS alike.
    """
    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)
    if notebook_resources == 'jupyter':
        monkeypatch.delenv('PANEL_JUPYTER_ENDPOINT')

    with config.set(notebook_resources=notebook_resources):
        load_notebook(inline=False)

    bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
    js_urls = next(line for line in bootstrap.splitlines() if 'const js_urls' in line)
    if notebook_resources == 'cdn':
        assert '/panel-preview/' not in js_urls
        assert 'https://cdn.holoviz.org/panel/' in js_urls
        assert 'https://cdn.bokeh.org/bokeh/' in js_urls
    else:
        assert '/panel-preview/static/extensions/panel/' in js_urls
        assert '/panel-preview/static/js/bokeh' in js_urls
        assert 'cdn.bokeh.org' not in js_urls


def test_notebook_resources_env_var(monkeypatch, jupyter_endpoint):
    from panel.io.resources import jupyter_endpoint_available

    assert jupyter_endpoint_available()
    monkeypatch.setenv('PANEL_NOTEBOOK_RESOURCES', 'CDN')
    assert config.notebook_resources == 'cdn'
    assert not jupyter_endpoint_available()


def test_notebook_ipywidgets_resources_use_cdn(monkeypatch, notebook_bootstrap):
    """
    ipywidgets mode (Voila and similar) has no Jupyter extension endpoint
    either: only a plain notebook kernel (``comms == 'default'``) does.
    """
    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)

    with config.set(comms='ipywidgets'):
        load_notebook(inline=False)

    bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
    js_urls = next(line for line in bootstrap.splitlines() if 'const js_urls' in line)
    assert '/panel-preview/static/extensions/panel/' not in js_urls
    assert 'https://cdn.holoviz.org/panel/' in js_urls


def test_notebook_checks_extension_only_for_default_comms(monkeypatch, jupyter_endpoint):
    """
    The proactive liveness check only makes sense where the endpoint is
    actually expected to exist, i.e. a plain notebook kernel.
    """
    from bokeh.io.state import curstate

    published = []

    def publish_display_data(data, **kwargs):
        published.append(data)

    monkeypatch.setattr('IPython.display.publish_display_data', publish_display_data)

    for comms in ('default', 'vscode', 'colab', 'ipywidgets'):
        published.clear()
        bk_state, mode = curstate(), resources_module.RESOURCE_MODE
        notebook_resources = resources_module.NOTEBOOK_RESOURCES
        notebook, notebook_type = bk_state.notebook, bk_state.notebook_type
        try:
            with config.set(comms=comms):
                load_notebook(inline=False)
            bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
            checks = 'panel.min.js", {method: "HEAD"}' in bootstrap
            assert checks == (comms == 'default'), comms
        finally:
            resources_module.RESOURCE_MODE = mode
            resources_module.NOTEBOOK_RESOURCES = notebook_resources
            bk_state._notebook, bk_state._notebook_type = notebook, notebook_type
            _SPEC_CACHE.clear()


def test_notebook_without_jupyter_endpoint_uses_cdn(monkeypatch):
    """
    Frontends other than Jupyter, e.g. nteract, also use 'default' comms but
    never serve the endpoint, so without the server's announcement neither
    the bootstrap nor later components may point at it.
    """
    from bokeh.io.state import curstate

    published = []
    monkeypatch.setattr(
        'IPython.display.publish_display_data', lambda data, **kwargs: published.append(data)
    )

    bk_state, mode = curstate(), resources_module.RESOURCE_MODE
    notebook_resources = resources_module.NOTEBOOK_RESOURCES
    notebook, notebook_type = bk_state.notebook, bk_state.notebook_type
    _SPEC_CACHE.clear()
    try:
        load_notebook(inline=False)
        bootstrap = next(data[LOAD_MIME] for data in published if LOAD_MIME in data)
        js_urls = next(line for line in bootstrap.splitlines() if 'const js_urls' in line)
        spec = resource_spec(DataTabulator)
        spec_urls = [url for lib in spec['libs'] for url in lib['js']] + spec['css']
    finally:
        resources_module.RESOURCE_MODE = mode
        resources_module.NOTEBOOK_RESOURCES = notebook_resources
        bk_state._notebook, bk_state._notebook_type = notebook, notebook_type
        _SPEC_CACHE.clear()

    assert '/panel-preview/' not in js_urls
    assert 'https://cdn.holoviz.org/panel/' in js_urls
    assert 'panel.min.js", {method: "HEAD"}' not in bootstrap
    assert spec_urls
    assert not any('panel-preview' in url for url in spec_urls)


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
def test_notebook_resources_do_not_reuse_spec_cached_before_bootstrap(nb_loaded, jupyter_endpoint):
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


def test_notebook_esm_bundle_uses_jupyter_extension_endpoint(
    tmp_path, monkeypatch, document, comm, notebook_bootstrap
):
    """
    A compiled bundle in the dist directory of a registered extension is
    served by the Jupyter extension endpoint rather than inlined.
    """
    from bokeh.embed.bundle import extension_dirs

    from panel.custom import JSComponent

    bundle = tmp_path / 'test.bundle.js'
    bundle.write_text('export function render() {}')
    (tmp_path / 'test.bundle.css').write_text('div {}')
    monkeypatch.setitem(extension_dirs, 'panel-test-ext', tmp_path)

    class BundledComponent(JSComponent):
        _bundle = bundle

    with config.set(inline=False):
        model = BundledComponent().get_root(document, comm)

    url = '/panel-preview/static/extensions/panel-test-ext/test.bundle'
    assert model.bundle == 'url'
    assert model.esm == f'{url}.js'
    assert model.css_bundle == f'{url}.css'


def test_notebook_esm_bundle_respects_render_esm_override(
    tmp_path, monkeypatch, document, comm, notebook_bootstrap
):
    """
    Extensions override `_render_esm`, typically returning a url only for
    server sessions, so the notebook has to ask for that same url.
    """
    from bokeh.embed.bundle import extension_dirs

    from panel.custom import JSComponent

    bundle = tmp_path / 'test.bundle.js'
    bundle.write_text('export function render() {}')
    monkeypatch.setitem(extension_dirs, 'panel-test-ext', tmp_path)

    class ServerUrlComponent(JSComponent):
        _bundle = bundle

        @classmethod
        def _render_esm(cls, compiled=True, server=False):
            if server:
                return './' + cls._component_resource_path(bundle, compiled) + '?abc'
            return bundle.read_text()

    class SourceComponent(ServerUrlComponent):

        @classmethod
        def _render_esm(cls, compiled=True, server=False):
            return bundle.read_text()

    with config.set(inline=False):
        url_model = ServerUrlComponent().get_root(document, comm)
        source_model = SourceComponent().get_root(document, comm)

    assert url_model.bundle == 'url'
    assert url_model.esm == '/panel-preview/static/extensions/panel-test-ext/test.bundle.js?abc'
    assert source_model.bundle not in (None, 'url')
    assert source_model.esm == 'export function render() {}'
    assert source_model.css_bundle is None


def test_notebook_component_css_uses_jupyter_extension_endpoint(nb_loaded, notebook_bootstrap):
    column = Column(Str('a'))
    with config.set(inline=False):
        column._repr_mimebundle_()

    (model, _) = list(column._models.values())[0]
    urls = [sts.url for sts in model.select({'type': ImportedStyleSheet})]

    assert urls
    assert all(url.startswith('/panel-preview/static/extensions/panel/') for url in urls)
