import sys

from enum import Enum

import param

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..reactive import ReactiveData
from ..util import lazy_load
from ..viewable import Viewable
from .base import PaneBase

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
    def options():
        """
        Returns the list of options of the PerspectiveViewer, like Hypergrid, Grid etc.

        Returns
        -------
        options: list
          A list of available options
        """
        return list(c.value for c in Plugin)


class Perspective(PaneBase, ReactiveData):
    """
    The Perspective widget enables exploring large tables of data.
    """

    aggregates = param.Dict(None, doc="""
      How to aggregate. For example {x: "distinct count"}""")
 
    columns = param.List(default=None, doc="""
        A list of source columns to show as columns. For example ["x", "y"]""")

    computed_columns = param.List(default=None, doc="""
      A list of computed columns. For example [""x"+"index""]""")

    column_pivots = param.List(None, doc="""
      A list of source columns to pivot by. For example ["x", "y"]""")

    filters = param.List(default=None, doc="""
      How to filter. For example [["x", "<", 3],["y", "contains", "abc"]]""")

    object = param.Parameter(doc="""
      The plot data declared as a dictionary of arrays or a DataFrame.""")

    row_pivots = param.List(default=None, doc="""
      A list of source columns to group by. For example ["x", "y"]""")

    selectable = param.Boolean(default=True, allow_None=True, doc="""
      Whether items are selectable.""")

    sort = param.List(default=None, doc="""
      How to sort. For example[["x","desc"]]""")

    plugin = param.ObjectSelector(default=Plugin.GRID.value, objects=Plugin.options(), doc="""
      The name of a plugin to display the data. For example hypergrid or d3_xy_scatter.""")

    toggle_config = param.Boolean(default=True, doc="""
      Whether to show the config menu.""")

    theme = param.ObjectSelector(default=DEFAULT_THEME, objects=THEMES, doc="""
      The style of the PerspectiveViewer. For example material-dark""")

    _data_params = ['object']

    _rerender_params = ['object']

    _updates = True

    def applies(cls, object):
        if isinstance(object, dict):
            return True
        elif 'pandas' in sys.modules:
            import pandas as pd
            return isinstance(object, pd.DataFrame)
        return False

    def _get_data(self):
        if self.object is None:
            return None, {}
        elif isinstance(self.object, dict):
            return self.object, self.object
        return self.object, ColumnDataSource.from_df(self.object)

    def _filter_properties(self, properties):
        ignored = list(Viewable.param)
        return [p for p in properties if p not in ignored]

    def _init_params(self):
        props = super()._init_params()
        props['source'] = ColumnDataSource(data=self._data)
        return props

    def _get_model(self, doc, root=None, parent=None, comm=None):
        Perspective = lazy_load('panel.models.perspective', 'Perspective', isinstance(comm, JupyterComm))
        properties = self._process_param_change(self._init_params())
        if properties.get('toggle_config'):
            properties['height'] = self.height or 300
        else:
            properties['height'] = self.height or 150
        model = Perspective(**properties)
        if root is None:
            root = model
        synced = list(set(self.param) ^ (set(PaneBase.param) | set(ReactiveData.param)))
        self._link_props(model, synced, doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref, model):
        pass
