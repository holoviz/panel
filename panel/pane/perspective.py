from __future__ import annotations

import datetime as dt
import sys

from collections.abc import Callable, Mapping
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, ClassVar

import numpy as np
import param

from bokeh.models import ColumnDataSource, ImportedStyleSheet
from pyviz_comms import JupyterComm

from ..io.state import state
from ..reactive import ReactiveData
from ..util import datetime_types, lazy_load
from ..viewable import Viewable
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..models.perspective import PerspectiveClickEvent

DEFAULT_THEME = "pro"

THEMES = [
    'material', 'material-dark', 'monokai', 'solarized', 'solarized-dark',
    'vaporwave', 'pro', 'pro-dark'
]

class Plugin(Enum):
    """The plugins (grids/charts) available in Perspective.  Pass these into
    the `plugin` arg in `PerspectiveWidget` or `PerspectiveViewer`.
    """

    HYPERGRID = "hypergrid"  # hypergrid
    GRID = "datagrid"  # hypergrid
    YBAR_D3 = "d3_y_bar"  # d3fc
    XBAR_D3 = "d3_x_bar"  # d3fc
    XYLINE_D3 = "d3_xy_line"  # d3fc
    YLINE_D3 = "d3_y_line"  # d3fc
    YAREA_D3 = "d3_y_area"  # d3fc
    YSCATTER_D3 = "d3_y_scatter"  # d3fc
    XYSCATTER_D3 = "d3_xy_scatter"  # d3fc
    TREEMAP_D3 = "d3_treemap"  # d3fc
    SUNBURST_D3 = "d3_sunburst"  # d3fc
    HEATMAP_D3 = "d3_heatmap"  # d3fc
    CANDLESTICK = "d3_candlestick"  # d3fc
    CANDLESTICK_D3 = "d3_candlestick"  # noqa: PIE796, d3fc
    OHLC = "d3_ohlc"  # d3fc
    OHLC_D3 = "d3_ohlc"  # noqa: PIE796, d3fc

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


def deconstruct_pandas(data, kwargs=None):
    """
    Given a dataframe, flatten it by resetting the index and memoizing
    the pivots that were applied.

    This code was copied from the Perspective repository and is
    reproduced under Apache 2.0 license. See the original at:

    https://github.com/finos/perspective/blob/master/python/perspective/perspective/core/data/pd.py

    Arguments
    ---------
    data: (pandas.dataframe)
      A Pandas DataFrame to parse

    Returns
    -------
    data: pandas.DataFrame
      A flattened version of the DataFrame
    kwargs: dict
      A dictionary containing optional members `columns`,
      `group_by`, and `split_by`.
    """
    import pandas as pd
    kwargs = kwargs or {}
    kwargs = {"columns": [], "group_by": [], "split_by": []}

    if isinstance(data.index, pd.PeriodIndex):
        data.index = data.index.to_timestamp()

    if isinstance(data, pd.DataFrame):
        if hasattr(pd, "CategoricalDtype"):
            for k, v in data.dtypes.items():
                if isinstance(v, pd.CategoricalDtype):
                    data[k] = data[k].astype(str)

    if (
        isinstance(data, pd.DataFrame)
        and isinstance(data.columns, pd.MultiIndex)
        and isinstance(data.index, pd.MultiIndex)
    ):
        # Row and col pivots
        kwargs["group_by"].extend([str(c) for c in data.index.names])

        # Two strategies
        if None in data.columns.names:
            # In this case, we need to extract the column names from the row
            # e.g. pt = pd.pivot_table(df, values = ['Discount','Sales'], index=['Country','Region'], columns=["State","Quantity"])
            # Table will be
            #                       Discount             Sales
            #         State       Alabama Alaska ...      Alabama Alaska ...
            #         Quantity    150 350 ...             300 500
            # Country Region
            #  US     Region 0    ...
            #  US     Region 1
            #
            # We need to transform this to:
            # group_by = ['Country', 'Region']
            # split_by = ['State', 'Quantity']
            # columns = ['Discount', 'Sales']
            existent = kwargs["group_by"] + data.columns.names
            for c in data.columns.names:
                if c is not None:
                    kwargs["split_by"].append(c)
                    data = data.stack()
            data = pd.DataFrame(data).reset_index()

            for new_column in data.columns:
                if new_column not in existent:
                    kwargs["columns"].append(new_column)
        else:
            # In this case, we have no need as the values is just a single entry
            # e.g. pt = pd.pivot_table(df, values = 'Discount', index=['Country','Region'], columns = ['Category', 'Segment'])
            for _ in kwargs["group_by"]:
                # unstack row pivots
                data = data.unstack()
            data = pd.DataFrame(data)

        # this rather weird loop is to map existing None columns into
        # levels, e.g. in the `else` block above, to reconstruct
        # the "Discount" name. IDK if this is stored or if the name is
        # lots, so we'll just call it 'index', 'index-1', ...
        i = 0
        new_names = list(data.index.names)
        for j, val in enumerate(data.index.names):
            if val is None:
                new_names[j] = "index" if i == 0 else f"index-{i}"
                i += 1
                # kwargs['group_by'].append(str(new_names[j]))
            else:
                if str(val) not in kwargs["group_by"]:
                    kwargs["split_by"].append(str(val))

        # Finally, remap any values columns to have column name 'value'
        data.index.names = new_names
        data = data.reset_index()  # copy
        data.columns = [
            str(c)
            if c
            in ["index"]
            + kwargs["group_by"]
            + kwargs["split_by"]
            + kwargs["columns"]
            else "value"
            for c in data.columns
        ]
        kwargs["columns"].extend(
            [
                "value"
                for c in data.columns
                if c
                not in ["index"]
                + kwargs["group_by"]
                + kwargs["split_by"]
                + kwargs["columns"]
            ]
        )
    elif isinstance(data, pd.DataFrame) and isinstance(data.columns, pd.MultiIndex):
        # Col pivots
        if data.index.name:
            kwargs["group_by"].append(str(data.index.name))
            push_row_pivot = False
        else:
            push_row_pivot = True

        data = pd.DataFrame(data.unstack())

        i = 0
        new_names = list(data.index.names)
        for j, val in enumerate(data.index.names):
            if val is None:
                new_names[j] = "index" if i == 0 else f"index-{i}"
                i += 1
                if push_row_pivot:
                    kwargs["group_by"].append(str(new_names[j]))
            else:
                if str(val) not in kwargs["group_by"]:
                    kwargs["split_by"].append(str(val))

        data.index.names = new_names
        data.columns = [
            str(c)
            if c in ["index"] + kwargs["group_by"] + kwargs["split_by"]
            else "value"
            for c in data.columns
        ]
        kwargs["columns"].extend(
            [
                "value"
                for c in data.columns
                if c not in ["index"] + kwargs["group_by"] + kwargs["split_by"]
            ]
        )

    elif isinstance(data, pd.DataFrame) and isinstance(data.index, pd.MultiIndex):
        # Row pivots
        kwargs["group_by"].extend(list(data.index.names))
        data = data.reset_index()  # copy

    if isinstance(data, pd.DataFrame):
        # flat df
        if "index" not in [str(c).lower() for c in data.columns]:
            data = data.reset_index(col_fill="index")

        if not kwargs["columns"]:
            # might already be set in row+col pivot df
            kwargs["columns"].extend([str(c) for c in data.columns])
            data.columns = kwargs["columns"]

    if isinstance(data, pd.Series):
        # Series
        flattened = data.reset_index()  # copy

        if isinstance(data, pd.Series):
            # preserve name from series
            flattened.name = data.name

            # make sure all columns are strings
            flattened.columns = [str(c) for c in flattened.columns]

        data = flattened

    return data, kwargs


class Perspective(ModelPane, ReactiveData):
    """
    The `Perspective` pane provides an interactive visualization component for
    large, real-time datasets built on the Perspective project.

    Reference: https://panel.holoviz.org/reference/panes/Perspective.html

    :Example:

    >>> Perspective(df, plugin='hypergrid', theme='pro-dark')
    """

    aggregates = param.Dict(default=None, nested_refs=True, doc="""
      How to aggregate. For example {"x": "distinct count"}""")

    columns = param.List(default=None, nested_refs=True, doc="""
      A list of source columns to show as columns. For example ["x", "y"]""")

    columns_config = param.Dict(default=None, nested_refs=True, doc="""
      Column configuration allowing specification of formatters, coloring
      and a variety of other attributes for each column.""")

    editable = param.Boolean(default=True, allow_None=True, doc="""
      Whether items are editable.""")

    expressions = param.ClassSelector(class_=(dict, list), default=None, nested_refs=True, doc="""
      A list of expressions computing new columns from existing columns.
      For example [""x"+"index""]""")

    split_by = param.List(default=None, nested_refs=True, doc="""
      A list of source columns to pivot by. For example ["x", "y"]""")

    filters = param.List(default=None, nested_refs=True, doc="""
      How to filter. For example [["x", "<", 3],["y", "contains", "abc"]]""")

    min_width = param.Integer(default=420, bounds=(0, None), doc="""
        Minimal width of the component (in pixels) if width is adjustable.""")

    object = param.Parameter(doc="""
      The plot data declared as a dictionary of arrays or a DataFrame.""")

    group_by = param.List(default=None, doc="""
      A list of source columns to group by. For example ["x", "y"]""")

    selectable = param.Boolean(default=True, allow_None=True, doc="""
      Whether items are selectable.""")

    sort = param.List(default=None, doc="""
      How to sort. For example[["x","desc"]]""")

    plugin = param.Selector(default=Plugin.GRID.value, objects=Plugin.options(), doc="""
      The name of a plugin to display the data. For example hypergrid or d3_xy_scatter.""")

    plugin_config = param.Dict(default={}, nested_refs=True, doc="""
      Configuration for the PerspectiveViewerPlugin.""")

    settings = param.Boolean(default=True, doc="""
      Whether to show the settings menu.""")

    theme = param.Selector(default='pro', objects=THEMES, doc="""
      The style of the PerspectiveViewer. For example pro-dark""")

    title = param.String(default=None, doc="""
      Title for the Perspective viewer.""")

    priority: ClassVar[float | bool | None] = None

    _bokeh_model: ClassVar[type[Model] | None] = None

    _data_params: ClassVar[list[str]] = ['object']

    _rename: ClassVar[Mapping[str, str | None]] = {
        'selection': None
    }

    _updates: ClassVar[bool] = True

    @classmethod
    def applies(cls, object):
        if isinstance(object, dict) and all(isinstance(v, (list, np.ndarray)) for v in object.values()):
            return 0 if object else None
        elif 'pandas' in sys.modules:
            import pandas as pd
            if isinstance(object, pd.DataFrame):
                return 0
        return False

    def __init__(self, object=None, **params):
        click_handler = params.pop('on_click', None)
        self._on_click_callbacks = []
        super().__init__(object, **params)
        if click_handler:
            self.on_click(click_handler)

    def _get_data(self):
        if self.object is None:
            return {}, {}
        if isinstance(self.object, dict):
            ncols = len(self.object)
            df = data = self.object
        else:
            df, kwargs = deconstruct_pandas(self.object)
            ncols = len(df.columns)
            data = {col: df[col].values for col in df.columns}
            if kwargs:
                self.param.update(**{
                    k: v for k, v in kwargs.items()
                    if getattr(self, k) is None
                })
        cols = {self._as_digit(c) for c in df}
        if len(cols) != ncols:
            raise ValueError("Integer columns must be unique when "
                             "converted to strings.")
        return df, {str(k): v for k, v in data.items()}

    def _filter_properties(self, properties):
        ignored = list(Viewable.param)
        return [p for p in properties if p not in ignored]

    def _get_properties(self, doc, source=None):
        props = super()._get_properties(doc)
        if 'theme' in props and 'material' in props['theme']:
            props['theme'] = props['theme'].replace('material', 'pro')
        del props['object']
        if source is None:
            source = ColumnDataSource(data=self._data)
        else:
            source.data = self._data
        props['source'] = source
        props['schema'] = schema = {}
        for col, array in source.data.items():
            if not isinstance(array, np.ndarray):
                array = np.asarray(array)
            kind = array.dtype.kind
            if kind == 'M':
                schema[col] = 'datetime'
            elif kind in 'ui':
                schema[col] = 'integer'
            elif kind == 'b':
                schema[col] = 'boolean'
            elif kind == 'f':
                schema[col] = 'float'
            elif kind in 'sU':
                schema[col] = 'string'
            else:
                if len(array):
                    value = array[0]
                    if isinstance(value, datetime_types) and type(value) is not dt.date:
                        schema[col] = 'datetime'
                    elif isinstance(value, dt.date):
                        schema[col] = 'date'
                    elif isinstance(value, str):
                        schema[col] = 'string'
                    elif isinstance(value, (float, np.floating)):
                        schema[col] = 'float'
                    elif isinstance(value, (int, np.integer)):
                        schema[col] = 'integer'
                    else:
                        schema[col] = 'string'
                else:
                    schema[col] = 'string'
        return props

    def _get_theme(self, theme, resources=None):
        from ..models.perspective import THEME_URL
        theme = theme.replace('material', 'pro')
        theme_url = f'{THEME_URL}{theme}.css'
        if self._bokeh_model is not None:
            self._bokeh_model.__css_raw__ = self._bokeh_model.__css_raw__[:5] + [theme_url]
        return theme_url

    def _process_param_change(self, params):
        if 'stylesheets' in params or 'theme' in params:
            self._get_theme(params.get('theme', self.theme))
            css = getattr(self._bokeh_model, '__css__', [])
            params['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css
            ] + params.get('stylesheets', self.stylesheets)
        if 'theme' in params and 'material' in params['theme']:
            params['theme'] = params['theme'].replace('material', 'pro')
        props = super()._process_param_change(params)
        for p in ('columns', 'group_by', 'split_by'):
            if props.get(p):
                props[p] = [None if col is None else str(col) for col in props[p]]
        if props.get('settings'):
            props['height'] = self.height or 300
        else:
            props['height'] = self.height or 150
        if props.get('sort'):
            props['sort'] = [[str(col), *args] for col, *args in props['sort']]
        if props.get('filters'):
            props['filters'] = [[str(col), *args] for col, *args in props['filters']]
        if props.get('aggregates'):
            props['aggregates'] = {str(col): agg for col, agg in props['aggregates'].items()}
        if isinstance(props.get('expressions'), list):
            props['expressions'] = {f'expression_{i}': exp for i, exp in enumerate(props['expressions'])}
        return props

    def _as_digit(self, col):
        if self._processed is None or col in self._processed or col is None:
            return col
        elif col.isdigit() and int(col) in self._processed:
            return int(col)
        return col

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        for prop in ('columns', 'group_by', 'split_by'):
            if prop not in msg:
                continue
            msg[prop] = [self._as_digit(col) for col in msg[prop]]
        if msg.get('sort'):
            msg['sort'] = [[self._as_digit(col), *args] for col, *args in msg['sort']]
        if msg.get('filters'):
            msg['filters'] = [[self._as_digit(col), *args] for col, *args in msg['filters']]
        if msg.get('aggregates'):
            msg['aggregates'] = {self._as_digit(col): agg for col, agg in msg['aggregates'].items()}
        return msg

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        Perspective._bokeh_model = lazy_load(
            'panel.models.perspective', 'Perspective', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('perspective-click', model=model, doc=doc, comm=comm)
        return model

    def _update(self, ref: str, model: Model) -> None:
        model.update(**self._get_properties(model.document, source=model.source))

    def _process_event(self, event):
        if event.event_name == 'perspective-click':
            for cb in self._on_click_callbacks:
                state.execute(partial(cb, event), schedule=False)

    def on_click(self, callback: Callable[[PerspectiveClickEvent], None]):
        """
        Register a callback to be executed when any row is clicked.
        The callback is given a PerspectiveClickEvent declaring the
        config, column names, and row values of the row that was
        clicked.

        Arguments
        ---------
        callback: (callable)
            The callback to run on edit events.
        """
        self._on_click_callbacks.append(callback)
