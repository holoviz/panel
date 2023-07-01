import os

from pathlib import Path

from packaging.version import Version

from panel.config import config, panel_extension as extension
from panel.io.convert import BOKEH_VERSION
from panel.io.resources import (
    CDN_DIST, DIST_DIR, PANEL_DIR, Resources, resolve_custom_path,
    set_resource_mode,
)
from panel.io.state import set_curdoc
from panel.widgets import Button

bokeh_version = Version(BOKEH_VERSION)
if bokeh_version.is_devrelease or bokeh_version.is_prerelease:
    bk_prefix = 'dev'
else:
    bk_prefix = 'release'

def test_resolve_custom_path_relative_input():
    assert resolve_custom_path(Button, 'button.py') == (PANEL_DIR / 'widgets' / 'button.py')

def test_resolve_custom_path_relative_input_relative_to():
    assert str(resolve_custom_path(Button, 'button.py', relative=True)) == 'button.py'

def test_resolve_custom_path_relative_level_up_input():
    assert resolve_custom_path(Button, '../reactive.py') == (PANEL_DIR / 'reactive.py')

def test_resolve_custom_path_relative_input_level_up_relative_to():
    assert str(resolve_custom_path(Button, '../reactive.py', relative=True)) == f'..{os.path.sep}reactive.py'

def test_resolve_custom_path_abs_input():
    assert resolve_custom_path(Button, (PANEL_DIR / 'widgets' / 'button.py')) == (PANEL_DIR / 'widgets' / 'button.py')

def test_resolve_custom_path_abs_input_relative_to():
    assert str(resolve_custom_path(Button, (PANEL_DIR / 'widgets' / 'button.py'), relative=True)) == 'button.py'

def test_resources_cdn():
    resources = Resources(mode='cdn', minified=True)
    assert resources.js_raw == ['Bokeh.set_log_level("info");']
    assert resources.js_files == [
        f'https://cdn.bokeh.org/bokeh/{bk_prefix}/bokeh-{BOKEH_VERSION}.min.js',
        f'https://cdn.bokeh.org/bokeh/{bk_prefix}/bokeh-gl-{BOKEH_VERSION}.min.js',
        f'https://cdn.bokeh.org/bokeh/{bk_prefix}/bokeh-widgets-{BOKEH_VERSION}.min.js',
        f'https://cdn.bokeh.org/bokeh/{bk_prefix}/bokeh-tables-{BOKEH_VERSION}.min.js',
        f'https://cdn.bokeh.org/bokeh/{bk_prefix}/bokeh-mathjax-{BOKEH_VERSION}.min.js',
    ]

def test_resources_server_absolute():
    resources = Resources(mode='server', absolute=True, minified=True)
    assert resources.js_raw == ['Bokeh.set_log_level("info");']
    assert resources.js_files == [
        'http://localhost:5006/static/js/bokeh.min.js',
        'http://localhost:5006/static/js/bokeh-gl.min.js',
        'http://localhost:5006/static/js/bokeh-widgets.min.js',
        'http://localhost:5006/static/js/bokeh-tables.min.js',
        'http://localhost:5006/static/js/bokeh-mathjax.min.js'
    ]

def test_resources_server():
    resources = Resources(mode='server', minified=True)
    assert resources.js_raw == ['Bokeh.set_log_level("info");']
    assert resources.js_files == [
        'static/js/bokeh.min.js',
        'static/js/bokeh-gl.min.js',
        'static/js/bokeh-widgets.min.js',
        'static/js/bokeh-tables.min.js',
        'static/js/bokeh-mathjax.min.js'
    ]

def test_resources_config_css_files(document):
    resources = Resources(mode='cdn')
    with set_curdoc(document):
        config.css_files = [Path(__file__).parent.parent / 'assets' / 'custom.css']
        assert resources.css_raw == ['/* Test */\n']

def test_resources_model_server(document):
    resources = Resources(mode='server')
    with set_resource_mode('server'):
        with set_curdoc(document):
            extension('tabulator')
            assert resources.js_files[:2] == [
                'static/extensions/panel/bundled/datatabulator/tabulator-tables@5.5.0/dist/js/tabulator.js',
                'static/extensions/panel/bundled/datatabulator/luxon/build/global/luxon.min.js',
            ]
            assert resources.css_files == [
                'static/extensions/panel/bundled/datatabulator/tabulator-tables@5.5.0/dist/css/tabulator_simple.min.css'
            ]

def test_resources_model_cdn(document):
    resources = Resources(mode='cdn')
    with set_resource_mode('cdn'):
        with set_curdoc(document):
            extension('tabulator')
            assert resources.js_files[:2] == [
                f'{CDN_DIST}bundled/datatabulator/tabulator-tables@5.5.0/dist/js/tabulator.js',
                f'{CDN_DIST}bundled/datatabulator/luxon/build/global/luxon.min.js',
            ]
            assert resources.css_files == [
                f'{CDN_DIST}bundled/datatabulator/tabulator-tables@5.5.0/dist/css/tabulator_simple.min.css'
            ]

def test_resources_model_inline(document):
    resources = Resources(mode='inline')
    with set_resource_mode('inline'):
        with set_curdoc(document):
            extension('tabulator')
            assert resources.js_raw[-2:] == [
                (DIST_DIR / 'bundled/datatabulator/tabulator-tables@5.5.0/dist/js/tabulator.js').read_text(encoding='utf-8'),
                (DIST_DIR / 'bundled/datatabulator/luxon/build/global/luxon.min.js').read_text(encoding='utf-8')
            ]
            assert resources.css_raw == [
                (DIST_DIR / 'bundled/datatabulator/tabulator-tables@5.5.0/dist/css/tabulator_simple.min.css').read_text(encoding='utf-8')
            ]

def test_resources_reactive_html_server(document):
    resources = Resources(mode='server')
    with set_resource_mode('server'):
        with set_curdoc(document):
            extension('gridstack')
            assert resources.js_files[-1:] == [
                'static/extensions/panel/bundled/gridstack/gridstack@7.2.3/dist/gridstack-all.js'
            ]
            assert resources.css_files == [
                'static/extensions/panel/bundled/gridstack/gridstack@7.2.3/dist/gridstack.min.css',
                'static/extensions/panel/bundled/gridstack/gridstack@7.2.3/dist/gridstack-extra.min.css'
            ]

def test_resources_reactive_html_cdn(document):
    resources = Resources(mode='cdn')
    with set_resource_mode('cdn'):
        with set_curdoc(document):
            extension('gridstack')
            assert resources.js_files[-1:] == [
                f'{CDN_DIST}bundled/gridstack/gridstack@7.2.3/dist/gridstack-all.js'
            ]
            assert resources.css_files == [
                f'{CDN_DIST}bundled/gridstack/gridstack@7.2.3/dist/gridstack.min.css',
                f'{CDN_DIST}bundled/gridstack/gridstack@7.2.3/dist/gridstack-extra.min.css'
            ]

def test_resources_reactive_html_inline(document):
    resources = Resources(mode='inline')
    with set_resource_mode('inline'):
        with set_curdoc(document):
            extension('gridstack')
            assert resources.js_raw[-1:] == [
                (DIST_DIR / 'bundled/gridstack/gridstack@7.2.3/dist/gridstack-all.js').read_text(encoding='utf-8')
            ]
            assert resources.css_raw == [
                (DIST_DIR / 'bundled/gridstack/gridstack@7.2.3/dist/gridstack.min.css').read_text(encoding='utf-8'),
                (DIST_DIR / 'bundled/gridstack/gridstack@7.2.3/dist/gridstack-extra.min.css').read_text(encoding='utf-8')
            ]

def test_resources_design_server(document):
    resources = Resources(mode='server')
    with set_resource_mode('server'):
        with set_curdoc(document):
            extension(design='bootstrap')
            assert resources.js_files[-1:] == [
                'static/extensions/panel/bundled/bootstrap5/js/bootstrap.bundle.min.js'
            ]

def test_resources_design_cdn(document):
    resources = Resources(mode='cdn')
    with set_resource_mode('cdn'):
        with set_curdoc(document):
            extension(design='bootstrap')
            assert resources.js_files[-1:] == [
                f'{CDN_DIST}bundled/bootstrap5/js/bootstrap.bundle.min.js'
            ]

def test_resources_design_inline(document):
    resources = Resources(mode='inline')
    with set_resource_mode('inline'):
        with set_curdoc(document):
            extension(design='bootstrap')
            assert resources.js_raw[-1:] == [
                (DIST_DIR / 'bundled/bootstrap5/js/bootstrap.bundle.min.js').read_text(encoding='utf-8')
            ]
