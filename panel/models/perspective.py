from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Instance, List, Null, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource

from ..config import config
from ..io.resources import JS_VERSION, bundled_files
from ..util import classproperty
from .layout import HTMLBox

PERSPECTIVE_THEMES = [
    'material', 'material-dark', 'monokai', 'solarized', 'solarized-dark', 'vaporwave'
]

PERSPECTIVE_VERSION = '1.9.3'

THEME_PATH = f"@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/css/"
THEME_URL = f"{config.npm_cdn}/{THEME_PATH}"
PANEL_CDN = f"{config.npm_cdn}/@holoviz/panel@{JS_VERSION}/dist/bundled/perspective/{THEME_PATH}"

CSS_URLS = [
    f"{THEME_URL}fonts.css",
    f"{THEME_URL}themes.css",
    f"{THEME_URL}variables.css"
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

    expressions = Nullable(List(String))

    editable = Bool(default=True)

    filters = Either(List(Any), Null())

    plugin = String()

    plugin_config = Either(Dict(String, Any), Null, default={})

    group_by = Either(List(String), Null())

    selectable = Bool(default=True)

    schema = Dict(String, String)

    sort = Either(List(List(String)), Null())

    source = Instance(ColumnDataSource)

    toggle_config = Bool(True)

    theme = Enum(*PERSPECTIVE_THEMES, default="material")

    # pylint: disable=line-too-long
    __javascript__ = [
        f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/umd/perspective.js",
        f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer-datagrid.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer-d3fc.js",
    ]

    __js_skip__ = {
        "perspective": __javascript__,
    }

    __js_require__ = {
        "paths": {
            "perspective": f"{config.npm_cdn}/@finos/perspective@{PERSPECTIVE_VERSION}/dist/umd/perspective",
            "perspective-viewer": f"{config.npm_cdn}/@finos/perspective-viewer@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer",
            "perspective-viewer-datagrid": f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer-datagrid",
            "perspective-viewer-d3fc": f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@{PERSPECTIVE_VERSION}/dist/umd/perspective-viewer-d3fc",
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
