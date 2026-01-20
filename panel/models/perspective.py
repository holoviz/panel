from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Instance, List, Null, String,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource

from ..config import config
from ..io.resources import JS_VERSION, bundled_files
from ..util import classproperty
from .layout import HTMLBox

PERSPECTIVE_THEMES = [
    'monokai', 'solarized', 'solarized-dark', 'vaporwave', 'dracula',
    'pro', 'pro-dark', 'gruvbox', 'gruvbox-dark',
]

PERSPECTIVE_VERSION = '3.8.0'

THEME_PATH = f"@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/css/"
THEME_URL = f"{config.npm_cdn}/{THEME_PATH}"
PANEL_CDN = f"{config.npm_cdn}/@holoviz/panel@{JS_VERSION}/dist/bundled/perspective/{THEME_PATH}"

CSS_URLS = [
    f"{THEME_URL}fonts.css",
    f"{THEME_URL}themes.css",
    f"{THEME_URL}variables.css",
]
for theme in PERSPECTIVE_THEMES:
    CSS_URLS.append(f'{THEME_URL}{theme}.css')

class PerspectiveClickEvent(ModelEvent):

    event_name = 'perspective-click'

    def __init__(self, model, config, column_names, row):
        self.config = config
        self.column_names = column_names
        self.row = row
        super().__init__(model=model)

    def __repr__(self):
        return (
            f'{type(self).__name__}(config={self.config}, '
            f'column_names={self.column_names}, row={self.row}'
        )

class Perspective(HTMLBox):

    aggregates = Either(Dict(String, Any), Null())

    split_by = Either(List(String), Null())

    columns = Either(List(Either(String, Null)), Null())

    columns_config = Either(Dict(String, Any), Null())

    expressions = Either(Dict(String, Any), Null())

    editable = Bool(default=True)

    filters = Either(List(Any), Null())

    plugin = String()

    plugin_config = Either(Dict(String, Any), Null, default={})

    group_by = Either(List(String), Null())

    selectable = Bool(default=True)

    settings = Bool(default=True)

    schema = Dict(String, String)

    sort = Either(List(List(String)), Null())

    source = Instance(ColumnDataSource)

    theme = Enum(*PERSPECTIVE_THEMES, default="pro")

    title = Either(String(), Null())

    __javascript_module_exports__ = ['perspective', 'perspective_viewer']

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/cdn/perspective.js",
        f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer-datagrid.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer-d3fc.js",
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/wasm/perspective-js.js",
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/wasm/perspective-js.wasm",
        f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/wasm/perspective-viewer.js",
        f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/wasm/perspective-viewer.wasm",
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/wasm/perspective-server.wasm",
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/wasm/perspective-server.js"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return [js for js in bundled_files(cls, 'javascript_modules') if 'wasm' not in js]

    @classproperty
    def __js_skip__(cls):
        return {
            "customElements.get('perspective-viewer')": cls.__javascript_modules__
        }

    __js_require__ = {
        "paths": {
            "perspective": f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/cdn/perspective",
            "perspective-worker": f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/cdn/perspective.worker",
            "perspective-viewer": f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer",
            "perspective-viewer-datagrid": f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer-datagrid",
            "perspective-viewer-d3fc": f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@{PERSPECTIVE_VERSION}/dist/cdn/perspective-viewer-d3fc",
        },
        "exports": {
            "perspective": "perspective",
            "perspective-viewer": "PerspectiveViewer",
            "perspective-viewer-datagrid": "PerspectiveViewerDatagrid",
            "perspective-viewer-d3fc": "PerspectiveViewerD3fc",
        },
    }

    __css_raw__ = CSS_URLS

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')
