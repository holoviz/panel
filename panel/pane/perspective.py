# @Philippfr: I would like to move this to file to panel.widgets.
# But I get below error when I do
# File "C:\repos\private\panel\panel\widgets\select.py", line 19, in <module>
# from ..layout import Column, VSpacer
# ImportError: attempted relative import with no known parent package
# Can you help?

# FYI. There is an issue with Perspective. See https://github.com/finos/perspective/issues/964
import param

import panel as pn
from panel.pane.web_component import WebComponent
from bokeh.models import ColumnDataSource

JS_FILES = {
    "perspective": "https://unpkg.com/@finos/perspective@0.4.5/dist/umd/perspective.js",
    "perspective-viewer": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/perspective-viewer.js",
    "perspective-viewer-hypergrid": "https://unpkg.com/@finos/perspective-viewer-hypergrid@0.4.5/dist/umd/perspective-viewer-hypergrid.js",
    "perspective-viewer-d3fc": "https://unpkg.com/@finos/perspective-viewer-d3fc@0.4.5/dist/umd/perspective-viewer-d3fc.js",
}

CSS_FILES = {
    "all": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/all-themes.css",
    "material": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/material.css",
    "material.dark": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/material.dark.css",
    "material-dense": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/material-dense.css",
    "material-dense.dark": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/material-dense.dark.css",
    "vaporwave": "https://unpkg.com/@finos/perspective-viewer@0.4.5/dist/umd/vaporwave.css",
}

THEMES = {
    "material": "perspective-viewer-material",
    "material-dark": "perspective-viewer-material-dark",
    "material-dense": "perspective-viewer-material-dense",
    "material-dense-dark": "perspective-viewer-material-dense-dark",
    "vaporwave": "perspective-viewer-vaporwave",
}
#Hack; When the user drags some of the columns, then the class attribute contains "dragging" also.
THEMES_DRAGGING = {key + " dragging": value + " dragging" for key, value in THEMES.items()}
THEMES = {**THEMES, **THEMES_DRAGGING}

from enum import Enum

# Source: https://github.com/finos/perspective/blob/e23988b4b933da6b90fd5767d059a33e70a2493e/python/perspective/perspective/core/plugin.py#L49
class Plugin(Enum):
    '''The plugins (grids/charts) available in Perspective.  Pass these into
    the `plugin` arg in `PerspectiveWidget` or `PerspectiveViewer`.
    Examples:
        >>> widget = PerspectiveWidget(data, plugin=Plugin.TREEMAP)
    '''
    HYPERGRID = 'hypergrid'  # hypergrid
    GRID = 'hypergrid'  # hypergrid

    YBAR = 'y_bar'  # highcharts
    XBAR = 'x_bar'  # highcharts
    YLINE = 'y_line'  # highcharts
    YAREA = 'y_area'  # highcharts
    YSCATTER = 'y_scatter'  # highcharts
    XYLINE = 'xy_line'  # highcharts
    XYSCATTER = 'xy_scatter'  # highcharts
    TREEMAP = 'treemap'  # highcharts
    SUNBURST = 'sunburst'  # highcharts
    HEATMAP = 'heatmap'  # highcharts

    YBAR_D3 = 'd3_y_bar'  # d3fc
    XBAR_D3 = 'd3_x_bar'  # d3fc
    YLINE_D3 = 'd3_y_line'  # d3fc
    YAREA_D3 = 'd3_y_area'  # d3fc
    YSCATTER_D3 = 'd3_y_scatter'  # d3fc
    XYSCATTER_D3 = 'd3_xy_scatter'  # d3fc
    TREEMAP_D3 = 'd3_treemap'  # d3fc
    SUNBURST_D3 = 'd3_sunburst'  # d3fc
    HEATMAP_D3 = 'd3_heatmap'  # d3fc

    CANDLESTICK = 'd3_candlestick'  # d3fc
    CANDLESTICK_D3 = 'd3_candlestick'  # d3fc
    OHLC = 'd3_ohlc'  # d3fc
    OHLC_D3 = 'd3_ohlc'  # d3fc

    @staticmethod
    def options():
        return list(c.value for c in Plugin)

def extend():
    for key, value in JS_FILES.items():
        pn.config.js_files[key] = value
    pn.config.css_files.append(CSS_FILES["all"])


class Perspective(WebComponent):
    html = param.String(
        """
    <perspective-viewer id="view1" class='perspective-viewer-material-dark' style="height:100%;width:100%"></perspective-viewer>
    """
    )
    attributes_to_watch = param.Dict({
        "class": "theme",
        "plugin": "plugin",
        "rows": "rows",
        "row-pivots": "row_pivots",
        "columns": "columns",
        "column-pivots": "column_pivots",
        "sort": "sort",
        "aggregates": "aggregates", # Have not been able to manually test this one
        "filters": "filters",
    })

    theme = param.ObjectSelector("perspective-viewer-material-dark", objects=THEMES)
    plugin = param.ObjectSelector(Plugin.GRID.value, objects=Plugin.options())
    rows = param.List(None)
    row_pivots = param.List(None)
    column_pivots = param.List(None)
    columns = param.List(None)
    aggregates = param.List(None)
    sort = param.List(None)
    filters = param.List(None)

    # @Philipfr: Is it ok WebComponent is dependent on pandas or should the users just use
    # ColumnDataSource?
    # And in general the datatransfer might be improved using some kind of functionality like Arrow
    # from the Perspective python package. Should we look into this?
    data = param.DataFrame(doc="""
    The data will be reloaded in full when ever it changes."""
    )



    def __init__(self, **params):
        self.param.column_data_source_orient.default="records"
        self.param.column_data_source_load_function.default="load"

        super().__init__(**params)
        self._set_column_data_source()

    @param.depends("data", watch=True)
    def _set_column_data_source(self):
        if not self.data is None:
            self.column_data_source = ColumnDataSource(ColumnDataSource.from_df(self.data))
        else:
            self.column_data_source = ColumnDataSource()
