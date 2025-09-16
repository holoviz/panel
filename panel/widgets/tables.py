from __future__ import annotations

import datetime as dt
import uuid

from collections.abc import Callable, Mapping
from functools import partial
from types import FunctionType, MethodType
from typing import (
    TYPE_CHECKING, Any, ClassVar, Literal, Sequence, TypedDict, cast,
)

import numpy as np
import param

from bokeh.core.serialization import Serializer
from bokeh.model import Model
from bokeh.models import ColumnDataSource, ImportedStyleSheet
from bokeh.models.widgets.tables import (
    AvgAggregator, CellEditor, CellFormatter, CheckboxEditor, DataCube,
    DataTable, DateEditor, DateFormatter, GroupingInfo, IntEditor,
    MaxAggregator, MinAggregator, NumberEditor, NumberFormatter, RowAggregator,
    StringEditor, StringFormatter, SumAggregator, TableColumn,
)
from bokeh.util.serialization import convert_datetime_array
from param.parameterized import transform_reference
from pyviz_comms import JupyterComm

from ..io.model import JSCode
from ..io.resources import CDN_DIST, CSS_URLS
from ..io.state import state
from ..reactive import Reactive, ReactiveData
from ..util import (
    clone_model, datetime_as_utctimestamp, isdatetime, lazy_load,
    styler_update, updating,
)
from ..util.warnings import warn
from .base import Widget
from .button import Button
from .input import TextInput

if TYPE_CHECKING:
    import pandas as pd

    from bokeh.document import Document
    from bokeh.models.sources import DataDict
    from pyviz_comms import Comm

    from ..models.tabulator import (
        CellClickEvent, SelectionEvent, TableEditEvent,
    )
    from ..reactive import TDataColumn

    class FilterSpec(TypedDict, total=False):
        headerFilter: str | bool
        headerFilterParams: dict[str, Any]
        headerFilterFunc: str
        headerFilterPlaceholder: str

class ColumnSpec(TypedDict, total=False):
    editable: bool
    editor: str | CellEditor | JSCode
    editorParams: dict[str, Any]
    field: str
    frozen: bool
    headerHozAlign: Literal["center", "left", "right"]
    headerSort: bool
    headerTooltip: str
    hozAlign: Literal["center", "left", "right"]
    formatter: str | CellFormatter | JSCode
    formatterParams: dict[str, Any]
    sorter: str
    title: str
    titleFormatter: str | CellFormatter | JSCode
    titleFormatterParams: dict[str, Any]
    width: str | int

class GroupSpec(TypedDict):
    columns: Sequence[ColumnSpec]
    title: str


def _convert_datetime_array_ignore_list(v):
    if isinstance(v, np.ndarray):
        return convert_datetime_array(v)
    return v

def _get_value_from_keys(d:dict, key1, key2, default=None):
    if key1 in d:
        return d[key1]
    if key2 in d:
        msg = f"The {key1} format should be preferred over the {key2}."
        warn(msg, DeprecationWarning)
        return d[key2]
    return default

class BaseTable(ReactiveData, Widget):

    aggregators = param.Dict(default={}, nested_refs=True, doc="""
        A dictionary mapping from index name to an aggregator to
        be used for hierarchical multi-indexes (valid aggregators
        include 'min', 'max', 'mean' and 'sum'). If separate
        aggregators for different columns are required the dictionary
        may be nested as `{index_name: {column_name: aggregator}}`""")

    editors = param.Dict(default={}, nested_refs=True, doc="""
        Bokeh CellEditor to use for a particular column
        (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, nested_refs=True, doc="""
        Bokeh CellFormatter to use for a particular column
        (overrides the default chosen based on the type).""")

    hierarchical = param.Boolean(default=False, constant=True, doc="""
        Whether to generate a hierarchical index.""")

    row_height = param.Integer(default=40, doc="""
        The height of each table row.""")

    selection = param.List(default=[], doc="""
        The currently selected rows of the table.""")

    show_index = param.Boolean(default=True, doc="""
        Whether to show the index column.""")

    sorters = param.List(default=[], doc="""
        A list of sorters to apply during pagination.""")

    text_align = param.ClassSelector(default={}, nested_refs=True, class_=(dict, str), doc="""
        A mapping from column name to alignment or a fixed column
        alignment, which should be one of 'left', 'center', 'right'.""")

    titles = param.Dict(default={}, nested_refs=True, doc="""
        A mapping from column name to a title to override the name with.""")

    widths = param.ClassSelector(default={}, nested_refs=True, class_=(dict, int), doc="""
        A mapping from column name to column width or a fixed column
        width.""")

    value = param.Parameter(default=None)

    _data_params: ClassVar[list[str]] = ['value']

    _manual_params: ClassVar[list[str]] = [
        'formatters', 'editors', 'widths', 'titles', 'value', 'show_index'
    ]

    _rename: ClassVar[Mapping[str, str | None]] = {
        'hierarchical': None, 'name': None, 'selection': None
    }

    __abstract = True

    def __init__(self, value=None, **params):
        self._renamed_cols = {}
        self._filters = []
        self._index_mapping = {}
        self._edited_indexes = []
        super().__init__(value=value, **params)
        self._internal_callbacks.extend([
            self.param.watch(self._setup_on_change, ['editors', 'formatters']),
            self.param._watch(self._reset_selection, ['value'], precedence=-1)
        ])
        self.param.trigger('editors')
        self.param.trigger('formatters')

    @param.depends('value', watch=True, on_init=True)
    def _compute_renamed_cols(self):
        if self.value is None:
            self._renamed_cols.clear()
            return
        self._renamed_cols = {
            ('_'.join(col) if isinstance(col, tuple) else str(col)) if str(col) != col else col: col for col in self._get_fields()
        }

    def _reset_selection(self, event):
        if 'selectable' in self.param and not self.selectable:
            return
        if event.type == 'triggered' and self._updating:
            return
        if self._indexes_changed(event.old, event.new):
            selection = []
            for sel in self.selection:
                idx = event.old.index[sel]
                try:
                    new = event.new.index.get_loc(idx)
                    selection.append(new)
                except KeyError:
                    pass
            self.selection = selection

    def _indexes_changed(self, old, new):
        """
        Comparator that checks whether DataFrame indexes have changed.

        If indexes and length are unchanged we assume we do not
        have to reset various settings including expanded rows,
        scroll position, pagination etc.
        """
        if type(old) is not type(new) or isinstance(new, dict) or len(old) != len(new):
            return True
        return (old.index != new.index).any()

    @property
    def _length(self):
        return len(self._processed)

    def _validate(self, *events: param.parameterized.Event):
        if self.value is None:
            return
        cols = self.value.columns
        if len(cols) != len(cols.drop_duplicates()):
            raise ValueError('Cannot display a pandas.DataFrame with '
                             'duplicate column names.')

    def _get_fields(self) -> list[str]:
        indexes = self.indexes
        col_names = [] if self.value is None else list(self.value.columns)
        if not self.hierarchical or len(indexes) == 1:
            col_names = indexes + col_names
        else:
            col_names = indexes[-1:] + col_names
        return col_names

    def _get_columns(self) -> list[TableColumn]:
        if self.value is None:
            return []

        indexes = self.indexes
        fields = self._get_fields()
        df = self.value.reset_index() if len(indexes) > 1 else self.value
        return self._get_column_definitions(fields, df)

    def _get_column_definitions(self, col_names: list[str], df: pd.DataFrame) -> list[TableColumn]:
        import pandas as pd
        indexes = self.indexes
        columns = []
        for col in col_names:
            if col in df.columns:
                data: pd.Series | pd.Index = df[col]
            elif col in self.indexes:
                if len(self.indexes) == 1:
                    data = df.index
                elif df.index.nlevels == 1:
                    # Look in the column with the tuple format
                    index_col = tuple([col[: -(df.columns.nlevels - 1)]] + [""] * (df.columns.nlevels - 1))
                    data = df[index_col]
                else:
                    data = df.index.get_level_values(self.indexes.index(col))

            if isinstance(data, pd.DataFrame):
                raise ValueError("DataFrame contains duplicate column names.")

            col_kwargs: dict[str, Any] = {}
            kind = data.dtype.kind
            editor: CellEditor
            formatter: CellFormatter | None = self.formatters.get(col)
            if kind == 'i':
                editor = IntEditor()
            elif kind == 'b':
                editor = CheckboxEditor()
            elif kind == 'f':
                editor = NumberEditor()
            elif isdatetime(data) or kind == 'M':
                editor = DateEditor()
            else:
                editor = StringEditor()

            if col in self.editors and not isinstance(self.editors[col], (dict, str, JSCode)):
                editor = self.editors[col]
                if isinstance(editor, CellEditor):
                    editor = clone_model(editor)

            if col in indexes or editor is None:
                editor = CellEditor()

            if formatter is None or isinstance(formatter, (dict, str, JSCode)):
                if kind == 'i':
                    formatter = NumberFormatter(text_align='right')
                elif kind == 'b':
                    formatter = StringFormatter(text_align='center')
                elif kind == 'f':
                    formatter = NumberFormatter(format='0,0.0[00000]', text_align='right')
                elif isdatetime(data) or kind == 'M':
                    if len(data) and isinstance(data.values[0], dt.date):
                        date_format = '%Y-%m-%d'
                    else:
                        date_format = '%Y-%m-%d %H:%M:%S'
                    formatter = DateFormatter(format=date_format, text_align='right')
                else:
                    formatter = StringFormatter(null_format='')

                default_text_align = True
            else:
                if isinstance(formatter, CellFormatter):
                    formatter = clone_model(formatter)
                if formatter and hasattr(formatter, 'text_align'):
                    default_text_align = type(formatter).text_align.class_default(formatter) == formatter.text_align
                else:
                    default_text_align = True

            if not formatter or not hasattr(formatter, 'text_align'):
                pass
            elif isinstance(self.text_align, str):
                formatter.text_align = self.text_align
                if not default_text_align:
                    msg = f"The 'text_align' in Tabulator.formatters[{col!r}] is overridden by Tabulator.text_align"
                    warn(msg, RuntimeWarning)
            elif col in self.text_align:
                formatter.text_align = self.text_align[col]
                if not default_text_align:
                    msg = f"The 'text_align' in Tabulator.formatters[{col!r}] is overridden by Tabulator.text_align[{col!r}]"
                    warn(msg, RuntimeWarning)
            elif col in self.indexes:
                formatter.text_align = 'left'

            if isinstance(self.widths, int):
                col_kwargs['width'] = self.widths
            elif str(col) in self.widths and isinstance(self.widths.get(str(col)), int):
                col_kwargs['width'] = self.widths.get(str(col))
            else:
                col_kwargs['width'] = 0

            col_name = '_'.join(col) if isinstance(col, tuple) else col
            title = self.titles.get(col, str(col_name))
            if col in indexes and len(indexes) > 1 and self.hierarchical:
                title = 'Index: {}'.format(' | '.join(indexes))
            elif col in self.indexes and col.startswith('level_'):
                title = ''

            if formatter:
                col_kwargs["formatter"] = formatter

            column = TableColumn(field=str(col_name), title=title,
                                 editor=editor, **col_kwargs)
            columns.append(column)
        return columns

    def _setup_on_change(self, *events: param.parameterized.Event):
        for event in events:
            self._process_on_change(event)

    def _process_on_change(self, event: param.parameterized.Event):
        old, new = event.old, event.new
        for model in (old if isinstance(old, dict) else {}).values():
            if not isinstance(model, (CellEditor, CellFormatter)):
                continue
            change_fn = self._editor_change if isinstance(model, CellEditor) else self._formatter_change
            for prop in (model.properties() - Model.properties()):
                try:
                    model.remove_on_change(prop, change_fn)
                except ValueError:
                    pass
        for model in (new if isinstance(new, dict) else {}).values():
            if not isinstance(model, (CellEditor, CellFormatter)):
                continue
            change_fn = self._editor_change if isinstance(model, CellEditor) else self._formatter_change
            for prop in (model.properties() - Model.properties()):
                model.on_change(prop, change_fn)

    def _editor_change(self, attr: str, new: Any, old: Any):
        self.param.trigger('editors')

    def _formatter_change(self, attr: str, new: Any, old: Any):
        self.param.trigger('formatters')

    def _update_index_mapping(self):
        if self._processed is None or isinstance(self._processed, list) and not self._processed:
            self._index_mapping = {}
            return
        self._index_mapping = {
            i: index
            for i, index in enumerate(self._processed.index)
        }

    @updating
    def _update_cds(self, *events: param.parameterized.Event):
        self._processed, data = self._get_data()
        self._update_index_mapping()
        self._data = {k: _convert_datetime_array_ignore_list(v) for k, v in data.items()}
        named_events = {e.name: e for e in events}
        msg = {'data': self._data}
        for ref, (m, _) in self._models.copy().items():
            self._apply_update(named_events, msg, m.source, ref)

    def _process_param_change(self, params):
        if 'disabled' in params:
            params['editable'] = not params.pop('disabled') and len(self.indexes) <= 1
        params = super()._process_param_change(params)
        return params

    def _get_properties(self, doc: Document | None = None) -> dict[str, Any]:
        properties = super()._get_properties(doc)
        properties['columns'] = self._get_columns()
        properties['source']  = cds = ColumnDataSource(data=self._data)
        cds.selected.indices = self.selection
        return properties

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        properties = self._get_properties(doc)
        model = cast(Model, self._widget_type(**properties))  # type: ignore[misc]
        root = root or model
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
        self, events: tuple[param.parameterized.Event, ...], model: Model, doc: Document,
        root: Model, parent: Model | None, comm: Comm | None
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

    def _sort_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.sorters:
            return df
        fields = [self._renamed_cols.get(s['field'], s['field']) for s in self.sorters]
        ascending = [s['dir'] == 'asc' for s in self.sorters]

        # Making a copy of the DataFrame because it could be a view of the original
        # dataframe. There could be a better place to do this.
        df = df.copy()
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
                return col.fillna("").str.lower()
            except Exception:
                return col

        df_sorted = df.sort_values(fields, ascending=ascending, kind='mergesort',
                                  key=tabulator_sorter)

        # Revert temporary changes to DataFrames
        if rename:
            df_sorted.index.name = None
        df_sorted.drop(columns=['_index_'], inplace=True)
        return df_sorted

    def _filter_dataframe(
        self,
        df: pd.DataFrame,
        header_filters: bool = True,
        internal_filters: bool = True
    ) -> pd.DataFrame:
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
        for col_name, filt in (self._filters if internal_filters else []):
            if col_name is not None and col_name not in df.columns:
                continue
            if isinstance(filt, (FunctionType, MethodType, partial)):
                res = filt(df)
                if type(res) is type(df): #function returned filtered dataframe
                    df = res
                else: #assume boolean mask
                    filters.append(res)
                continue
            if isinstance(filt, param.Parameter):
                val = getattr(filt.owner, filt.name)
            else:
                val = filt
            column = df[col_name]
            if val is None:
                continue
            elif np.isscalar(val):
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

        if header_filters:
            filters.extend(self._get_header_filters(df))

        if filters:
            mask = filters[0]
            for f in filters:
                mask &= f
            if self._edited_indexes:
                edited_mask = (df.index.isin(self._edited_indexes))
                mask = mask | edited_mask
            df = df[mask]
        return df

    def _get_header_filters(self, df: pd.DataFrame) -> list[pd.Series | np.ndarray]:
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
            else:
                continue

            # Sometimes Tabulator will provide a zero/single element list
            if isinstance(val, list):
                if len(val) == 1:
                    val = val[0]
                elif not val:
                    continue

            if col.dtype.kind != 'O':
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
                if not isinstance(val, (list, np.ndarray)): val = [val]
                filters.append(col.isin(val))
            elif op == 'like':
                filters.append(col.str.contains(val, case=False, regex=False))
            elif op == 'starts':
                filters.append(col.str.startsWith(val))
            elif op == 'ends':
                filters.append(col.str.endsWith(val))
            elif op == 'keywords':
                match_all = filt_def.get(col_name, {}).get('matchAll', False)
                sep = filt_def.get(col_name, {}).get('separator', ' ')
                matches = val.split(sep)
                if match_all:
                    for match in matches:
                        filters.append(col.str.contains(match, case=False, regex=False))
                else:
                    filt = col.str.contains(matches[0], case=False, regex=False)
                    for match in matches[1:]:
                        filt |= col.str.contains(match, case=False, regex=False)
                    filters.append(filt)
            elif op == 'regex':
                raise ValueError("Regex filtering not supported.")
            else:
                raise ValueError(f"Filter type {op!r} not recognized.")
        return filters

    def add_filter(self, filter: Any, column: str | None = None):
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

        Parameters
        ----------
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
        elif isinstance(filter, (FunctionType, MethodType, partial)):
            deps = list(filter._dinfo['kw'].values()) if hasattr(filter, '_dinfo') else []
        else:
            filter = transform_reference(filter)
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

    def _process_column(self, values: TDataColumn, col: str, df: pd.DataFrame | None = None):
        if not isinstance(values, (list, np.ndarray)):
            return [str(v) for v in values]
        if isinstance(values, np.ndarray):
            if values.dtype.kind == "b":
                # Workaround for https://github.com/bokeh/bokeh/issues/12776
                return values.tolist()
            import pandas as pd
            if df is not None and col in df.columns and isinstance(df[col].dtype, pd.StringDtype):
                values[df[col].isna()] = None
        return values

    def _get_data(self) -> tuple[pd.DataFrame, DataDict]:
        return self._process_df_and_convert_to_cds(self.value)

    def _process_df_and_convert_to_cds(self, df: pd.DataFrame) -> tuple[pd.DataFrame, DataDict]:
        # By default we potentially have two distinct views of the data
        # locally we hold the fully filtered data, i.e. with header filters
        # applied but since header filters are applied on the frontend
        # we send the unfiltered data

        import pandas as pd

        # Ensure NaT serialization is enabled
        try:
            Serializer.register(pd.NaT, lambda _, __: None)  # type: ignore
        except AssertionError:
            pass

        df = self._filter_dataframe(df, header_filters=False)
        if df is None:
            return [], {}
        indexes: list[Any]
        if isinstance(self.value.index, pd.MultiIndex):
            indexes = [
                f'level_{i}' if n is None else n
                for i, n in enumerate(df.index.names)
            ]
        else:
            default_index = ('level_0' if 'index' in df.columns else 'index')
            indexes = [df.index.name or default_index]
        if df.columns.nlevels > 1 and len(indexes) > 1:
            indexes = [i + "_" * (df.columns.nlevels - 1) for i in indexes]
        data = ColumnDataSource.from_df(df.reset_index() if len(indexes) > 1 else df)
        if not self.show_index and len(indexes) > 1:
            data = {k: v for k, v in data.items() if k not in indexes}
        return df, {k if isinstance(k, str) else str(k): self._process_column(v, k, df) for k, v in data.items()}

    def _update_column(self, column: str, array: TDataColumn):
        import pandas as pd

        self.value[column] = array
        if self._processed is not None and self.value is not self._processed:
            with pd.option_context('mode.chained_assignment', None):
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
            indexes = [
                f'level_{i}' if n is None else n
                for i, n in enumerate(self.value.index.names)
            ]
            if self.value.columns.nlevels > 1:
                indexes = [i + "_" * (self.value.columns.nlevels - 1) for i in indexes]
            return indexes
        default_index = ('level_0' if 'index' in self.value.columns else 'index')
        return [self.value.index.name or default_index]

    def stream(self, stream_value, rollover=None, reset_index=True):
        """
        Streams (appends) the `stream_value` provided to the existing
        value in an efficient manner.

        Parameters
        ----------
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
            if self.value.empty:
                combined = pd.DataFrame(
                    stream_value, columns=self.value.columns
                ).astype(self.value.dtypes)
            else:
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

        Parameters
        ----------
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
                "is not supported. Please provide a DataFrame."
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
            patches = {}
            for k, v in patch_value.items():
                values = []
                for (patch_ind, value) in v:
                    data_ind = patch_ind
                    if isinstance(patch_ind, slice):
                        data_ind = range(patch_ind.start, patch_ind.stop, patch_ind.step or 1)
                    if as_index:
                        if not isinstance(data_ind, range):
                            patch_ind = self.value.index.get_loc(patch_ind)
                            if not isinstance(patch_ind, int):
                                raise ValueError(
                                    'Patching a table with duplicate index values is not supported. '
                                    f'Found this duplicate index: {data_ind!r}'
                                )
                        self.value.loc[data_ind, k] = value
                    else:
                        self.value.iloc[data_ind, columns.index(k)] = value
                    if isinstance(value, pd.Timestamp):
                        value = datetime_as_utctimestamp(value)
                    elif value is pd.NaT:
                        value = np.nan
                    values.append((patch_ind, value))
                patches[k] = values
            self._patch(patches)
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
        if self.value is None:
            return
        df = self._processed
        return self._sort_df(df)

    @property
    def selected_dataframe(self):
        """
        Returns a DataFrame of the currently selected rows.
        """
        if self.value is None:
            return
        elif not self.selection:
            return self.current_view.iloc[:0]
        df = self.value.iloc[self.selection]
        return self._filter_dataframe(df)


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

    autosize_mode = param.Selector(default='force_fit', objects=[
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

    _manual_params: ClassVar[list[str]] = BaseTable._manual_params + ['aggregators']

    _aggregators = {
        'sum': SumAggregator, 'max': MaxAggregator,
        'min': MinAggregator, 'mean': AvgAggregator
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'hierarchical': None}

    _rename: ClassVar[Mapping[str, str | None]] = {
        'selection': None, 'sorters': None, 'text_align': None
    }

    @property
    def _widget_type(self) -> type[Model] | None:  # type: ignore[override]
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

    def _get_properties(self, doc: Document | None = None) -> dict[str, Any]:
        properties = super()._get_properties(doc)
        if self.hierarchical:
            properties['target'] = ColumnDataSource(data=dict(row_indices=[], labels=[]))
            properties['grouping'] = self._get_groupings()
        return properties

    def _update_aggregators(self, model):
        for g in model.grouping:
            group = self._renamed_cols.get(g.getter, g.getter)
            index = self.indexes[self.indexes.index(group)+1]
            g.aggregators = self._get_aggregators(index)


class _ListValidateWithCallable(param.List):

    __slots__ = ['callable']

    def __init__(self, **params):
        self.callable = params.pop("callable", None)
        super().__init__(**params)

    def _validate(self, val):
        super()._validate(val)
        self._validate_callable(val)

    def _validate_callable(self, val):
        if self.callable is not None:
            selectable = self.callable()
            if selectable and val:
                if set(val) - set(selectable):
                    raise ValueError(
                        "Values in 'selection' must not have values "
                        "which are not available with 'selectable_rows'."
                  )


class Tabulator(BaseTable):
    """
    The `Tabulator` widget wraps the [Tabulator js](http://tabulator.info/)
    table to provide a full-featured, very powerful interactive table.

    Reference: https://panel.holoviz.org/reference/widgets/Tabulator.html

    :Example:

    >>> Tabulator(df, theme='site', pagination='remote', page_size=25)
    """

    buttons = param.Dict(default={}, nested_refs=True, doc="""
        Dictionary mapping from column name to a HTML element
        to use as the button icon.""")

    container_popup = param.Boolean(default=True, doc="""
        If True, popups will appear within the table container, otherwise
        popups will be appended to the body element of the DOM.""")

    expanded = param.List(default=[], nested_refs=True, doc="""
        List of expanded rows, only applicable if a row_content function
        has been defined.""")

    embed_content = param.Boolean(default=False, doc="""
        Whether to embed the row_content or render it dynamically
        when a row is expanded.""")

    filters = param.List(default=[], doc="""
        List of client-side filters declared as dictionaries containing
        'field', 'type' and 'value' keys.""")

    frozen_columns = param.ClassSelector(class_=(list, dict), default=[], nested_refs=True, doc="""
        One of:
        - List indicating the columns to freeze. The column(s) may be
        selected by name or index.
        - Dict indicating columns to freeze as keys and their freeze location
        as values, freeze location is either 'right' or 'left'.""")

    frozen_rows = param.List(default=[], nested_refs=True, doc="""
        List indicating the rows to freeze. If set, the
        first N rows will be frozen, which prevents them from scrolling
        out of frame; if set to a negative value the last N rows will be
        frozen.""")

    groups = param.Dict(default={}, nested_refs=True, doc="""
        Dictionary mapping defining the groups.""")

    groupby = param.List(default=[], nested_refs=True, doc="""
        Groups rows in the table by one or more columns.""")

    header_align = param.ClassSelector(default={}, nested_refs=True, class_=(dict, str), doc="""
        A mapping from column name to alignment or a fixed column
        alignment, which should be one of 'left', 'center', 'right'.""")

    header_filters = param.ClassSelector(class_=(bool, dict), nested_refs=True, doc="""
        Whether to enable filters in the header or dictionary
        configuring filters for each column.""")

    header_tooltips = param.Dict(default={}, doc="""
        Dictionary mapping from column name to a tooltip to show when
        hovering over the column header.""")

    hidden_columns = param.List(default=[], nested_refs=True, doc="""
        List of columns to hide.""")

    layout = param.Selector(default='fit_data_table', objects=[
        'fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table',
        'fit_columns'], doc="""
        Describes the column layout mode with one of the following options
        'fit_columns', 'fit_data', 'fit_data_stretch', 'fit_data_fill',
        'fit_data_table'.""")

    initial_page_size = param.Integer(default=20, bounds=(1, None), doc="""
        Initial page size if page_size is None and therefore automatically set.""")

    pagination = param.Selector(default=None, allow_None=True,
                                      objects=['local', 'remote'], doc="""
        Defines the pagination mode of the Tabulator.

          - None
              No pagination is applied, all rows are rendered.
          - 'local' (client-side)
              Pagination is applied locally, i.e. the entire DataFrame
              is loaded and then paginated.
          - 'remote' (server-side)
              Pagination is applied remotely, i.e. only the current page
              is loaded from the server.""")

    page = param.Integer(default=1, doc="""
        Currently selected page (indexed starting at 1), if pagination is enabled.""")

    page_size = param.Integer(default=None, bounds=(1, None), doc="""
        Number of rows to render per page, if pagination is enabled.""")

    row_content = param.Callable(doc="""
        A function which is given the DataFrame row and should return
        a Panel object to render as additional detail below the row.""")

    row_height = param.Integer(default=30, doc="""
        The height of each table row.""")

    selection: list[int] = _ListValidateWithCallable(default=[], doc="""
        The currently selected rows of the table. It validates
        its values against 'selectable_rows' if used.""")

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
              Same as 'checkbox' but header does not allow select/deselect all
          - 'toggle'
              Selection toggles when clicked
          - int
              The maximum number of selectable rows.
        """)

    selectable_rows = param.Callable(default=None, doc="""
        A function which given a DataFrame should return a list of
        rows by integer index, which are selectable.""")

    sortable = param.ClassSelector(default=True, class_=(bool, dict), doc="""
        Whether the columns in the table should be sortable.
        Can either be specified as a simple boolean toggling the behavior
        on and off or as a dictionary specifying the option per column.""")

    theme = param.Selector(
        default="simple", objects=[
            'default', 'site', 'simple', 'midnight', 'modern', 'bootstrap',
            'bootstrap4', 'materialize', 'bulma', 'semantic-ui', 'fast',
            'bootstrap5'
        ], doc="""
        Tabulator CSS theme to apply to table.""")

    theme_classes = param.List(default=[], nested_refs=True, item_type=str, doc="""
       List of extra CSS classes to apply to the Tabulator element
       to customize the theme.""")

    title_formatters = param.Dict(default={}, nested_refs=True, doc="""
       Tabulator formatter specification to use for a particular column
       header title.""")

    _data_params: ClassVar[list[str]] = [
        'value', 'page', 'page_size', 'pagination', 'sorters', 'filters'
    ]

    _config_params: ClassVar[list[str]] = [
        'frozen_columns', 'groups', 'selectable', 'hierarchical', 'sortable'
    ]

    _content_params: ClassVar[list[str]] = _data_params + ['expanded', 'row_content', 'embed_content']

    _manual_params: ClassVar[list[str]] = BaseTable._manual_params + _config_params

    _priority_changes: ClassVar[list[str]] = ['data', 'filters']

    _rename: ClassVar[Mapping[str, str | None]] = {
        'selection': None, 'row_content': None, 'row_height': None,
        'text_align': None, 'header_align': None, 'header_filters': None,
        'header_tooltips': None, 'styles': 'cell_styles',
        'title_formatters': None, 'sortable': None, 'initial_page_size': None
    }

    # Determines the maximum size limits beyond which (local, remote)
    # pagination is enabled
    _MAX_ROW_LIMITS: ClassVar[tuple[int, int]] = (200, 10000)

    _stylesheets = [CSS_URLS['font-awesome']]

    def __init__(self, value=None, **params):
        import pandas.io.formats.style
        click_handler = params.pop('on_click', None)
        edit_handler = params.pop('on_edit', None)
        if isinstance(value, pandas.io.formats.style.Styler):
            style = value
            value = value.data
        else:
            style = None
        configuration = params.pop('configuration', {})
        self.style = None
        self._computed_styler = None
        self._child_panels = {}
        self._indexed_children = {}
        self._explicit_pagination = 'pagination' in params
        self._on_edit_callbacks = []
        self._on_click_callbacks = {}
        self._old_value = None
        super().__init__(value=value, **params)
        self._configuration = configuration
        self.param.watch(self._update_children, self._content_params)
        self.param.watch(self._clear_selection_remote_pagination, 'value')
        if click_handler:
            self.on_click(click_handler)
        if edit_handler:
            self.on_edit(edit_handler)
        if style is not None:
            self.style._todo = style._todo
        self.param.selection.callable = self._get_selectable

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

    def _process_events(self, events: dict[str, Any]) -> None:
        if 'expanded' in events:
            self._update_expanded(events.pop('expanded'))
        if events.get('page_size') == 0:  # page_size can't be 0
            events.pop('page_size')
        return super()._process_events(events)

    def _process_event(self, event) -> None:
        if event.event_name == 'selection-change':
            if self.pagination == 'remote':
                self._update_selection(event)
            return

        event_col = self._renamed_cols.get(event.column, event.column)
        if self.pagination == 'remote':
            nrows = self.page_size or self.initial_page_size
            event.row = event.row+(self.page-1)*nrows

        idx = self._index_mapping.get(event.row, event.row)
        iloc = self.value.index.get_loc(idx)
        self._validate_iloc(idx, iloc)
        event.row = iloc
        if event_col not in self.buttons:
            if event_col in self.value.columns:
                event.value = self.value[event_col].iloc[event.row]
            else:
                event.value = self.value.index[event.row]

        # Set the old attribute on a table edit event
        if event.event_name == 'table-edit':
            if event.pre:
                import pandas as pd
                filter_df = pd.DataFrame({event.column: [event.value]})
                filters = self._get_header_filters(filter_df)
                # Check if edited cell was filtered
                if filters and filters[0].any():
                    self._edited_indexes.append(idx)
            else:
                if self._old_value is not None:
                    event.old = self._old_value[event_col].iloc[event.row]
                for cb in self._on_edit_callbacks:
                    state.execute(partial(cb, event), schedule=False)
                self._update_style()
        else:
            for cb in self._on_click_callbacks.get(None, []):
                state.execute(partial(cb, event), schedule=False)
            for cb in self._on_click_callbacks.get(event_col, []):
                state.execute(partial(cb, event), schedule=False)

    def _get_theme(self, theme, resources=None):
        from ..models.tabulator import _TABULATOR_THEMES_MAPPING, THEME_PATH
        theme_ = _TABULATOR_THEMES_MAPPING.get(theme, theme)
        fname = 'tabulator' if theme_ == 'default' else f'tabulator_{theme_}'
        theme_url = f'{CDN_DIST}bundled/datatabulator/{THEME_PATH}{fname}.min.css'
        if self._widget_type is not None:
            self._widget_type.__css_raw__ = [theme_url]
        return theme_url

    def _update_columns(self, event, model):
        if event.name not in self._config_params:
            super()._update_columns(event, model)
            if (event.name in ('editors', 'formatters', 'sortable') and
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
        # comparison and update the data held by the backend.

        # It also makes a copy of the value dataframe, to use it to obtain
        # the old value in a table-edit event.
        self._old_value = self.value.copy()

        import pandas as pd
        df = pd.DataFrame(data)
        filters = self._get_header_filters(df) if self.pagination == 'remote' else []
        if filters:
            mask = filters[0]
            for f in filters:
                mask &= f
            if self._edited_indexes:
                edited_mask = (df[self.value.index.name or 'index'].isin(self._edited_indexes))
                mask = mask | edited_mask
            df = df[mask]
        data = {
            col: df[col].values for col in df.columns
        }
        return super()._process_data(data)

    def _get_data(self):
        if self.pagination != 'remote' or self.value is None:
            return super()._get_data()

        # If data is paginated the current view on the frontend
        # and locally are identical and both paginated
        import pandas as pd
        df = self._filter_dataframe(self.value)
        df = self._sort_df(df)
        nrows = self.page_size or self.initial_page_size
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
        return df, {k if isinstance(k, str) else str(k): self._process_column(v, k, page_df) for k, v in data}

    def _get_style_data(self, recompute=True):
        if self.value is None or self.style is None or self.value.empty:
            return {}
        df = self._processed
        if len(self.indexes) > 1:
            df = df.reset_index()
        if recompute:
            try:
                self._computed_styler = styler = df.style
            except Exception:
                self._computed_styler = None
                return {}
            if styler is None:
                return {}
            styler._todo = styler_update(self.style, df)
            try:
                styler._compute()
            except Exception:
                styler._todo = []
        else:
            styler = self._computed_styler
        if styler is None:
            return {}

        # Compute offsets (not that multi-indexes are reset so don't require an offset)
        offset = 1 + int(len(self.indexes) == 1)  + int(self.selectable in ('checkbox', 'checkbox-single')) + int(bool(self.row_content))

        if self.pagination == 'remote':
            page_size = self.page_size or self.initial_page_size
            start = (self.page - 1) * page_size
            end = start + page_size

        # Map column indexes in the data to indexes after frozen_columns are applied
        column_mapper = {}
        frozen_cols = self.frozen_columns
        column_mapper = {}
        if isinstance(frozen_cols, list):
            if len(self.indexes) > 1:
                nfrozen = len(frozen_cols)
            else:
                nfrozen = len([col for col in frozen_cols if col not in self.indexes])
            non_frozen = [col for col in df.columns if col not in frozen_cols]
            for i, col in enumerate(df.columns):
                if col in frozen_cols:
                    column_mapper[i] = frozen_cols.index(col) - len(self.indexes)
                else:
                    column_mapper[i] = nfrozen + non_frozen.index(col)
        elif isinstance(frozen_cols, dict):
            left_cols = [col for col, p in frozen_cols.items() if p in 'left']
            right_cols = [col for col, p in frozen_cols.items() if p in 'right']
            non_frozen = [col for col in df.columns if col not in frozen_cols]
            for i, col in enumerate(df.columns):
                if col in left_cols:
                    column_mapper[i] = left_cols.index(col) - len(self.indexes)
                elif col in right_cols:
                    column_mapper[i] = len(left_cols) + len(non_frozen) + right_cols.index(col)
                else:
                    column_mapper[i] = len(left_cols) + non_frozen.index(col)

        styles = {}
        for (r, c), s in styler.ctx.items():
            if self.pagination == 'remote':
                if (r < start or r >= end):
                    continue
                else:
                    r -= start
            if r not in styles:
                styles[int(r)] = {}
            c = column_mapper.get(int(c), int(c))
            styles[int(r)][offset+c] = s
        return {'id': uuid.uuid4().hex, 'data': styles}

    def _get_selectable(self):
        if self.value is None or self.selectable_rows is None:
            return None
        df = self._processed
        if self.pagination == 'remote':
            nrows = self.page_size or self.initial_page_size
            start = (self.page-1)*nrows
            df = df.iloc[start:(start+nrows)]
        return self.selectable_rows(df)

    def _update_style(self, recompute=True):
        styles = self._get_style_data(recompute)
        msg = {'cell_styles': styles}
        for ref, (m, _) in self._models.copy().items():
            self._apply_update([], msg, m, ref)

    def _get_children(self):
        if self.row_content is None or self.value is None:
            return {}, [], []
        from ..pane import panel
        df = self._processed
        if self.pagination == 'remote':
            nrows = self.page_size or self.initial_page_size
            start = (self.page-1)*nrows
            df = df.iloc[start:(start+nrows)]
        indexed_children, children = {}, {}
        if self.embed_content:
            indexes = list(range(len(df)))
            mapped = self._map_indexes(indexes)
            expanded = [
                i for i, m in zip(indexes, mapped)
                if m in self.expanded
            ]
            for i in indexes:
                idx = df.index[i]
                if idx in self._indexed_children:
                    child = self._indexed_children[idx]
                else:
                    child = panel(self.row_content(df.iloc[i]))
                indexed_children[idx] = children[i] = child
        else:
            expanded = []
            for i in self.expanded:
                idx = self.value.index[i]
                if idx in self._indexed_children:
                    child = self._indexed_children[idx]
                else:
                    child = panel(self.row_content(self.value.iloc[i]))
                try:
                    loc = df.index.get_loc(idx)
                except KeyError:
                    continue
                expanded.append(loc)
                indexed_children[idx] = children[loc] = child
        removed = [
            child for idx, child in self._indexed_children.items()
            if idx not in indexed_children
        ]
        self._indexed_children = indexed_children
        return children, removed, expanded

    def _get_model_children(self, doc, root, parent, comm=None):
        ref = root.ref['id']
        models = {}
        for i, p in self._child_panels.items():
            if ref in p._models:
                model = p._models[ref][0]
            else:
                model = p._get_model(doc, root, parent, comm)
            model.margin = (0, 0, 0, 0)
            models[i] = model
        return models

    def _update_children(self, *events):
        page_event = all(e.name in ('page', 'page_size', 'pagination', 'sorters') for e in events)
        if (page_event and self.pagination != 'remote'):
            return
        for event in events:
            if event.name == 'value' and self._indexes_changed(event.old, event.new):
                self.expanded = []
                self._indexed_children.clear()
                return
            elif event.name == 'row_content':
                self._indexed_children.clear()
        self._child_panels, removed, expanded = self._get_children()
        for ref, (m, _) in self._models.copy().items():
            msg = {'expanded': expanded}
            if not self.embed_content or any(e.name == 'row_content' for e in events):
                root, doc, comm = state._views[ref][1:]
                for child_panel in removed:
                    child_panel._cleanup(root)
                msg['children'] = self._get_model_children(doc, root, m, comm)
            self._apply_update([], msg, m, ref)

    @updating
    def _stream(self, stream, rollover=None, follow=True):
        if self.pagination == 'remote':
            length = self._length
            nrows = self.page_size or self.initial_page_size
            max_page = max(length//nrows + bool(length%nrows), 1)
            if self.page != max_page and not follow:
                return
            self._processed, _ = self._get_data()
            return
        super()._stream(stream, rollover)
        self._update_style()
        self._update_selectable()
        self._update_index_mapping()

    def stream(self, stream_value, rollover=None, reset_index=True, follow=True):
        for ref, (model, _) in self._models.copy().items():
            self._apply_update([], {'follow': follow}, model, ref)
        super().stream(stream_value, rollover, reset_index)
        if follow and self.pagination:
            self._update_max_page()
        if follow and self.pagination:
            length = self._length
            nrows = self.page_size or self.initial_page_size
            self.page = max(length//nrows + bool(length%nrows), 1)

    @updating
    def _patch(self, patch):
        if self.filters or self._filters or self.sorters:
            self._updating = False
            self._update_cds()
            return
        if self.pagination == 'remote':
            nrows = self.page_size or self.initial_page_size
            start = (self.page - 1) * nrows
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
        if any(event.name == 'filters' for event in events):
            self._edited_indexes = []
        page_events = ('page', 'page_size', 'sorters')
        if self._updating:
            return
        elif events and all(e.name in page_events for e in events) and self.pagination == 'local':
            return
        elif events and all(e.name in page_events for e in events) and not self.pagination:
            self._processed, _ = self._get_data()
            return
        elif self.pagination == 'remote':
            self._processed = None
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
        for ref, (model, _) in self._models.copy().items():
            self._apply_update([], {'selectable_rows': selectable}, model, ref)

    @param.depends('page_size', watch=True)
    def _update_max_page(self):
        length = self._length
        nrows = self.page_size or self.initial_page_size
        max_page = max(length//nrows + bool(length%nrows), 1)
        self.param.page.bounds = (1, max_page)
        for ref, (model, _) in self._models.copy().items():
            self._apply_update([], {'max_page': max_page}, model, ref)

    def _clear_selection_remote_pagination(self, event):
        if not self._updating and self.selection and event.new is not event.old and self.pagination == 'remote':
            self.selection = []

    def _update_selected(self, *events: param.parameterized.Event, indices=None):
        kwargs = {}
        if self.value is not None:
            # Compute integer indexes of the selected rows
            # on the displayed page
            index = self.value.iloc[self.selection].index
            indices = []
            for ind in index.values:
                try:
                    iloc = self._processed.index.get_loc(ind)
                    self._validate_iloc(ind, iloc)
                    indices.append((ind, iloc))
                except KeyError:
                    continue
            if self.pagination == 'remote':
                nrows = self.page_size or self.initial_page_size
                start = (self.page - 1) * nrows
                end = start+nrows
                p_range = self._processed.index[start:end]
                indices = [iloc - start for ind, iloc in indices
                           if ind in p_range]
            else:
                indices = [iloc for _, iloc in indices]
            kwargs['indices'] = indices
        super()._update_selected(*events, **kwargs)

    def _update_column(self, column: str, array: TDataColumn) -> None:
        import pandas as pd

        if self.pagination != 'remote':
            index = self._processed.index.values
            self.value.loc[index, column] = array
            with pd.option_context('mode.chained_assignment', None):
                self._processed[column] = array
            return
        nrows = self.page_size or self.initial_page_size
        start = (self.page - 1) * nrows
        end = start+nrows
        index = self._processed.iloc[start:end].index.values
        self.value.loc[index, column] = array

        with pd.option_context('mode.chained_assignment', None):
            self._processed.loc[index, column] = array

    def _map_indexes(self, indexes: list[int], existing: list[int] = [], add: bool = True) -> list[int]:
        if self.pagination == 'remote':
            nrows = self.page_size or self.initial_page_size
            start = (self.page-1)*nrows
        else:
            start = 0
        ilocs = list(existing)
        index = self._processed.iloc[[start+ind for ind in indexes]].index
        for v in index.values:
            try:
                iloc = self.value.index.get_loc(v)
                self._validate_iloc(v, iloc)
            except KeyError:
                continue
            if add:
                ilocs.append(iloc)
            elif iloc in ilocs:
                ilocs.remove(iloc)
        return list(dict.fromkeys(ilocs))

    def _update_expanded(self, expanded):
        self.expanded = self._map_indexes(expanded)

    def _update_selection(self, indices: list[int] | SelectionEvent):
        if isinstance(indices, list):
            selected = True
            ilocs: list[int] = []
            inds = indices
        else:
            selected = indices.selected
            ilocs = [] if indices.flush else self.selection.copy()
            inds = indices.indices

        ilocs = self._map_indexes(inds, ilocs, add=selected)
        if isinstance(self.selectable, int) and not isinstance(self.selectable, bool):
            ilocs = ilocs[len(ilocs) - self.selectable:]
        self.selection = ilocs  # type: ignore

    def _get_properties(self, doc: Document | None = None) -> dict[str, Any]:
        properties = super()._get_properties(doc)
        properties['configuration'] = self._get_configuration(properties['columns'])
        properties['cell_styles'] = self._get_style_data()
        properties['indexes'] = self.indexes
        if self.pagination:
            length = self._length
            page_size = self.page_size or self.initial_page_size
            properties['max_page'] = max(length//page_size + bool(length % page_size), 1)
        if isinstance(self.selectable, str) and self.selectable.startswith('checkbox'):
            properties['select_mode'] = 'checkbox'
        else:
            properties['select_mode'] = self.selectable
        return properties

    def _process_param_change(self, params):
        if 'theme' in params or 'stylesheets' in params:
            theme_url = self._get_theme(params.pop('theme', self.theme))
            if theme_url:
                params['stylesheets'] = params.get('stylesheets', self.stylesheets) + [
                    ImportedStyleSheet(url=theme_url)
                ]
        params = Reactive._process_param_change(self, params)
        if 'disabled' in params:
            params['editable'] = not params.pop('disabled') and len(self.indexes) <= 1
        if 'frozen_rows' in params:
            length = self._length
            params['frozen_rows'] = [
                length+r if r < 0 else r for r in params['frozen_rows']
            ]
        if 'hidden_columns' in params:
            import pandas as pd
            if not self.show_index and self.value is not None and not isinstance(self.value.index, pd.MultiIndex):
                params['hidden_columns'] = params['hidden_columns'] + [self.value.index.name or 'index']
        if 'selectable_rows' in params:
            params['selectable_rows'] = self._get_selectable()
        return params

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        Tabulator._widget_type = lazy_load(
            'panel.models.tabulator', 'DataTabulator', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        root = root or model
        self._child_panels, removed, expanded = self._get_children()
        model.expanded = expanded
        model.children = self._get_model_children(doc, root, parent, comm)
        self._link_props(model, ['page', 'sorters', 'expanded', 'filters', 'page_size'], doc, root, comm)
        self._register_events('cell-click', 'table-edit', 'selection-change', model=model, doc=doc, comm=comm)
        return model

    def _get_filter_spec(self, column: TableColumn) -> FilterSpec:
        fspec: FilterSpec = {}
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
                elif isdatetime(col) or col.dtype.kind == 'M':
                    fspec['headerFilter'] = False
                else:
                    fspec['headerFilter'] = True
            elif isinstance(column.editor, DateEditor):
                # Datetime filtering currently broken with Tabulator 5.4.3
                # Initial (empty) value of filter is passed to luxon.js
                # and causes error
                fspec['headerFilter'] = False
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
        # Tabulator JS renamed select and autocomplete to list, and relies on
        # valuesLookup set to True to autopopulate the filter, instead of
        # values. This ensure backwards compatibility.
        if filter_type in ['select', 'autocomplete']:
            self.param.warning(
                f'The {filter_type!r} filter has been deprecated, use '
                f'instead the "list" filter type to configure column {column.field!r}'
            )
            filter_type = 'list'
            if filter_params.get('values', False) is True:
                self.param.warning(
                    'Setting "values" to True has been deprecated, instead '
                    f'set "valuesLookup" to True to configure column {column.field!r}'
                )
                del filter_params['values']
                filter_params['valuesLookup'] = True
        if filter_type == 'list':
            if not filter_params:
                filter_params = {'valuesLookup': True}
            if filter_func is None:
                filter_func = 'in' if filter_params.get('multiselect') else 'like'
        fspec['headerFilter'] = filter_type
        if filter_params:
            fspec['headerFilterParams'] = filter_params
        if filter_func:
            fspec['headerFilterFunc'] = filter_func
        if filter_placeholder:
            fspec['headerFilterPlaceholder'] = filter_placeholder
        return fspec

    def _config_columns(self, column_objs: list[TableColumn]) -> Sequence[ColumnSpec | GroupSpec]:
        column_objs = list(column_objs)
        groups: dict[str, GroupSpec] = {}
        columns: Sequence[ColumnSpec | GroupSpec] = []
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
        if isinstance(self.frozen_columns, dict):
            left_frozen_columns = [col for col in column_objs if
                                   self.frozen_columns.get(col.field, self.frozen_columns.get(column_objs.index(col))) == "left"]
            right_frozen_columns = [col for col in column_objs if
                                    self.frozen_columns.get(col.field, self.frozen_columns.get(column_objs.index(col))) == "right"]
            non_frozen_columns = [col for col in column_objs if
                                  col.field not in self.frozen_columns and column_objs.index(col) not in self.frozen_columns]
            ordered_columns = left_frozen_columns + non_frozen_columns + right_frozen_columns
        else:
            ordered_columns = []
            for col in self.frozen_columns:
                if isinstance(col, int):
                    ordered_columns.append(column_objs.pop(col))
                else:
                    cols = [c for c in column_objs if c.field == col]
                    if cols:
                        ordered_columns.append(cols[0])
                        column_objs.remove(cols[0])
            ordered_columns += column_objs

        grouping = {
            group: [str(gc) for gc in group_cols]
            for group, group_cols in self.groups.items()
        }
        for i, column in enumerate(ordered_columns):
            field = str(column.field)
            index = self._renamed_cols[field]
            matching_groups = [
                group for group, group_cols in grouping.items()
                if field in group_cols
            ]
            col_dict: ColumnSpec = dict(field=field)
            if isinstance(self.sortable, dict):
                col_dict['headerSort'] = _get_value_from_keys(self.sortable, index, field, True)
            elif not self.sortable:
                col_dict['headerSort'] = self.sortable
            if isinstance(self.text_align, str):
                col_dict['hozAlign'] = self.text_align  # type: ignore
            elif index in self.text_align or field in self.text_align:
                col_dict['hozAlign'] = _get_value_from_keys(self.text_align, index, field)
            if isinstance(self.header_align, str):
                col_dict['headerHozAlign'] = self.header_align  # type: ignore
            elif index in self.header_align or field in self.header_align:
                col_dict['headerHozAlign'] = _get_value_from_keys(self.header_align, index, field)  # type: ignore
            formatter = _get_value_from_keys(self.formatters, index, field)
            if isinstance(formatter, (str, JSCode)):
                col_dict['formatter'] = formatter
            elif isinstance(formatter, dict):
                formatter = dict(formatter)
                col_dict['formatter'] = formatter.pop('type')
                col_dict['formatterParams'] = formatter
            title_formatter = _get_value_from_keys(self.title_formatters, index, field)
            if isinstance(title_formatter, (str, JSCode)):
                col_dict['titleFormatter'] = title_formatter
            elif isinstance(title_formatter, dict):
                title_formatter = dict(title_formatter)
                col_dict['titleFormatter'] = title_formatter.pop('type')
                col_dict['titleFormatterParams'] = title_formatter
            if field in self.indexes:
                if len(self.indexes) == 1:
                    dtype = self.value.index.dtype
                else:
                    dtype = self.value.index.get_level_values(self.indexes.index(field)).dtype
            else:
                dtype = self.value.dtypes[index]
            if dtype.kind == 'M':
                col_dict['sorter'] = 'timestamp'
            elif dtype.kind in 'iuf':
                col_dict['sorter'] = 'number'
            elif dtype.kind == 'b':
                col_dict['sorter'] = 'boolean'
            editor = _get_value_from_keys(self.editors, index, field)
            if (index in self.editors or field in self.editors) and editor is None:
                col_dict['editable'] = False
            if isinstance(editor, (str, JSCode)):
                col_dict['editor'] = editor
            elif isinstance(editor, dict):
                editor = dict(editor)
                col_dict['editor'] = editor.pop('type')
                col_dict['editorParams'] = editor
            if col_dict.get('editor') in ['select', 'autocomplete']:
                self.param.warning(
                    f'The {col_dict["editor"]!r} editor has been deprecated, use '
                    f'instead the "list" editor type to configure column {index!r}'
                )
                col_dict['editor'] = 'list'
                if col_dict.get('editorParams', {}).get('values', False) is True:
                    del col_dict['editorParams']['values']
                    col_dict['editorParams']['valuesLookup'] = True
            if index in self.frozen_columns or field in self.frozen_columns or i in self.frozen_columns:
                if index != field and field in self.frozen_columns:
                    msg = f"The {index} format should be preferred over the {field}."
                    warn(msg, DeprecationWarning)
                col_dict['frozen'] = True
            if isinstance(self.widths, dict) and (col_width := _get_value_from_keys(self.widths, index, field)) and isinstance(col_width, str):
                col_dict['width'] = col_width
            col_dict.update(self._get_filter_spec(column))

            if index in self.header_tooltips or field in self.header_tooltips:
                col_dict["headerTooltip"] = _get_value_from_keys(self.header_tooltips, index, field)

            if isinstance(index, tuple):
                children = columns
                last = cast(GroupSpec, children[-1] if len(children) > 0 else {})
                for j, group in enumerate(index[:-1]):
                    group_title = self.titles.get(index[: j + 1], group)
                    if 'title' in last and last['title'] == group_title:
                        new = False
                        children = last['columns']
                    else:
                        new = True
                        children.append({
                            'columns': [],
                            'title': group_title,
                        })
                    last = cast(GroupSpec, children[-1])
                    if new:
                        children = last['columns']
                children.append(col_dict)
                column.title = self.titles.get(index, index[-1])
            elif matching_groups:
                group = matching_groups[0]
                if group in groups:
                    groups[group]['columns'].append(col_dict)
                    continue
                group_dict: GroupSpec = {
                    'title': group,
                    'columns': [col_dict]
                }
                groups[group] = group_dict
                columns.append(group_dict)
            else:
                columns.append(col_dict)
        return columns

    def _get_configuration(self, columns: list[TableColumn]) -> dict[str, Any]:
        """
        Returns the Tabulator configuration.
        """
        configuration = dict(self._configuration)
        if 'selectable' not in configuration:
            configuration['selectable'] = self.selectable
        if self.groups and 'columns' in configuration:
            raise ValueError("Groups must be defined either explicitly "
                             "or via the configuration, not both.")
        user_columns = {v["field"]: v for v in configuration.get('columns', {})}
        configuration["columns"] = self._config_columns(columns)
        for idx, col in enumerate(columns):
            if (name := col.field) in user_columns:
                configuration["columns"][idx] |= user_columns[name]
        configuration['dataTree'] = self.hierarchical
        if self.sizing_mode in ('stretch_height', 'stretch_both'):
            configuration['maxHeight'] = '100%'
        elif self.height:
            configuration['height'] = self.height
        return configuration

    def download(self, filename: str = 'table.csv'):
        """
        Triggers downloading of the table as a CSV or JSON.

        Parameters
        ----------
        filename: str
            The filename to save the table as.
        """
        for ref, (model, _) in self._models.copy().items():
            self._apply_update({}, {'filename': filename}, model, ref)
            self._apply_update({}, {'download': not model.download}, model, ref)

    def download_menu(self, text_kwargs={}, button_kwargs={}):
        """
        Returns a menu containing a TextInput and Button widget to set
        the filename and trigger a client-side download of the data.

        Parameters
        ----------
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

        Parameters
        ----------
        callback: (callable)
            The callback to run on edit events.
        """
        self._on_edit_callbacks.append(callback)

    def on_click(self, callback: Callable[[CellClickEvent], None], column: str | None = None):
        """
        Register a callback to be executed when any cell is clicked.
        The callback is given a CellClickEvent declaring the column
        and row of the cell that was clicked.

        Parameters
        ----------
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
    def current_view(self) -> pd.DataFrame:
        """
        Returns the current view of the table after filtering and
        sorting are applied.
        """
        df = self._processed
        if self.pagination == 'remote':
            return df
        df = self._filter_dataframe(df, header_filters=True, internal_filters=False)
        return self._sort_df(df)
