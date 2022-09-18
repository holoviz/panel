from bokeh.core.properties import (
    Any, Bool, Dict, Either, Instance, List, Null, Nullable, String,
)
from bokeh.models import ColumnDataSource, HTMLBox

from ..config import config


class Perspective(HTMLBox):

    aggregates = Either(Dict(String, Any), Null())

    split_by = Either(List(String), Null())

    columns = Either(List(Either(String, Null)), Null)

    expressions = Either(List(String), Null())

    editable = Nullable(Bool())

    filters = Either(List(Any), Null())

    plugin = String()

    plugin_config = Either(Dict(String, Any), Null)

    group_by = Either(List(String), Null())

    selectable = Nullable(Bool())

    schema = Dict(String, String)

    sort = Either(List(List(String)), Null())

    source = Instance(ColumnDataSource)

    toggle_config = Bool(True)

    theme = String()

    # pylint: disable=line-too-long
    __javascript__ = [
        f"{config.npm_cdn}/@finos/perspective@1.3.6/dist/umd/perspective.js",
        f"{config.npm_cdn}/@finos/perspective-viewer@1.3.6/dist/umd/perspective-viewer.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@1.3.6/dist/umd/perspective-viewer-datagrid.js",
        f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@1.3.6/dist/umd/perspective-viewer-d3fc.js",
    ]

    __js_skip__ = {
        "perspective": __javascript__,
    }

    __js_require__ = {
        "paths": {
            "perspective": f"{config.npm_cdn}/@finos/perspective@1.3.6/dist/umd/perspective",
            "perspective-viewer": f"{config.npm_cdn}/@finos/perspective-viewer@1.3.6/dist/umd/perspective-viewer",
            "perspective-viewer-datagrid": f"{config.npm_cdn}/@finos/perspective-viewer-datagrid@1.3.6/dist/umd/perspective-viewer-datagrid",
            "perspective-viewer-d3fc": f"{config.npm_cdn}/@finos/perspective-viewer-d3fc@1.3.6/dist/umd/perspective-viewer-d3fc",
        },
        "exports": {
            "perspective": "perspective",
            "perspective-viewer": "PerspectiveViewer",
            "perspective-viewer-datagrid": "PerspectiveViewerDatagrid",
            "perspective-viewer-d3fc": "PerspectiveViewerD3fc",
        },
    }

    __css__ = [f"{config.npm_cdn}/@finos/perspective-viewer@1.3.6/dist/css/themes.css"]
