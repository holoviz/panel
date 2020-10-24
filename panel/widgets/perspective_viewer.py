"""Implementation of the PerspectiveViewer Web Component"""
from enum import Enum
from typing import List

import panel as pn
import param

from panel.models.perspective_viewer import (
    PerspectiveViewer as _BkPerspectiveViewer,
)
from panel.widgets.dataframe_base import DataFrameWithStreamAndPatchBaseWidget

DEFAULT_THEME = "material"
THEMES_MAP = {
    "material": "perspective-viewer-material",
    "material-dark": "perspective-viewer-material-dark",
    "material-dense": "perspective-viewer-material-dense",
    "material-dense-dark": "perspective-viewer-material-dense-dark",
    "vaporwave": "perspective-viewer-vaporwave",
}
THEMES = [*THEMES_MAP.keys()]
# Hack: When the user drags some of the columns, then the class attribute contains "dragging" also.
CSS_CLASS_MAP = {v: k for k, v in THEMES_MAP.items()}
DEFAULT_CSS_CLASS = THEMES_MAP[DEFAULT_THEME]

# Source: https://github.com/finos/perspective/blob/e23988b4b933da6b90fd5767d059a33e70a2493e/python/perspective/perspective/core/plugin.py#L49 # pylint: disable=line-too-long
class Plugin(Enum):
    """The plugins (grids/charts) available in Perspective.  Pass these into
    the `plugin` arg in `PerspectiveWidget` or `PerspectiveViewer`.
    """

    HYPERGRID = "hypergrid"  # hypergrid
    GRID = "datagrid"  # hypergrid
    YBAR_D3 = "d3_y_bar"  # d3fc
    XBAR_D3 = "d3_x_bar"  # d3fc
    YLINE_D3 = "d3_y_line"  # d3fc
    YAREA_D3 = "d3_y_area"  # d3fc
    YSCATTER_D3 = "d3_y_scatter"  # d3fc
    XYSCATTER_D3 = "d3_xy_scatter"  # d3fc
    TREEMAP_D3 = "d3_treemap"  # d3fc
    SUNBURST_D3 = "d3_sunburst"  # d3fc
    HEATMAP_D3 = "d3_heatmap"  # d3fc
    CANDLESTICK = "d3_candlestick"  # d3fc
    CANDLESTICK_D3 = "d3_candlestick"  # d3fc
    OHLC = "d3_ohlc"  # d3fc
    OHLC_D3 = "d3_ohlc"  # d3fc

    @staticmethod
    def options() -> List:
        """Returns the list of options of the PerspectiveViewer, like Hypergrid, Grid etc.

        Returns:
            List: [description]
        """
        return list(c.value for c in Plugin)


class PerspectiveViewer(DataFrameWithStreamAndPatchBaseWidget):  # pylint: disable=abstract-method
    """The PerspectiveViewer widget enables exploring large tables of data"""

    _widget_type = _BkPerspectiveViewer

    columns = param.List(
        None, doc='A list of source columns to show as columns. For example ["x", "y"]'
    )
    # We don't expose this as it is not documented
    # parsed_computed_columns = param.List(
    #     None,
    #     doc='A list of parsed computed columns. For example [{"name":"x+y","func":"add","inputs":["x","y"]}]',
    # )
    computed_columns = param.List(
        None, doc='A list of computed columns. For example [""x"+"index""]',
    )
    column_pivots = param.List(
        None, doc='A list of source columns to pivot by. For example ["x", "y"]'
    )
    row_pivots = param.List(
        None, doc='A list of source columns to group by. For example ["x", "y"]'
    )
    aggregates = param.Dict(None, doc='How to aggregate. For example {x: "distinct count"}')
    sort = param.List(None, doc='How to sort. For example[["x","desc"]]')
    filters = param.List(
        None, doc='How to filter. For example [["x", "<", 3],["y", "contains", "abc"]]'
    )

    theme = param.ObjectSelector(
        DEFAULT_THEME,
        objects=THEMES,
        doc="The style of the PerspectiveViewer. For example material-dark",
    )
    plugin = param.ObjectSelector(
        Plugin.GRID.value,
        objects=Plugin.options(),
        doc="The name of a plugin to display the data. For example hypergrid or d3_xy_scatter.",
    )

    # I set this to something > 0. Otherwise the PerspectiveViewer widget will have a height of 0px
    # It will appear as if it does not work.
    height = param.Integer(default=300, bounds=(0, None))

    def __init__(self, **params):
        super().__init__(**params)

        self._set_source()
