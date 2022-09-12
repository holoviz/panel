from __future__ import annotations

import datetime as dt
import uuid

from functools import partial
from types import FunctionType, MethodType
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Mapping, Optional,
    Tuple, Type, TypeVar,
)

import numpy as np
import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets.tables import (
    AvgAggregator, CellEditor, CellFormatter, CheckboxEditor, DataCube,
    DataTable, DateEditor, DateFormatter, GroupingInfo, IntEditor,
    MaxAggregator, MinAggregator, NumberEditor, NumberFormatter, RowAggregator,
    StringEditor, StringFormatter, SumAggregator, TableColumn,
)
from bokeh.util.serialization import convert_datetime_array
from pyviz_comms import JupyterComm

from ..depends import param_value_if_widget
from ..io.resources import LOCAL_DIST, set_resource_mode
from ..io.state import state
from ..reactive import ReactiveData
from ..util import (
    clone_model, isdatetime, lazy_load, updating,
)
from ..viewable import Layoutable
from .base import Widget
from .button import Button
from .input import TextInput

if TYPE_CHECKING:
    try:
        import pandas as pd
        DataFrameType = pd.DataFrame
    except Exception:
        DataFrameType = TypeVar('DataFrameType')

    from bokeh.document import Document
    from bokeh.model import Model
    from bokeh.models.sources import DataDict
    from pyviz_comms import Comm

    from ..models.tabulator import CellClickEvent, TableEditEvent


class BaseTable(ReactiveData, Widget):

    aggregators = param.Dict(default={}, doc="""
        A dictionary mapping from index name to an aggregator to
        be used for hierarchical multi-indexes (valid aggregators
        include 'min', 'max', 'mean' and 'sum'). If separate
        aggregators for different columns are required the dictionary
        may be nested as `{index_name: {column_name: aggregator}}`""")

    editors = param.Dict(default={}, doc="""
        Bokeh CellEditor to use for a particular column
        (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, doc="""
        Bokeh CellFormatter to use for a particular column
        (overrides the default chosen based on the type).""")

    hierarchical = param.Boolean(default=False, constant=True, doc="""
        Whether to generate a hierachical index.""")

    row_height = param.Integer(default=40, doc="""
        The height of each table row.""")

    selection = param.List(default=[], doc="""
        The currently selected rows of the table.""")

    show_index = param.Boolean(default=True, doc="""
        Whether to show the index column.""")

    sorters = param.List(default=[], doc="""
        A list of sorters to apply during pagination.""")

    text_align = param.ClassSelector(default={}, class_=(dict, str), doc="""
        A mapping from column name to alignment or a fixed column
        alignment, which should be one of 'left', 'center', 'right'.""")

    titles = param.Dict(default={}, doc="""
        A mapping from column name to a title to override the name with.""")

    widths = param.ClassSelector(default={}, class_=(dict, int), doc="""
        A mapping from column name to column width or a fixed column
        width.""")

    value = param.Parameter(default=None)

    _data_params: ClassVar[List[str]] = ['value']

    _manual_params: ClassVar[List[str]] = [
        'formatters', 'editors', 'widths', 'titles', 'value', 'show_index'
    ]

    _rename: ClassVar[Mapping[str, str | None]] = {'disabled': 'editable', 'selection': None}

    __abstract = True

    def __init__(self, value=None, **params):
        self._renamed_cols = {}
        self._filters = []
        super().__init__(value=value, **params)

    @param.depends('value', watch=True, on_init=True)
    def _compute_renamed_cols(self):
        if self.value is None:
            self._renamed_cols.clear()
            return
        self._renamed_cols = {
            str(col) if str(col) != col else col: col for col in self._get_fields()
        }

    def _validate(self, *events: param.parameterized.Event):
        if self.value is None:
            return
        cols = self.value.columns
        if len(cols) != len(cols.drop_duplicates()):
            raise ValueError('Cannot display a pandas.DataFrame with '
                             'duplicate column names.')

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'editable' in msg:
            msg['editable'] = not msg.pop('editable') and len(self.indexes) <= 1
        return msg

    def _get_fields(self) -> List[str]:
        indexes = self.indexes
        col_names = list(self.value.columns)
        if not self.hierarchical or len(indexes) == 1:
            col_names = indexes + col_names
        else:
            col_names = indexes[-1:] + col_names
        return col_names

    def _get_columns(self) -> List[TableColumn]:
        if self.value is None:
            return []

        indexes = self.indexes
        fields = self._get_fields()
        df = self.value.reset_index() if len(indexes) > 1 else self.value
        return self._get_column_definitions(fields, df)

    def _get_column_definitions(self, col_names: List[str], df: DataFrameType) -> List[TableColumn]:
        import pandas as pd
        indexes = self.indexes
        columns = []
        for col in col_names:
            if col in df.columns:
                data = df[col]
            elif col in self.indexes:
                if len(self.indexes) == 1:
                    data = df.index
                else:
                    data = df.index.get_level_values(self.indexes.index(col))

            if isinstance(data, pd.DataFrame):
                raise ValueError("DataFrame contains duplicate column names.")

            col_kwargs = {}
            kind = data.dtype.kind
            editor: CellEditor
            formatter: CellFormatter
            if kind == 'i':
                formatter = NumberFormatter(text_align='right')
                editor = IntEditor()
            elif kind == 'b':
                formatter = StringFormatter(text_align='center')
                editor = CheckboxEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]', text_align='right')
                editor = NumberEditor()
            elif isdatetime(data) or kind == 'M':
                if len(data) and isinstance(data.values[0], dt.date):
                    date_format = '%Y-%m-%d'
                else:
                    date_format = '%Y-%m-%d %H:%M:%S'
                formatter = DateFormatter(format=date_format, text_align='right')
                editor = DateEditor()
            else:
                formatter = StringFormatter()
                editor = StringEditor()

            if isinstance(self.text_align, str):
                formatter.text_align = self.text_align
            elif col in self.text_align:
                formatter.text_align = self.text_align[col]
            elif col in self.indexes:
                formatter.text_align = 'left'

            if col in self.editors and not isinstance(self.editors[col], (dict, str)):
                editor = self.editors[col]
                if isinstance(editor, CellEditor):
                    editor = clone_model(editor)

            if col in indexes or editor is None:
                editor = CellEditor()

            if col in self.formatters and not isinstance(self.formatters[col], (dict, str)):
                formatter = self.formatters[col]
                if isinstance(formatter, CellFormatter):
                    formatter = clone_model(formatter)

            if isinstance(self.widths, int):
                col_kwargs['width'] = self.widths
            elif str(col) in self.widths and isinstance(self.widths.get(str(col)), int):
                col_kwargs['width'] = self.widths.get(str(col))
            else:
                col_kwargs['width'] = 0

            title = self.titles.get(col, str(col))
            if col in indexes and len(indexes) > 1 and self.hierarchical:
                title = 'Index: %s' % ' | '.join(indexes)
            elif col in self.indexes and col.startswith('level_'):
                title = ''
            column = TableColumn(field=str(col), title=title,
                                 editor=editor, formatter=formatter,
                                 **col_kwargs)
            columns.append(column)
        return columns

    @updating
    def _update_cds(self, *events: param.parameterized.Event):
        old_processed = self._processed
        self._processed, data = self._get_data()
        # If there is a selection we have to compute new index
        if self.selection and old_processed is not None:
            indexes = list(self._processed.index)
            selection = []
            for sel in self.selection:
                try:
                    iv = old_processed.index[sel]
                    idx = indexes.index(iv)
                    selection.append(idx)
                except Exception:
                    continue
            self.selection = selection
        self._data = {k: convert_datetime_array(v) for k, v in data.items()}
        msg = {'data': self._data}
        for ref, (m, _) in self._models.items():
            self._apply_update(events, msg, m.source, ref)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        source = ColumnDataSource(data=self._data)
        source.selected.indices = self.selection # type: ignore
        properties = self._get_properties(source)
        model = self._widget_type(**properties)
        if root is None:
            root = model
        self._link_props(model.source, ['data'], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_columns(self, event: param.parameterized.Event, model: Model):
        if event.name == 'value' and [c.field for c in model.columns] == self._get_fields():
            # Skip column update if the data has changed but the columns
            # have not
            return
        model.columns = self._get_columns()

    def _manual_update(
        self, events: Tuple[param.parameterized.Event, ...], model: Model, doc: Document,
        root: Model, parent: Optional[Model], comm: Optional[Comm]
    ) -> None:
        for event in events:
            if event.type == 'triggered' and self._updating:
                continue
            elif event.name in ('value', 'show_index'):
                self._update_columns(event, model)
                if isinstance(model, DataCube):
                    model.groupings = self._get_groupings()
            elif hasattr(self, '_update_' + event.name):
                getattr(self, '_update_' + event.name)(model)
            else:
                self._update_columns(event, model)

    def _sort_df(self, df: DataFrameType) -> DataFrameType:
        if not self.sorters:
            return df
        fields = [self._renamed_cols.get(s['field'], s['field']) for s in self.sorters]
        ascending = [s['dir'] == 'asc' for s in self.sorters]

        # Temporarily add _index_ column because Tabulator uses internal _index
        # as additional sorter to break ties
        df['_index_'] = np.arange(len(df)).astype(str)
        fields.append('_index_')
        ascending.append(True)

        # Handle sort on index column if show_index=True
        if self.show_index:
            rename = 'index' in fields and df.index.name is None
            if rename:
                df.index.name = 'index'
        else:
            rename = False

        def tabulator_sorter(col):
            # Tabulator JS defines its own sorting algorithm:
            # - strings's case isn't taken into account
            if col.dtype.kind not in 'SUO':
                return col
            try:
                return col.str.lower()
            except Exception:
                return col

        df_sorted = df.sort_values(fields, ascending=ascending, kind='mergesort',
                                  key=tabulator_sorter)

        # Revert temporary changes to DataFrames
        if rename:
            df.index.name = None
            df_sorted.index.name = None
        df.drop(columns=['_index_'], inplace=True)
        df_sorted.drop(columns=['_index_'], inplace=True)
        return df_sorted

    def _filter_dataframe(self, df: DataFrameType) -> DataFrameType:
        """
        Filter the DataFrame.

        Parameters
        ----------
        df : DataFrame
           The DataFrame to filter

        Returns
        -------
        DataFrame
            The filtered DataFrame
        """
        filters = []
        for col_name, filt in self._filters:
            if isinstance(filt, (FunctionType, MethodType)):
                df = filt(df)
                continue
            if isinstance(filt, param.Parameter):
                val = getattr(filt.owner, filt.name)
            else:
                val = filt
            column = df[col_name]
            if np.isscalar(val):
                mask = column == val
            elif isinstance(val, (list, set)):
                if not val:
                    continue
                mask = column.isin(val)
            elif isinstance(val, tuple):
                start, end = val
                if start is None and end is None:
                    continue
                elif start is None:
                    mask = column<=end
                elif end is None:
                    mask = column>=start
                else:
                    mask = (column>=start) & (column<=end)
            else:
                raise ValueError(f"'{col_name} filter value not "
                                 "understood. Must be either a scalar, "
                                 "tuple or list.")
            filters.append(mask)

        filters.extend(self._get_header_filters(df))

        if filters:
            mask = filters[0]
            for f in filters:
                mask &= f
            df = df[mask]
        return df

    def _get_header_filters(self, df):
        filters = []
        for filt in getattr(self, 'filters', []):
            col_name = filt['field']
            op = filt['type']
            val = filt['value']
            filt_def = getattr(self, 'header_filters', {}) or {}
            if col_name in df.columns:
                col = df[col_name]
            elif col_name in self.indexes:
                if len(self.indexes) == 1:
                    col = df.index
                else:
                    col = df.index.get_level_values(self.indexes.index(col_name))

            # Sometimes Tabulator will provide a zero/single element list
            if isinstance(val, list):
                if len(val) == 1:
                    val = val[0]
                elif not val:
                    continue

            val = col.dtype.type(val)
            if op == '=':
                filters.append(col == val)
            elif op == '!=':
                filters.append(col != val)
            elif op == '<':
                filters.append(col < val)
            elif op == '>':
                filters.append(col > val)
            elif op == '>=':
                filters.append(col >= val)
            elif op == '<=':
                filters.append(col <= val)
            elif op == 'in':
                filters.append(col.isin(val))
            elif op == 'like':
                filters.append(col.str.lower().str.contains(val.lower()))
            elif op == 'starts':
                filters.append(col.str.startsWith(val))
            elif op == 'ends':
                filters.append(col.str.endsWith(val))
            elif op == 'keywords':
                match_all = filt_def.get(col_name, {}).get('matchAll', False)
                sep = filt_def.get(col_name, {}).get('separator', ' ')
                matches = val.lower().split(sep)
                if match_all:
                    for match in matches:
                        filters.append(col.str.lower().str.contains(match))
                else:
                    filt = col.str.lower().str.contains(matches[0])
                    for match in matches[1:]:
                        filt |= col.str.lower().str.contains(match)
                    filters.append(filt)
            elif op == 'regex':
                raise ValueError("Regex filtering not supported.")
            else:
                raise ValueError(f"Filter type {op!r} not recognized.")
        return filters

    def add_filter(self, filter, column=None):
        """
        Adds a filter to the table which can be a static value or
        dynamic parameter based object which will automatically
        update the table when changed..

        When a static value, widget or parameter is supplied the
        filtering will follow a few well defined behaviors:

          * scalar: Filters by checking for equality
          * tuple: A tuple will be interpreted as range.
          * list: A list will be interpreted as a set of discrete
                  scalars and the filter will check if the values
                  in the column match any of the items in the list.

        Arguments
        ---------
        filter: Widget, param.Parameter or FunctionType
            The value by which to filter the DataFrame along the
            declared column, or a function accepting the DataFrame to
            be filtered and returning a filtered copy of the DataFrame.
        column: str or None
            Column to which the filter will be applied, if the filter
            is a constant value, widget or parameter.

        Raises
        ------
        ValueError: If the filter type is not supported or no column
                    was declared.
        """
        if isinstance(filter, (tuple, list, set)) or np.isscalar(filter):
            deps = []
        elif isinstance(filter, (FunctionType, MethodType)):
            deps = list(filter._dinfo['kw'].values()) if hasattr(filter, '_dinfo') else []
        else:
            filter = param_value_if_widget(filter)
            if not isinstance(filter, param.Parameter):
                raise ValueError(f'{type(self).__name__} filter must be '
                                 'a constant value, parameter, widget '
                                 'or function.')
            elif column is None:
                raise ValueError('When filtering with a parameter or '
                                 'widget, a column to filter on must be '
                                 'declared.')
            deps = [filter]
        for dep in deps:
            dep.owner.param.watch(self._update_cds, dep.name)
        self._filters.append((column, filter))
        self._update_cds()

    def remove_filter(self, filter):
        """
        Removes a filter which was previously added.
        """
        self._filters = [(column, filt) for (column, filt) in self._filters
                         if filt is not filter]
        self._update_cds()

    def _process_column(self, values):
        if not isinstance(values, (list, np.ndarray)):
            return [str(v) for v in values]
        return values

    def _get_data(self) -> Tuple[DataFrameType, DataDict]:
        return self._process_df_and_convert_to_cds(self.value)

    def _process_df_and_convert_to_cds(self, df: DataFrameType) -> Tuple[DataFrameType, DataDict]:
        import pandas as pd
        df = self._filter_dataframe(df)
        if df is None:
            return [], {}
        if isinstance(self.value.index, pd.MultiIndex):
            indexes = [
                f'level_{i}' if n is None else n
                for i, n in enumerate(df.index.names)
            ]
        else:
            default_index = ('level_0' if 'index' in df.columns else 'index')
            indexes = [df.index.name or default_index]
        if len(indexes) > 1:
            df = df.reset_index()
        data = ColumnDataSource.from_df(df)
        if not self.show_index:
            data = {k: v for k, v in data.items() if k not in indexes}
        return df, {k if isinstance(k, str) else str(k): self._process_column(v) for k, v in data.items()}

    def _update_column(self, column, array):
        self.value[column] = array
        if self._processed is not None and self.value is not self._processed:
            self._processed[column] = array

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def indexes(self):
        import pandas as pd
        if self.value is None or not self.show_index:
            return []
        elif isinstance(self.value.index, pd.MultiIndex):
            return [
                f'level_{i}' if n is None else n
                for i, n in enumerate(self.value.index.names)
            ]
        default_index = ('level_0' if 'index' in self.value.columns else 'index')
        return [self.value.index.name or default_index]

    def stream(self, stream_value, rollover=None, reset_index=True):
        """
        Streams (appends) the `stream_value` provided to the existing
        value in an efficient manner.

        Arguments
        ---------
        stream_value: (pd.DataFrame | pd.Series | Dict)
          The new value(s) to append to the existing value.
        rollover: int
           A maximum column size, above which data from the start of
           the column begins to be discarded. If None, then columns
           will continue to grow unbounded.
        reset_index: (bool, default=True)
          If True and the stream_value is a DataFrame,
          then its index is reset. Helps to keep the
          index unique and named `index`

        Raises
        ------
        ValueError: Raised if the stream_value is not a supported type.

        Examples
        --------

        Stream a Series to a DataFrame
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = pd.Series({"x": 4, "y": "d"})
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Stream a Dataframe to a Dataframe
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}

        Stream a Dictionary row to a DataFrame
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = {"x": 4, "y": "d"}
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Stream a Dictionary of Columns to a Dataframe
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> stream_value = {"x": [3, 4], "y": ["c", "d"]}
        >>> tabulator.stream(stream_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}
        """
        import pandas as pd

        if not np.isfinite(self.value.index.max()):
            value_index_start = 1
        else:
            value_index_start = self.value.index.max() + 1

        if isinstance(stream_value, pd.DataFrame):
            if reset_index:
                stream_value = stream_value.reset_index(drop=True)
                stream_value.index += value_index_start
            combined = pd.concat([self.value, stream_value])
            if rollover is not None:
                combined = combined.iloc[-rollover:]
            with param.discard_events(self):
                self.value = combined
            try:
                self._updating = True
                self.param.trigger('value')
            finally:
                self._updating = False
            stream_value, stream_data = self._process_df_and_convert_to_cds(stream_value)
            try:
                self._updating = True
                self._stream(stream_data, rollover)
            finally:
                self._updating = False
        elif isinstance(stream_value, pd.Series):
            self.value.loc[value_index_start] = stream_value
            if rollover is not None and len(self.value) > rollover:
                with param.discard_events(self):
                    self.value = self.value.iloc[-rollover:]
            stream_value, stream_data = self._process_df_and_convert_to_cds(self.value.iloc[-1:])
            try:
                self._updating = True
                self._stream(stream_data, rollover)
            finally:
                self._updating = False
        elif isinstance(stream_value, dict):
            if stream_value:
                try:
                    stream_value = pd.DataFrame(stream_value)
                except ValueError:
                    stream_value = pd.Series(stream_value)
                self.stream(stream_value, rollover)
        else:
            raise ValueError("The stream value provided is not a DataFrame, Series or Dict!")

    def patch(self, patch_value, as_index=True):
        """
        Efficiently patches (updates) the existing value with the `patch_value`.

        Arguments
        ---------
        patch_value: (pd.DataFrame | pd.Series | Dict)
          The value(s) to patch the existing value with.
        as_index: boolean
          Whether to treat the patch index as DataFrame indexes (True)
          or as simple integer index.

        Raises
        ------
        ValueError: Raised if the patch_value is not a supported type.

        Examples
        --------

        Patch a DataFrame with a Dictionary row.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = {"x": [(0, 3)]}
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 2], 'y': ['a', 'b']}

        Patch a Dataframe with a Dictionary of Columns.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = {"x": [(slice(2), (3,4))], "y": [(1,'d')]}
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 4], 'y': ['a', 'd']}

        Patch a DataFrame with a Series. Please note the index is used in the update.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = pd.Series({"index": 1, "x": 4, "y": "d"})
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [1, 4], 'y': ['a', 'd']}

        Patch a Dataframe with a Dataframe. Please note the index is used in the update.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = Tabulator(value=value)
        >>> patch_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> tabulator.patch(patch_value)
        >>> tabulator.value.to_dict("list")
        {'x': [3, 4], 'y': ['c', 'd']}
        """
        if self.value is None:
            raise ValueError(f"Cannot patch empty {type(self).__name__}.")

        import pandas as pd
        if not isinstance(self.value, pd.DataFrame):
            raise ValueError(
                f"Patching an object of type {type(self.value).__name__} "
                "is not supported. Please provide a dict."
            )

        if isinstance(patch_value, pd.DataFrame):
            patch_value_dict = {
                column: list(patch_value[column].items()) for column in patch_value.columns
            }
            self.patch(patch_value_dict, as_index=as_index)
        elif isinstance(patch_value, pd.Series):
            if "index" in patch_value:  # Series orient is row
                patch_value_dict = {
                    k: [(patch_value["index"], v)] for k, v in patch_value.items()
                }
                patch_value_dict.pop("index")
            else:  # Series orient is column
                patch_value_dict = {patch_value.name: list(patch_value.items())}
            self.patch(patch_value_dict, as_index=as_index)
        elif isinstance(patch_value, dict):
            columns = list(self.value.columns)
            for k, v in patch_value.items():
                for (ind, value) in v:
                    if isinstance(ind, slice):
                        ind = range(ind.start, ind.stop, ind.step or 1)
                    if as_index:
                        self.value.loc[ind, k] = value
                    else:
                        self.value.iloc[ind, columns.index(k)] = value
            self._patch(patch_value)
        else:
            raise ValueError(
                f"Patching with a patch_value of type {type(patch_value).__name__} "
                "is not supported. Please provide a DataFrame, Series or Dict."
            )

    @property
    def current_view(self):
        """
        Returns the current view of the table after filtering and
        sorting are applied.
        """
        df = self._processed
        return self._sort_df(df)

    @property
    def selected_dataframe(self):
        """
        Returns a DataFrame of the currently selected rows.
        """
        if not self.selection:
            return self.current_view.iloc[:0]
        return self.current_view.iloc[self.selection]


class DataFrame(BaseTable):
    """
    The `DataFrame` widget allows displaying and editing a pandas DataFrame.

    Note that editing is not possible for multi-indexed DataFrames, in which
    case you will need to reduce the DataFrame to a single index.

    Also note that the `DataFrame` widget will eventually be replaced with the
    `Tabulator` widget, and so new code should be written to use `Tabulator`
    instead.

    Reference: https://panel.holoviz.org/reference/widgets/DataFrame.html

    :Example:

    >>> DataFrame(df, name='DataFrame')
    """

    auto_edit = param.Boolean(default=False, doc="""
        Whether clicking on a table cell automatically starts edit mode.""")

    autosize_mode = param.ObjectSelector(default='force_fit', objects=[
        "none", "fit_columns", "fit_viewport", "force_fit"], doc="""

        Determines the column autosizing mode, as one of the following options:

        ``"fit_columns"``
          Compute column widths based on cell contents while ensuring the
          table fits into the available viewport. This results in no
          horizontal scrollbar showing up, but data can get unreadable
          if there is not enough space available.

        ``"fit_viewport"``
          Adjust the viewport size after computing column widths based
          on cell contents.

        ``"force_fit"``
          Fit columns into available space dividing the table width across
          the columns equally (equivalent to `fit_columns=True`).
          This results in no horizontal scrollbar showing up, but data
          can get unreadable if there is not enough space available.

        ``"none"``
          Do not automatically compute column widths.""")

    fit_columns = param.Boolean(default=None, doc="""
        Whether columns should expand to the available width. This
        results in no horizontal scrollbar showing up, but data can
        get unreadable if there is no enough space available.""")

    frozen_columns = param.Integer(default=None, doc="""
        Integer indicating the number of columns to freeze. If set, the
        first N columns will be frozen, which prevents them from
        scrolling out of frame.""")

    frozen_rows = param.Integer(default=None, doc="""
       Integer indicating the number of rows to freeze. If set, the
       first N rows will be frozen, which prevents them from scrolling
       out of frame; if set to a negative value the last N rows will be
       frozen.""")

    reorderable = param.Boolean(default=True, doc="""
        Allows the reordering of a table's columns. To reorder a
        column, click and drag a table's header to the desired
        location in the table.  The columns on either side will remain
        in their previous order.""")

    sortable = param.Boolean(default=True, doc="""
        Allows to sort table's contents. By default natural order is
        preserved.  To sort a column, click on its header. Clicking
        one more time changes sort direction. Use Ctrl + click to
        return to natural order. Use Shift + click to sort multiple
        columns simultaneously.""")

    _manual_params: ClassVar[List[str]] = BaseTable._manual_params + ['aggregators']

    _aggregators = {'sum': SumAggregator, 'max': MaxAggregator,
                    'min': MinAggregator, 'mean': AvgAggregator}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'hierarchical': None}

    _rename: ClassVar[Mapping[str, str | None]] = {
        'disabled': 'editable', 'selection': None, 'sorters': None,
        'text_align': None
    }

    @property
    def _widget_type(self) -> Type[Model]:
        return DataCube if self.hierarchical else DataTable

    def _get_columns(self):
        if self.value is None:
            return []

        indexes = self.indexes
        col_names = list(self.value.columns)
        if not self.hierarchical or len(indexes) == 1:
            col_names = indexes + col_names
        else:
            col_names = indexes[-1:] + col_names
        df = self.value.reset_index() if len(indexes) > 1 else self.value
        return self._get_column_definitions(col_names, df)

    def _get_groupings(self):
        if self.value is None:
            return []

        groups = []
        for group, agg_group in zip(self.indexes[:-1], self.indexes[1:]):
            if str(group) != group:
                self._renamed_cols[str(group)] = group
            aggs = self._get_aggregators(agg_group)
            groups.append(GroupingInfo(getter=str(group), aggregators=aggs))
        return groups

    def _get_aggregators(self, group):
        numeric_cols = list(self.value.select_dtypes(include='number').columns)
        aggs = self.aggregators.get(group, [])
        if not isinstance(aggs, list):
            aggs = [aggs]
        expanded_aggs = []
        for col_aggs in aggs:
            if not isinstance(col_aggs, dict):
                col_aggs = {col: col_aggs for col in numeric_cols}
            for col, agg in col_aggs.items():
                if isinstance(agg, str):
                    agg = self._aggregators.get(agg)
                if issubclass(agg, RowAggregator):
                    expanded_aggs.append(agg(field_=str(col)))
        return expanded_aggs

    def _get_properties(self, source):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        if props.get('height', None) is None:
            data = source.data
            length = max([len(v) for v in data.values()]) if data else 0
            props['height'] = min([length * self.row_height + 30, 2000])
        if self.hierarchical:
            props['target'] = ColumnDataSource(data=dict(row_indices=[], labels=[]))
            props['grouping'] = self._get_groupings()
        props['source'] = source
        props['columns'] = self._get_columns()
        props['index_position'] = None
        props['fit_columns'] = self.fit_columns
        if 'autosize_mode' in DataTable.properties():
            props['frozen_columns'] = self.frozen_columns
            props['frozen_rows'] = self.frozen_rows
            props['autosize_mode'] = self.autosize_mode
            props['auto_edit'] = self.auto_edit
        props['row_height'] = self.row_height
        props['editable'] = not self.disabled and len(self.indexes) <= 1
        props['sortable'] = self.sortable
        props['reorderable'] = self.reorderable
        return props

    def _update_aggregators(self, model):
        for g in model.grouping:
            group = self._renamed_cols.get(g.getter, g.getter)
            index = self.indexes[self.indexes.index(group)+1]
            g.aggregators = self._get_aggregators(index)


class Tabulator(BaseTable):
    """
    The `Tabulator` widget wraps the [Tabulator js](http://tabulator.info/)
    table to provide a full-featured, very powerful interactive table.

    Reference: https://panel.holoviz.org/reference/widgets/Tabulator.html

    :Example:

    >>> Tabulator(df, theme='site', pagination='remote', page_size=25)
    """

    buttons = param.Dict(default={}, doc="""
        Dictionary mapping from column name to a HTML element
        to use as the button icon.""")

    expanded = param.List(default=[], doc="""
        List of expanded rows, only applicable if a row_content function
        has been defined.""")

    embed_content = param.Boolean(default=False, doc="""
        Whether to embed the row_content or render it dynamically
        when a row is expanded.""")

    filters = param.List(default=[], doc="""
        List of client-side filters declared as dictionaries containing
        'field', 'type' and 'value' keys.""")

    frozen_columns = param.List(default=[], doc="""
        List indicating the columns to freeze. The column(s) may be
        selected by name or index.""")

    frozen_rows = param.List(default=[], doc="""
        List indicating the rows to freeze. If set, the
        first N rows will be frozen, which prevents them from scrolling
        out of frame; if set to a negative value the last N rows will be
        frozen.""")

    groups = param.Dict(default={}, doc="""
        Dictionary mapping defining the groups.""")

    groupby = param.List(default=[], doc="""
        Groups rows in the table by one or more columns.""")

    header_align = param.ClassSelector(default={}, class_=(dict, str), doc="""
        A mapping from column name to alignment or a fixed column
        alignment, which should be one of 'left', 'center', 'right'.""")

    header_filters = param.ClassSelector(class_=(bool, dict), doc="""
        Whether to enable filters in the header or dictionary
        configuring filters for each column.""")

    hidden_columns = param.List(default=[], doc="""
        List of columns to hide.""")

    layout = param.ObjectSelector(default='fit_data_table', objects=[
        'fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table',
        'fit_columns'])

    pagination = param.ObjectSelector(default=None, allow_None=True,
                                      objects=['local', 'remote'])

    page = param.Integer(default=1, doc="""
        Currently selected page (indexed starting at 1), if pagination is enabled.""")

    page_size = param.Integer(default=20, bounds=(1, None), doc="""
        Number of rows to render per page, if pagination is enabled.""")

    row_content = param.Callable(doc="""
        A function which is given the DataFrame row and should return
        a Panel object to render as additional detail below the row.""")

    row_height = param.Integer(default=30, doc="""
        The height of each table row.""")

    selectable = param.ClassSelector(
        default=True, class_=(bool, str, int), doc="""
        Defines the selection mode of the Tabulator.

          - True
              Selects rows on click. To select multiple use Ctrl-select,
              to select a range use Shift-select
          - False
              Disables selection
          - 'checkbox'
              Adds a column of checkboxes to toggle selections
          - 'checkbox-single'
              Same as 'checkbox' but header does not alllow select/deselect all
          - 'toggle'
              Selection toggles when clicked
          - int
              The maximum number of selectable rows.
        """)

    selectable_rows = param.Callable(default=None, doc="""
        A function which given a DataFrame should return a list of
        rows by integer index, which are selectable.""")

    theme = param.ObjectSelector(
        default="simple", objects=[
            'default', 'site', 'simple', 'midnight', 'modern', 'bootstrap',
            'bootstrap4', 'materialize', 'bulma', 'semantic-ui', 'fast'
        ], doc="""
        Tabulator CSS theme to apply to table.""")

    _data_params: ClassVar[List[str]] = [
        'value', 'page', 'page_size', 'pagination', 'sorters', 'filters'
    ]

    _config_params: ClassVar[List[str]] = [
        'frozen_columns', 'groups', 'selectable', 'hierarchical'
    ]

    _content_params: ClassVar[List[str]] = _data_params + ['expanded', 'row_content', 'embed_content']

    _manual_params: ClassVar[List[str]] = BaseTable._manual_params + _config_params

    _priority_changes: ClassVar[List[str]] = ['data']

    _rename: ClassVar[Mapping[str, str | None]] = {
        'disabled': 'editable', 'selection': None, 'selectable': 'select_mode',
        'row_content': None, 'row_height': None, 'text_align': None,
        'embed_content': None, 'header_align': None, 'header_filters': None
    }

    # Determines the maximum size limits beyond which (local, remote)
    # pagination is enabled
    _MAX_ROW_LIMITS: ClassVar[Tuple[int, int]] = (200, 10000)

    def __init__(self, value=None, **params):
        import pandas.io.formats.style
        if isinstance(value, pandas.io.formats.style.Styler):
            style = value
            value = value.data
        else:
            style = None
        configuration = params.pop('configuration', {})
        self.style = None
        self._computed_styler = None
        self._child_panels = {}
        self._explicit_pagination = 'pagination' in params
        self._on_edit_callbacks = []
        self._on_click_callbacks = {}
        super().__init__(value=value, **params)
        self._configuration = configuration
        self.param.watch(self._update_children, self._content_params)
        if style is not None:
            self.style._todo = style._todo

    @param.depends('value', watch=True, on_init=True)
    def _apply_max_size(self):
        """
        Ensure large tables automatically enable remote pagination.
        """
        if self.value is None or self._explicit_pagination:
            return
        with param.parameterized.discard_events(self):
            if self.hierarchical:
                pass
            elif self._MAX_ROW_LIMITS[0] < len(self.value) <= self._MAX_ROW_LIMITS[1]:
                self.pagination = 'local'
            elif len(self.value) > self._MAX_ROW_LIMITS[1]:
                self.pagination = 'remote'
        self._explicit_pagination = False

    @param.depends('pagination', watch=True)
    def _set_explicict_pagination(self):
        self._explicit_pagination = True

    @staticmethod
    def _validate_iloc(idx, iloc):
        # Validate that the index returned by Pandas get_loc is a single int,
        # as get_loc can return a slice or a mask array when it finds more
        # than one locations.
        if not isinstance(iloc, int):
            raise ValueError(
                'The Tabulator widget expects the provided `value` Pandas DataFrame '
                'to have unique indexes, in particular when it has to deal with '
                f'click or edit events. Found this duplicate index: {idx!r}'
            )

    def _validate(self, *events):
        super()._validate(*events)
        if self.value is not None:
            todo = []
            if self.style is not None:
                todo = self.style._todo
            try:
                self.style = self.value.style
                self.style._todo = todo
            except Exception:
                pass

    def _cleanup(self, root: Model | None = None) -> None:
        for p in self._child_panels.values():
            p._cleanup(root)
        super()._cleanup(root)

    def _process_event(self, event):
        event_col = self._renamed_cols.get(event.column, event.column)
        processed = self._sort_df(self._processed)
        if self.pagination in ['local', 'remote']:
            nrows = self.page_size
            event.row = event.row+(self.page-1)*nrows
        event_row = event.row
        if event_col not in self.buttons:
            if event_col not in processed.columns:
                event.value = processed.index[event_row]
            else:
                event.value = processed[event_col].iloc[event_row]
        # Set the old attribute on a table edit event
        if event.event_name == 'table-edit' and self._old is not None:
            old_processed = self._sort_df(self._old)
            event.old = old_processed[event_col].iloc[event_row]
        # We want to return the index of the original `value` dataframe.
        if self._filters or self.filters or self.sorters:
            idx = processed.index[event.row]
            iloc = self.value.index.get_loc(idx)
            self._validate_iloc(idx, iloc)
            event.row = iloc
        if event.event_name == 'table-edit':
            for cb in self._on_edit_callbacks:
                print(cb)
                state.execute(partial(cb, event))
            self._update_style()
        else:
            for cb in self._on_click_callbacks.get(None, []):
                state.execute(partial(cb, event))
            for cb in self._on_click_callbacks.get(event_col, []):
                state.execute(partial(cb, event))

    def _get_theme(self, theme, resources=None):
        from ..io.resources import RESOURCE_MODE
        from ..models.tabulator import (
            _TABULATOR_THEMES_MAPPING, THEME_PATH, THEME_URL, _get_theme_url,
        )
        if RESOURCE_MODE == 'server' and resources in (None, 'server'):
            theme_url = f'{LOCAL_DIST}bundled/datatabulator/{THEME_PATH}'
            if state.rel_path:
                theme_url = f'{state.rel_path}/{theme_url}'
        else:
            theme_url = THEME_URL
        # Ensure theme_url updates before theme
        cdn_url = _get_theme_url(THEME_URL, theme)
        theme_url = _get_theme_url(theme_url, theme)
        theme_ = _TABULATOR_THEMES_MAPPING.get(self.theme, self.theme)
        fname = 'tabulator' if theme_ == 'default' else 'tabulator_' + theme_
        if self._widget_type is not None:
            self._widget_type.__css_raw__ = [f'{cdn_url}{fname}.min.css']
        return theme_url, theme

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'frozen_rows' in msg:
            length = self._length
            msg['frozen_rows'] = [
                length+r if r < 0 else r for r in msg['frozen_rows']
            ]
        if 'theme' in msg:
            msg['theme_url'], msg['theme'] = self._get_theme(msg.pop('theme'))
        if msg.get('select_mode') == 'checkbox-single':
            msg['select_mode'] = 'checkbox'
        return msg

    def _update_columns(self, event, model):
        if event.name not in self._config_params:
            super()._update_columns(event, model)
            if (event.name in ('editors', 'formatters') and
                not any(isinstance(v, (str, dict)) for v in event.new.values())):
                # If no tabulator editor/formatter was changed we can skip
                # update to config
                return
        model.configuration = self._get_configuration(model.columns)

    def _process_data(self, data):
        # Extending _process_data to cover the case when header filters are
        # active and a cell is edited. In that case the data received from the
        # front-end is the full table, not just the filtered one. However the
        # _processed data is already filtered, this made the comparison between
        # the new data and old data wrong. This extension replicates the
        # front-end filtering - if need be - to be able to correctly make the
        # comparison and update the data hold by the backend.
        if not self.filters:
            return super()._process_data(data)
        import pandas as pd
        df = pd.DataFrame(data)
        filters = self._get_header_filters(df)
        if filters:
            mask = filters[0]
            for f in filters:
                mask &= f
            df = df[mask]
        data = {
            col: df[col].values for col in df.columns
        }
        return super()._process_data(data)

    def _get_data(self):
        if self.pagination != 'remote' or self.value is None:
            return super()._get_data()
        import pandas as pd
        df = self._filter_dataframe(self.value)
        df = self._sort_df(df)
        nrows = self.page_size
        start = (self.page-1)*nrows
        page_df = df.iloc[start: start+nrows]
        if isinstance(self.value.index, pd.MultiIndex):
            indexes = [
                f'level_{i}' if n is None else n
                for i, n in enumerate(df.index.names)
            ]
        else:
            default_index = ('level_0' if 'index' in df.columns else 'index')
            indexes = [df.index.name or default_index]
        if len(indexes) > 1:
            page_df = page_df.reset_index()
        data = ColumnDataSource.from_df(page_df).items()
        return df, {k if isinstance(k, str) else str(k): v for k, v in data}

    @property
    def _length(self):
        return len(self._processed)

    def _get_style_data(self, recompute=True):
        if self.value is None or self.style is None:
            return {}
        df = self._processed
        if recompute:
            try:
                self._computed_styler = styler = df.style
            except Exception:
                self._computed_styler = None
                return {}
            if styler is None:
                return {}
            styler._todo = self.style._todo
            styler._compute()
        else:
            styler = self._computed_styler
        if styler is None:
            return {}
        offset = 1 + len(self.indexes) + int(self.selectable in ('checkbox', 'checkbox-single')) + int(bool(self.row_content))
        if self.pagination == 'remote':
            start = (self.page-1)*self.page_size
            end = start + self.page_size
        styles = {}
        for (r, c), s in styler.ctx.items():
            if self.pagination == 'remote':
                if (r < start or r >= end):
                    continue
                else:
                    r -= start
            if r not in styles:
                styles[int(r)] = {}
            styles[int(r)][offset+int(c)] = s
        return {'id': uuid.uuid4().hex, 'data': styles}

    def _get_selectable(self):
        if self.value is None or self.selectable_rows is None:
            return None
        df = self._processed
        if self.pagination == 'remote':
            nrows = self.page_size
            start = (self.page-1)*nrows
            df = df.iloc[start:(start+nrows)]
        return self.selectable_rows(df)

    def _update_style(self, recompute=True):
        styles = self._get_style_data(recompute)
        msg = {'styles': styles}
        for ref, (m, _) in self._models.items():
            self._apply_update([], msg, m, ref)

    def _get_children(self, old={}):
        if self.row_content is None or self.value is None:
            return {}
        from ..pane import panel
        df = self._processed
        if self.pagination == 'remote':
            nrows = self.page_size
            start = (self.page-1)*nrows
            df = df.iloc[start:(start+nrows)]
        children = {}
        for i in (range(len(df)) if self.embed_content else self.expanded):
            if i in old:
                children[i] = old[i]
            else:
                children[i] = panel(self.row_content(df.iloc[i]))
        return children

    def _get_model_children(self, panels, doc, root, parent, comm=None):
        ref = root.ref['id']
        models = {}
        for i, p in panels.items():
            if ref in p._models:
                model = p._models[ref][0]
            else:
                model = p._get_model(doc, root, parent, comm)
            model.margin = (0, 0, 0, 0)
            models[i] = model
        return models

    def _update_children(self, *events):
        cleanup, reuse = set(), set()
        page_events = ('page', 'page_size', 'value', 'pagination')
        for event in events:
            if event.name == 'expanded' and len(events) == 1:
                cleanup = set(event.old) - set(event.new)
                reuse = set(event.old) & set(event.new)
            elif ((event.name in page_events and not self._updating) or
                  (self.pagination == 'remote' and event.name == 'sorters')):
                self.expanded = []
                return
        old_panels = self._child_panels
        self._child_panels = child_panels = self._get_children(
            {i: old_panels[i] for i in reuse}
        )
        for ref, (m, _) in self._models.items():
            root, doc, comm = state._views[ref][1:]
            for idx in cleanup:
                old_panels[idx]._cleanup(root)
            children = self._get_model_children(
                child_panels, doc, root, m, comm
            )
            msg = {'children': children}
            self._apply_update([], msg, m, ref)

    @updating
    def _stream(self, stream, rollover=None, follow=True):
        if self.pagination == 'remote':
            length = self._length
            nrows = self.page_size
            max_page = max(length//nrows + bool(length%nrows), 1)
            if self.page != max_page:
                return
        super()._stream(stream, rollover)
        self._update_style()
        self._update_selectable()

    def stream(self, stream_value, rollover=None, reset_index=True, follow=True):
        for ref, (model, _) in self._models.items():
            self._apply_update([], {'follow': follow}, model, ref)
        if follow and self.pagination:
            length = self._length
            nrows = self.page_size
            self.page = max(length//nrows + bool(length%nrows), 1)
        super().stream(stream_value, rollover, reset_index)
        if follow and self.pagination:
            self._update_max_page()

    @updating
    def _patch(self, patch):
        if self.filters or self.sorters:
            self._updating = False
            self._update_cds()
            return
        if self.pagination == 'remote':
            nrows = self.page_size
            start = (self.page-1)*nrows
            end = start+nrows
            filtered = {}
            for c, values in patch.items():
                values = [(ind, val) for (ind, val) in values
                          if ind >= start and ind < end]
                if values:
                    filtered[c] = values
            patch = filtered
        if not patch:
            return
        super()._patch(patch)
        self._update_style()
        self._update_selectable()

    def _update_cds(self, *events):
        page_events = ('page', 'page_size', 'sorters', 'filters')
        if self._updating:
            return
        elif (events and all(e.name in page_events for e in events) and not self.pagination):
            self._processed, _ = self._get_data()
            return
        recompute = not all(
            e.name in ('page', 'page_size', 'pagination') for e in events
        )
        super()._update_cds(*events)
        if self.pagination:
            self._update_max_page()
            self._update_selected()
        self._update_style(recompute)
        self._update_selectable()

    def _update_selectable(self):
        selectable = self._get_selectable()
        for ref, (model, _) in self._models.items():
            self._apply_update([], {'selectable_rows': selectable}, model, ref)

    def _update_max_page(self):
        length = self._length
        nrows = self.page_size
        max_page = max(length//nrows + bool(length%nrows), 1)
        self.param.page.bounds = (1, max_page)
        for ref, (model, _) in self._models.items():
            self._apply_update([], {'max_page': max_page}, model, ref)

    def _update_selected(self, *events: param.parameterized.Event, indices=None):
        kwargs = {}
        if self.pagination == 'remote' and self.value is not None:
            index = self.value.iloc[self.selection].index
            indices = []
            for v in index.values:
                try:
                    iloc = self._processed.index.get_loc(v)
                    self._validate_iloc(v ,iloc)
                    indices.append(iloc)
                except KeyError:
                    continue
            nrows = self.page_size
            start = (self.page-1)*nrows
            end = start+nrows
            kwargs['indices'] = [ind-start for ind in indices
                                 if ind>=start and ind<end]
        super()._update_selected(*events, **kwargs)

    def _update_column(self, column: str, array: np.ndarray):
        if self.pagination != 'remote':
            index = self._processed.index.values
            self.value.loc[index, column] = array
            self._processed[column] = array
            return
        nrows = self.page_size
        start = (self.page-1)*nrows
        end = start+nrows
        index = self._processed.iloc[start:end].index.values
        self.value[column].loc[index] = array
        self._processed[column].loc[index] = array

    def _update_selection(self, indices: List[int]):
        if self.pagination != 'remote':
            self.selection = indices
            return
        nrows = self.page_size
        start = (self.page-1)*nrows
        index = self._processed.iloc[[start+ind for ind in indices]].index
        indices = []
        for v in index.values:
            try:
                iloc = self.value.index.get_loc(v)
                self._validate_iloc(v, iloc)
                indices.append(iloc)
            except KeyError:
                continue
        self.selection = indices

    def _get_properties(self, source: ColumnDataSource) -> Dict[str, Any]:
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        columns = self._get_columns()
        if self.selectable == 'checkbox-single':
            selectable = 'checkbox'
        else:
            selectable = self.selectable
        props.update({
            'aggregators': self.aggregators,
            'buttons': self.buttons,
            'expanded': self.expanded,
            'source': source,
            'styles': self._get_style_data(),
            'columns': columns,
            'configuration': self._get_configuration(columns),
            'page': self.page,
            'pagination': self.pagination,
            'page_size': self.page_size,
            'layout': self.layout,
            'groupby': self.groupby,
            'hidden_columns': self.hidden_columns,
            'editable': not self.disabled,
            'select_mode': selectable,
            'selectable_rows': self._get_selectable(),
            'sorters': self.sorters
        })
        process = {'theme': self.theme, 'frozen_rows': self.frozen_rows}
        props.update(self._process_param_change(process))
        if self.pagination:
            length = 0 if self._processed is None else len(self._processed)
            props['max_page'] = max(length//self.page_size + bool(length%self.page_size), 1)
        if self.frozen_rows and 'height' not in props and 'sizing_mode' not in props:
            length = self.page_size+2 if self.pagination else self._length
            props['height'] = min([length * self.row_height + 30, 2000])
        props['indexes'] = self.indexes
        return props

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.tabulator', 'DataTabulator', isinstance(comm, JupyterComm), root
            )
        if comm:
            with set_resource_mode('inline'):
                model = super()._get_model(doc, root, parent, comm)
        else:
            model = super()._get_model(doc, root, parent, comm)
        if root is None:
            root = model
        self._child_panels = child_panels = self._get_children()
        model.children = self._get_model_children(
            child_panels, doc, root, parent, comm
        )
        self._link_props(model, ['page', 'sorters', 'expanded', 'filters'], doc, root, comm)
        self._register_events('cell-click', 'table-edit', model=model, doc=doc, comm=comm)
        return model

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        if comm and 'theme_url' in msg:
            msg['theme_url'], msg['theme'] = self._get_theme(
                msg.pop('theme'), 'inline'
            )
        super()._update_model(events, msg, root, model, doc, comm)

    def _get_filter_spec(self, column: TableColumn) -> Dict[str, Any]:
        fspec = {}
        if not self.header_filters or (isinstance(self.header_filters, dict) and
                                       column.field not in self.header_filters):
            return fspec
        elif self.header_filters == True:
            if column.field in self.indexes:
                if len(self.indexes) == 1:
                    col = self.value.index
                else:
                    col = self.value.index.get_level_values(self.indexes.index(column.field))
                if col.dtype.kind in 'uif':
                    fspec['headerFilter'] = 'number'
                elif col.dtype.kind == 'b':
                    fspec['headerFilter'] = 'tickCross'
                    fspec['headerFilterParams'] = {'tristate': True, 'indeterminateValue': None}
                else:
                    fspec['headerFilter'] = True
            else:
                fspec['headerFilter'] = True
            return fspec
        filter_type = self.header_filters[column.field]
        if isinstance(filter_type, dict):
            filter_params = dict(filter_type)
            filter_type = filter_params.pop('type', True)
            filter_func = filter_params.pop('func', None)
            filter_placeholder = filter_params.pop('placeholder', None)
        else:
            filter_params = {}
            filter_func = None
            filter_placeholder = None
        fspec['headerFilter'] = filter_type
        if filter_type == 'select' and not filter_params:
            filter_params = {'values': True}
        fspec['headerFilter'] = filter_type
        if filter_params:
            fspec['headerFilterParams'] = filter_params
        if filter_func:
            fspec['headerFilterFunc'] = filter_func
        if filter_placeholder:
            fspec['headerFilterPlaceholder'] = filter_placeholder
        return fspec

    def _config_columns(self, column_objs: List[TableColumn]) -> List[Dict[str, Any]]:
        column_objs = list(column_objs)
        groups = {}
        columns = []
        selectable = self.selectable
        if self.row_content:
            columns.append({
                "formatter": "expand"
            })
        if isinstance(selectable, str) and selectable.startswith('checkbox'):
            title = "" if selectable.endswith('-single') else "rowSelection"
            columns.append({
                "formatter": "rowSelection",
                "titleFormatter": title,
                "hozAlign": "center",
                "headerSort": False,
                "frozen": True,
                "width": 40,
            })

        ordered = []
        for col in self.frozen_columns:
            if isinstance(col, int):
                ordered.append(column_objs.pop(col))
            else:
                cols = [c for c in column_objs if c.field == col]
                if cols:
                    ordered.append(cols[0])
                    column_objs.remove(cols[0])
        ordered += column_objs

        grouping = {
            group: [str(gc) for gc in group_cols]
            for group, group_cols in self.groups.items()
        }
        for i, column in enumerate(ordered):
            matching_groups = [
                group for group, group_cols in grouping.items()
                if column.field in group_cols
            ]
            col_dict = {'field': column.field}
            if isinstance(self.text_align, str):
                col_dict['hozAlign'] = self.text_align
            elif column.field in self.text_align:
                col_dict['hozAlign'] = self.text_align[column.field]
            if isinstance(self.header_align, str):
                col_dict['headerHozAlign'] = self.header_align
            elif column.field in self.header_align:
                col_dict['headerHozAlign'] = self.header_align[column.field]
            formatter = self.formatters.get(column.field)
            if isinstance(formatter, str):
                col_dict['formatter'] = formatter
            elif isinstance(formatter, dict):
                formatter = dict(formatter)
                col_dict['formatter'] = formatter.pop('type')
                col_dict['formatterParams'] = formatter
            editor = self.editors.get(column.field)
            if column.field in self.editors and editor is None:
                col_dict['editable'] = False
            if isinstance(editor, str):
                col_dict['editor'] = editor
            elif isinstance(editor, dict):
                editor = dict(editor)
                col_dict['editor'] = editor.pop('type')
                col_dict['editorParams'] = editor
            if column.field in self.frozen_columns or i in self.frozen_columns:
                col_dict['frozen'] = True
            if isinstance(self.widths, dict) and isinstance(self.widths.get(column.field), str):
                col_dict['width'] = self.widths[column.field]
            col_dict.update(self._get_filter_spec(column))
            if matching_groups:
                group = matching_groups[0]
                if group in groups:
                    groups[group]['columns'].append(col_dict)
                    continue
                group_dict = {
                    'title': group,
                    'columns': [col_dict]
                }
                groups[group] = group_dict
                columns.append(group_dict)
            else:
                columns.append(col_dict)
        return columns

    def _get_configuration(self, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Returns the Tabulator configuration.
        """
        configuration = dict(self._configuration)
        if 'selectable' not in configuration:
            configuration['selectable'] = self.selectable
        if self.groups and 'columns' in configuration:
            raise ValueError("Groups must be defined either explicitly "
                             "or via the configuration, not both.")
        configuration['columns'] = self._config_columns(columns)
        configuration['dataTree'] = self.hierarchical
        if self.sizing_mode in ('stretch_height', 'stretch_both'):
            configuration['maxHeight'] = '100%'
        elif self.height:
            configuration['height'] = self.height
        return configuration

    def download(self, filename: str = 'table.csv'):
        """
        Triggers downloading of the table as a CSV or JSON.

        Arguments
        ---------
        filename: str
            The filename to save the table as.
        """
        for ref, (model, _) in self._models.items():
            self._apply_update({}, {'filename': filename}, model, ref)
            self._apply_update({}, {'download': not model.download}, model, ref)

    def download_menu(self, text_kwargs={}, button_kwargs={}):
        """
        Returns a menu containing a TextInput and Button widget to set
        the filename and trigger a client-side download of the data.

        Arguments
        ---------
        text_kwargs: dict
            Keyword arguments passed to the TextInput constructor
        button_kwargs: dict
            Keyword arguments passed to the Button constructor

        Returns
        -------
        filename: TextInput
            The TextInput widget setting a filename.
        button: Button
            The Button that triggers a download.
        """
        text_kwargs = dict(text_kwargs)
        if 'name' not in text_kwargs:
            text_kwargs['name'] = 'Filename'
        if 'value' not in text_kwargs:
            text_kwargs['value'] = 'table.csv'
        filename = TextInput(**text_kwargs)

        button_kwargs = dict(button_kwargs)
        if 'name' not in button_kwargs:
            button_kwargs['name'] = 'Download'
        button = Button(**button_kwargs)
        button.js_on_click({'table': self, 'filename': filename}, code="""
        table.filename = filename.value
        table.download = !table.download
        """)
        return filename, button

    def on_edit(self, callback: Callable[[TableEditEvent], None]):
        """
        Register a callback to be executed when a cell is edited.
        Whenever a cell is edited on_edit callbacks are called with
        a TableEditEvent as the first argument containing the column,
        row and value of the edited cell.

        Arguments
        ---------
        callback: (callable)
            The callback to run on edit events.
        """
        self._on_edit_callbacks.append(callback)

    def on_click(self, callback: Callable[[CellClickEvent], None], column: Optional[str] = None):
        """
        Register a callback to be executed when any cell is clicked.
        The callback is given a CellClickEvent declaring the column
        and row of the cell that was clicked.

        Arguments
        ---------
        callback: (callable)
            The callback to run on edit events.
        column: (str)
            Optional argument restricting the callback to a specific
            column.
        """
        if column not in self._on_click_callbacks:
            self._on_click_callbacks[column] = []
        self._on_click_callbacks[column].append(callback)

    @property
    def current_view(self) -> DataFrameType:
        """
        Returns the current view of the table after filtering and
        sorting are applied.
        """
        df = self._processed
        if self.pagination == 'remote':
            return df
        return self._sort_df(df)
