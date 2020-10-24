"""Implementation of the [Perspective Viewer]\
(https://github.com/finos/perspective/tree/master/packages/perspective-viewer).
"""

from bokeh.core import properties
from bokeh.models import ColumnDataSource
from bokeh.models.layouts import HTMLBox


class PerspectiveViewer(HTMLBox):
    """A Bokeh Model that enables easy use of perspective-viewer widget
    """

    # pylint: disable=line-too-long
    __javascript__ = [
        "https://unpkg.com/@finos/perspective@0.5.2/dist/umd/perspective.js",
        "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/perspective-viewer.js",
        "https://unpkg.com/@finos/perspective-viewer-datagrid@0.5.2/dist/umd/perspective-viewer-datagrid.js",
        "https://unpkg.com/@finos/perspective-viewer-hypergrid@0.5.2/dist/umd/perspective-viewer-hypergrid.js",
        "https://unpkg.com/@finos/perspective-viewer-d3fc@0.5.2/dist/umd/perspective-viewer-d3fc.js",
    ]

    __js_skip__ = {
        "perspective": __javascript__[0:1],
        "perspective-viewer": __javascript__[1:2],
        "perspective-viewer-datagrid": __javascript__[2:3],
        "perspective-viewer-hypergrid": __javascript__[3:4],
        "perspective-viewer-d3fc": __javascript__[4:5],
    }

    __js_require__ = {
        "paths": {
            "perspective": "https://unpkg.com/@finos/perspective@0.5.2/dist/umd/perspective",
            "perspective-viewer": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/perspective-viewer",
            "perspective-viewer-datagrid": "https://unpkg.com/@finos/perspective-viewer-datagrid@0.5.2/dist/umd/perspective-viewer-datagrid",
            "perspective-viewer-hypergrid": "https://unpkg.com/@finos/perspective-viewer-hypergrid@0.5.2/dist/umd/perspective-viewer-hypergrid",
            "perspective-viewer-d3fc": "https://unpkg.com/@finos/perspective-viewer-d3fc@0.5.2/dist/umd/perspective-viewer-d3fc",
        },
        "exports": {
            "perspective": "Perspective",
            "perspective-viewer": "PerspectiveViewer",
            "perspective-viewer-datagrid": "PerspectiveViewerDatagrid",
            "perspective-viewer-hypergrid": "PerspectiveViewerHypergrid",
            "perspective-viewer-d3fc": "PerspectiveViewerD3fc",
        },
    }

    __css__ = ["https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/all-themes.css"]

    # CSS_FILES = {
    #     "material": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/material.css",
    #     "material-dark": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/material.dark.css",
    #     "material-dense": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/material-dense.css",
    #     "material-dense-dark": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/material-dense.dark.css",
    #     "vaporwave": "https://unpkg.com/@finos/perspective-viewer@0.5.2/dist/umd/vaporwave.css",
    # }

    # pylint: enable=line-too-long

    source = properties.Instance(ColumnDataSource)
    source_stream = properties.Instance(ColumnDataSource)
    source_patch = properties.Instance(ColumnDataSource)

    columns = properties.List(properties.String())
    parsed_computed_columns = properties.List(
        properties.Dict(properties.String(), properties.Any())
    )
    computed_columns = properties.List(properties.String())
    column_pivots = properties.List(properties.String())
    row_pivots = properties.List(properties.String())
    aggregates = properties.Dict(properties.String(), properties.String())
    sort = properties.List(properties.List(properties.String()))
    filters = properties.List(properties.List(properties.Any()))
    plugin = properties.String()
    theme = properties.String()
