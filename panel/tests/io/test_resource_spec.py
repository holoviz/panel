import pytest

from bokeh.model import Model

from panel.config import config, panel_extension as extension
from panel.custom import JSComponent
from panel.io.resource_spec import (
    SPEC_VERSION, declared_specs, lazy_load_available, resource_spec,
)
from panel.io.resources import (
    CDN_DIST, JS_VERSION, Resources, set_resource_mode,
)
from panel.io.state import set_curdoc, state
from panel.models.echarts import ECharts
from panel.models.esm import ReactiveESM
from panel.models.perspective import Perspective
from panel.models.plotly import PlotlyPlot
from panel.models.tabulator import TABULATOR_VERSION, DataTabulator
from panel.models.vizzu import VizzuChart
from panel.reactive import ReactiveHTML

MODES = ['cdn', 'server', 'inline']


def _resource_models():
    """
    Every Bokeh model class that declares external resources.
    """
    from panel.io.resource_spec import _has_resources
    return sorted(
        {cls for cls in Model.model_class_reverse_map.values() if _has_resources(cls)},
        key=lambda cls: cls.__qualname__
    )


def _declared(cls, attr):
    return list(getattr(cls, attr, None) or [])


def _spec_urls(spec):
    urls = []
    for lib in spec.get('libs', []):
        urls += lib.get('js', [])
        urls += [module['url'] for module in lib.get('modules', [])]
    return urls


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('cls', _resource_models(), ids=lambda cls: cls.__qualname__)
def test_resource_spec_urls_match_eager_path(cls, mode):
    """
    The spec has to hand the browser exactly the urls pn.extension would
    have rendered, in the same order, or the two paths can diverge.
    """
    spec = resource_spec(cls, mode)
    assert spec is not None
    assert spec['v'] == SPEC_VERSION

    resources = Resources(mode='cdn' if mode == 'inline' else mode)
    with set_resource_mode(mode):
        expected_js = resources.adjust_paths(_declared(cls, '__javascript__'))
        expected_modules = resources.adjust_paths(_declared(cls, '__javascript_modules__'))
        expected_css = resources.adjust_paths(_declared(cls, '__css__'))

    assert _spec_urls(spec) == expected_js + expected_modules
    assert spec.get('css', []) == expected_css


@pytest.mark.parametrize('cls', _resource_models(), ids=lambda cls: cls.__qualname__)
def test_resource_spec_module_exports(cls):
    """
    Every module export name lands on the module that provides it.
    """
    exports = list(getattr(cls, '__javascript_module_exports__', None) or [])
    if not exports:
        return
    spec = resource_spec(cls, 'cdn')
    modules = [
        module for lib in spec.get('libs', []) for module in lib.get('modules', [])
    ]
    assert [module.get('export') for module in modules[:len(exports)]] == exports


@pytest.mark.parametrize('cls', _resource_models(), ids=lambda cls: cls.__qualname__)
def test_resource_spec_shim_declared_with_modules(cls):
    """
    Modules cannot be imported without es-module-shims, so any spec that
    contains one has to carry the shim url, whether or not the page
    happens to have loaded it for some other reason.
    """
    spec = resource_spec(cls, 'cdn')
    has_modules = any('modules' in lib for lib in spec.get('libs', []))
    assert ('shim' in spec) == has_modules


def test_resource_spec_no_resources():
    from panel.models.widgets import Player
    assert resource_spec(Player) is None


def test_resource_spec_disabled():
    try:
        config.lazy_resources = False
        assert resource_spec(DataTabulator, 'cdn') is None
        assert declared_specs('cdn') == {}
    finally:
        config.lazy_resources = True


def test_resource_spec_timeout():
    try:
        config.resource_timeout = 500
        assert resource_spec(DataTabulator, 'cdn')['timeout'] == 500
    finally:
        config.resource_timeout = 15000


def test_resource_spec_grouped_by_global():
    spec = resource_spec(DataTabulator, 'cdn')
    assert spec['libs'] == [
        {
            'name': 'Tabulator',
            'js': [f'{CDN_DIST}bundled/datatabulator/tabulator-tables@{TABULATOR_VERSION}/dist/js/tabulator.min.js'],
            'probe': {'global': 'Tabulator'},
        },
        {
            'name': 'luxon',
            'js': [f'{CDN_DIST}bundled/datatabulator/luxon/build/global/luxon.min.js'],
            'probe': {'global': 'luxon'},
        },
    ]


def test_resource_spec_unclaimed_urls_grouped_separately():
    """
    echarts-gl has no global of its own but has to load after echarts, so
    it ends up in an anonymous group ordered behind it.
    """
    spec = resource_spec(ECharts, 'cdn')
    names = [lib['name'] for lib in spec['libs']]
    assert names == ['echarts', 'echarts:extra']
    assert 'probe' not in spec['libs'][1]


def test_resource_spec_custom_element_probe():
    spec = resource_spec(Perspective, 'cdn')
    assert [lib['probe'] for lib in spec['libs']] == [
        {'custom_element': 'perspective-viewer'}
    ]


@pytest.mark.parametrize('mode', MODES)
def test_resource_spec_follows_active_mode(mode):
    """
    The active mode has to be read when the spec is built, not when the
    module was imported, or every spec resolves for the module default.
    """
    with set_resource_mode(mode):
        assert resource_spec(PlotlyPlot) == resource_spec(PlotlyPlot, mode)


def test_resource_spec_server_mode_is_relative():
    spec = resource_spec(PlotlyPlot, 'server')
    assert _spec_urls(spec) == [
        'static/extensions/panel/bundled/plotlyplot/plotly-3.1.0.min.js'
    ]
    assert spec['css'] == [
        f'static/extensions/panel/bundled/plotlyplot/maplibre-gl@4.4.1/dist/maplibre-gl.css?v={JS_VERSION}'
    ]


def test_resource_spec_inline_falls_back_to_cdn():
    """
    There is nothing left to inline once the page has been rendered, so an
    inline page hands out CDN urls and flags that it did so.
    """
    spec = resource_spec(PlotlyPlot, 'inline')
    assert spec['inline_fallback'] is True
    assert _spec_urls(spec) == _spec_urls(resource_spec(PlotlyPlot, 'cdn'))


def test_resource_spec_module_urls_unbundled():
    spec = resource_spec(VizzuChart, 'server')
    assert _spec_urls(spec) == ['https://cdn.jsdelivr.net/npm/vizzu@0.17.1/dist/vizzu.min.js']


def test_resource_spec_esm_component():
    class Custom(JSComponent):
        # Naming an extension nobody loads keeps the class out of the eager
        # path, which would otherwise pick these urls up for every later test.
        _extension_name = 'test-lazy-resources'
        _esm = "export function render() {}"
        __javascript__ = ['https://example.com/lib.js']
        __css__ = ['https://example.com/lib.css']

    spec = resource_spec(Custom, 'cdn')
    assert _spec_urls(spec) == ['https://example.com/lib.js']
    assert spec['css'] == ['https://example.com/lib.css']


def test_resource_spec_reactive_html_component():
    class Custom(ReactiveHTML):
        _extension_name = 'test-lazy-resources'
        _template = "<div></div>"
        __javascript__ = ['https://example.com/lib.js']

    spec = resource_spec(Custom, 'cdn')
    assert _spec_urls(spec) == ['https://example.com/lib.js']


def test_resource_spec_shim_url_matches_reactive_esm():
    with set_resource_mode('server'):
        expected = Resources(mode='server').adjust_paths(ReactiveESM.__javascript__)[0]
    assert resource_spec(Perspective, 'server')['shim'] == expected


def test_model_carries_external_resources(document):
    with set_curdoc(document):
        model = DataTabulator()
    assert model.external_resources == resource_spec(DataTabulator)


def test_model_external_resources_disabled(document):
    try:
        config.lazy_resources = False
        with set_curdoc(document):
            model = DataTabulator()
        assert model.external_resources is None
    finally:
        config.lazy_resources = True


def test_model_without_resources_has_no_spec(document):
    from panel.models.trend import TrendIndicator
    with set_curdoc(document):
        model = TrendIndicator()
    assert model.external_resources is None


def test_declared_specs_covers_declared_extension(document):
    with set_resource_mode('cdn'), set_curdoc(document):
        extension('tabulator')
        declared = declared_specs('cdn')
    names = {lib['name'] for lib in declared['libs']}
    assert {'Tabulator', 'luxon'} <= names
    assert 'echarts' not in names


def test_declared_specs_matches_resource_spec(document):
    """
    The two paths derive their payload from the same builder, so a
    declared library is byte-identical to the one the model would ask for.
    """
    with set_resource_mode('cdn'), set_curdoc(document):
        extension('tabulator')
        declared = declared_specs('cdn')
        spec = resource_spec(DataTabulator, 'cdn')
    by_name = {lib['name']: lib for lib in declared['libs']}
    for lib in spec['libs']:
        assert by_name[lib['name']] == lib
    for url in spec['css']:
        assert url in declared['css']


def test_declared_specs_omits_empty_keys(monkeypatch):
    """
    An empty ``css`` or ``libs`` key would make the declare payload bigger
    for no reason, and the registry treats a missing key the same way.
    """
    monkeypatch.setattr(
        'panel.io.resource_spec._resource_classes', lambda: [ECharts]
    )
    declared = declared_specs('cdn')
    assert set(declared) == {'libs'}
    assert [lib['name'] for lib in declared['libs']] == ['echarts', 'echarts:extra']


@pytest.mark.parametrize('mode', MODES)
def test_declaring_extension_leaves_page_resources_unchanged(document, mode):
    """
    Lazy loading may not change what pn.extension puts on the page.
    """
    from panel.io.resources import bundle_resources

    def bundle():
        with set_resource_mode(mode), set_curdoc(document):
            extension('tabulator')
            return bundle_resources([], Resources(mode=mode))

    with_lazy = bundle()
    try:
        config.lazy_resources = False
        without_lazy = bundle()
    finally:
        config.lazy_resources = True

    assert with_lazy.js_files == without_lazy.js_files
    assert with_lazy.js_raw == without_lazy.js_raw
    assert with_lazy.js_modules == without_lazy.js_modules
    assert with_lazy.css_files == without_lazy.css_files
    assert with_lazy.css_raw == without_lazy.css_raw
    assert without_lazy.resource_declarations == {}
    assert with_lazy.resource_declarations


def test_render_js_declares_resources(document):
    from panel.io.resources import bundle_resources

    with set_resource_mode('cdn'), set_curdoc(document):
        extension('tabulator')
        bundle = bundle_resources([], Resources(mode='cdn'))
    rendered = bundle._render_js()
    assert '__panel_resources__.declare(' in rendered
    assert 'tabulator.min.js' in rendered


def test_lazy_load_available():
    try:
        with set_resource_mode('server'):
            assert lazy_load_available()
            assert lazy_load_available(notebook=True)
        with set_resource_mode('inline'):
            assert not lazy_load_available()
            assert lazy_load_available(notebook=True)
        config.lazy_resources = False
        with set_resource_mode('server'):
            assert not lazy_load_available()
    finally:
        config.lazy_resources = True


@pytest.fixture
def launching(monkeypatch):
    monkeypatch.setattr(type(state), '_is_launching', property(lambda self: True))


def test_lazy_load_leaves_extension_undeclared(document, launching):
    """
    Registering the extension after the fact would put the library into the
    page for every later render and make the page contents depend on when
    the component was created, so the lazy path leaves it alone.
    """
    from panel.util import lazy_load
    with set_curdoc(document), set_resource_mode('server'):
        extension()
        lazy_load('panel.models.tabulator', 'DataTabulator')
        assert state._extensions == []


def test_lazy_load_declares_extension_when_disabled(document, launching):
    """
    Without lazy loading the pre-1.10 recovery is the only thing that gets
    the resources onto the page, so it has to stay.
    """
    from panel.util import lazy_load
    try:
        config.lazy_resources = False
        with set_curdoc(document), set_resource_mode('server'):
            extension()
            lazy_load('panel.models.tabulator', 'DataTabulator')
            assert state._extensions == ['tabulator']
    finally:
        config.lazy_resources = True


def test_resource_spec_respects_rel_path(document):
    from panel.util import edit_readonly
    with set_curdoc(document):
        with edit_readonly(state):
            state.base_url = '/app/'
            state.rel_path = '..'
        try:
            spec = resource_spec(DataTabulator, 'server')
        finally:
            with edit_readonly(state):
                state.base_url = '/'
                state.rel_path = ''
    assert all(url.startswith('../static/') for url in _spec_urls(spec))
