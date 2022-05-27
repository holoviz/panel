from bokeh.core.properties import (
    Any, Bool, Dict, Either, Instance, List, Null, Nullable, String,
)
from bokeh.models import ColumnDataSource, HTMLBox


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
        "https://unpkg.com/@finos/perspective@1.3.6/dist/umd/perspective.js",
        "https://unpkg.com/@finos/perspective-viewer@1.3.6/dist/umd/perspective-viewer.js",
        "https://unpkg.com/@finos/perspective-viewer-datagrid@1.3.6/dist/umd/perspective-viewer-datagrid.js",
        "https://unpkg.com/@finos/perspective-viewer-d3fc@1.3.6/dist/umd/perspective-viewer-d3fc.js",
    ]

    __js_skip__ = {
        "perspective": __javascript__,
    }

    __js_require__ = {
        "paths": {
            "perspective": "https://unpkg.com/@finos/perspective@1.3.6/dist/umd/perspective",
            "perspective-viewer": "https://unpkg.com/@finos/perspective-viewer@1.3.6/dist/umd/perspective-viewer",
            "perspective-viewer-datagrid": "https://unpkg.com/@finos/perspective-viewer-datagrid@1.3.6/dist/umd/perspective-viewer-datagrid",
            "perspective-viewer-d3fc": "https://unpkg.com/@finos/perspective-viewer-d3fc@1.3.6/dist/umd/perspective-viewer-d3fc",
        },
        "exports": {
            "perspective": "perspective",
            "perspective-viewer": "PerspectiveViewer",
            "perspective-viewer-datagrid": "PerspectiveViewerDatagrid",
            "perspective-viewer-d3fc": "PerspectiveViewerD3fc",
        },
    }

    __css__ = ["https://unpkg.com/@finos/perspective-viewer@1.3.6/dist/css/themes.css"]
