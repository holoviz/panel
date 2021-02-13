import datetime as dt

from types import FunctionType, MethodType

import numpy as np
import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets.tables import (
    DataTable, DataCube, TableColumn, GroupingInfo, RowAggregator,
    NumberEditor, NumberFormatter, DateFormatter, CellEditor,
    DateEditor, StringFormatter, StringEditor, IntEditor,
    AvgAggregator, MaxAggregator, MinAggregator, SumAggregator,
    CheckboxEditor
)

from ..depends import param_value_if_widget
from ..io.notebook import push_on_root
from ..models.tabulator import (
    DataTabulator as _BkTabulator, TABULATOR_THEMES, THEME_URL
)
from ..reactive import ReactiveData
from ..viewable import Layoutable
from ..util import isdatetime, updating
from .base import Widget
from .button import Button
from .input import TextInput


class BaseTable(ReactiveData, Widget):

    editors = param.Dict(default={}, doc="""
        Bokeh CellEditor to use for a particular column
        (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, doc="""
        Bokeh CellFormatter to use for a particular column
        (overrides the default chosen based on the type).""")

    row_height = param.Integer(default=40, doc="""
        The height of each table row.""")

    selection = param.List(default=[], doc="""
        The currently selected rows of the table.""")

    show_index = param.Boolean(default=True, doc="""
        Whether to show the index column.""")

    titles = param.Dict(default={}, doc="""
        A mapping from column name to a title to override the name with.""")

    widths = param.ClassSelector(default={}, class_=(dict, int), doc="""
        A mapping from column name to column width or a fixed column
        width.""")

    value = param.Parameter(default=None)

    _data_params = ['value']

    _manual_params = ['formatters', 'editors', 'widths', 'titles', 'value', 'show_index']

    _rename = {'disabled': 'editable', 'selection': None}

    __abstract = True

    def __init__(self, value=None, **params):
        self._renamed_cols = {}
        self._filters = []
        super().__init__(value=value, **params)

    def _validate(self, event):
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

    def _get_columns(self):
        if self.value is None:
            return []

        indexes = self.indexes
        col_names = list(self.value.columns)
        if len(indexes) == 1:
            col_names = indexes + col_names
        else:
            col_names = indexes[-1:] + col_names
        df = self.value.reset_index() if len(indexes) > 1 else self.value
        return self._get_column_definitions(col_names, df)

    def _get_column_definitions(self, col_names, df):
        import pandas as pd
        indexes = self.indexes
        columns = []
        for col in col_names:
            if col in df.columns:
                data = df[col]
            else:
                data = df.index

            if isinstance(data, pd.DataFrame):
                raise ValueError("DataFrame contains duplicate column names.")

            col_kwargs = {}
            kind = data.dtype.kind
            if kind == 'i':
                formatter = NumberFormatter()
                editor = IntEditor()
            elif kind == 'b':
                formatter = StringFormatter()
                editor = CheckboxEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]')
                editor = NumberEditor()
            elif isdatetime(data) or kind == 'M':
                if len(data) and isinstance(data.values[0], dt.date):
                    date_format = '%Y-%m-%d'
                else:
                    date_format = '%Y-%m-%d %H:%M:%S'
                formatter = DateFormatter(format=date_format)
                editor = DateEditor()
            else:
                formatter = StringFormatter()
                editor = StringEditor()

            if col in self.editors and not isinstance(self.editors[col], (dict, str)):
                editor = self.editors[col]

            if col in indexes or editor is None:
                editor = CellEditor()

            if col in self.formatters and not isinstance(self.formatters[col], (dict, str)):
                formatter = self.formatters[col]

            if str(col) != col:
                self._renamed_cols[str(col)] = col

            if isinstance(self.widths, int):
                col_kwargs['width'] = self.widths
            elif str(col) in self.widths:
                col_kwargs['width'] = self.widths.get(str(col))

            title = self.titles.get(col, str(col))
            if col in indexes and len(indexes) > 1 and self.hierarchical:
                title = 'Index: %s' % ' | '.join(indexes)
            column = TableColumn(field=str(col), title=title,
                                 editor=editor, formatter=formatter,
                                 **col_kwargs)
            columns.append(column)
        return columns

    def _get_model(self, doc, root=None, parent=None, comm=None):
        source = ColumnDataSource(data=self._data)
        source.selected.indices = self.selection
        model = self._widget_type(**self._get_properties(source))
        if root is None:
            root = model
        self._link_props(model.source, ['data'], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update_columns(self, event, model):
        model.columns = self._get_columns()

    def _manual_update(self, events, model, doc, root, parent, comm):
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

    def _filter_dataframe(self, df, ):
        """
        Filter the DataFrame.

        Parameters
        ----------
        df : DataFrame
           The DataFrame to filter
        query : dict
            A dictionary containing all the query parameters

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
        if filters:
            mask = filters[0]
            for f in filters:
                mask &= f
            df = df[mask]
        return df

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

    def _get_data(self):
        df = self._filter_dataframe(self.value)
        if df is None:
            return [], {}
        elif len(self.indexes) > 1:
            df = df.reset_index()
        data = ColumnDataSource.from_df(df).items()
        return df, {k if isinstance(k, str) else str(k): v for k, v in data}

    def _update_column(self, column, array):
        self.value[column] = array

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def indexes(self):
        import pandas as pd
        if self.value is None or not self.show_index:
            return []
        elif isinstance(self.value.index, pd.MultiIndex):
            return list(self.value.index.names)
        return [self.value.index.name or 'index']

    def stream(self, stream_value, reset_index=True):
        """
        Streams (appends) the `stream_value` provided to the existing
        value in an efficient manner.

        Arguments
        ---------
        stream_value (Union[pd.DataFrame, pd.Series, Dict])
          The new value(s) to append to the existing value.
        reset_index (bool, default=True):
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
        value_index_start = self.value.index.max() + 1
        if isinstance(stream_value, pd.DataFrame):
            if reset_index:
                stream_value = stream_value.reset_index(drop=True)
                stream_value.index += value_index_start
            with param.discard_events(self):
                self.value = pd.concat([self.value, stream_value])
            try:
                self._updating = True
                self.param.trigger('value')
            finally:
                self._updating = False
            stream_value = self._filter_dataframe(stream_value)
            try:
                self._updating = True
                self._stream(stream_value)
            finally:
                self._updating = False
        elif isinstance(stream_value, pd.Series):
            self.value.loc[value_index_start] = stream_value
            stream_value = self._filter_dataframe(self.value.iloc[-1:])
            try:
                self._updating = True
                self._stream(stream_value)
            finally:
                self._updating = False
        elif isinstance(stream_value, dict):
            if stream_value:
                try:
                    stream_value = pd.DataFrame(stream_value)
                except ValueError:
                    stream_value = pd.Series(stream_value)
                self.stream(stream_value)
        else:
            raise ValueError("The stream value provided is not a DataFrame, Series or Dict!")

    def patch(self, patch_value):
        """
        Efficiently patches (updates) the existing value with the `patch_value`.

        Arguments
        ---------
        patch_value: (Union[pd.DataFrame, pd.Series, Dict])
          The value(s) to patch the existing value with.

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
        if self.value is None or isinstance(patch_value, dict):
            self._patch(patch_value)
            return

        import pandas as pd
        if not isinstance(self.value, pd.DataFrame):
            raise ValueError(
                f"Patching an object of type {type(self.value).__name__} "
                "is not supported. Please provide a dict."
            )

        if isinstance(patch_value, pd.DataFrame):
            patch_value_dict = {}
            for column in patch_value.columns:
                patch_value_dict[column] = []
                for index in patch_value.index:
                    patch_value_dict[column].append((index, patch_value.loc[index, column]))
            self.patch(patch_value_dict)
        elif isinstance(patch_value, pd.Series):
            if "index" in patch_value:  # Series orient is row
                patch_value_dict = {
                    k: [(patch_value["index"], v)] for k, v in patch_value.items()
                }
                patch_value_dict.pop("index")
            else:  # Series orient is column
                patch_value_dict = {
                    patch_value.name: [(index, value) for index, value in patch_value.items()]
                }
            self.patch(patch_value_dict)
        elif isinstance(patch_value, dict):
            for k, v in patch_value.items():
                for update in v:
                    self.value.loc[update[0], k] = update[1]
                self._patch(patch_value)
        else:
            raise ValueError(
                f"Patching with a patch_value of type {type(patch_value).__name__} "
                "is not supported. Please provide a DataFrame, Series or Dict."
            )

    @property
    def selected_dataframe(self):
        """
        Returns a DataFrame of the currently selected rows.
        """
        if not self.selection:
            return self.value
        return self.value.iloc[self.selection]



class DataFrame(BaseTable):

    aggregators = param.Dict(default={}, doc="""
        A dictionary mapping from index name to an aggregator to
        be used for hierarchical multi-indexes (valid aggregators
        include 'min', 'max', 'mean' and 'sum'). If separate
        aggregators for different columns are required the dictionary
        may be nested as `{index_name: {column_name: aggregator}}`""")

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

    hierarchical = param.Boolean(default=False, constant=True, doc="""
        Whether to generate a hierachical index.""")

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

    _manual_params = BaseTable._manual_params + ['aggregators']

    _aggregators = {'sum': SumAggregator, 'max': MaxAggregator,
                    'min': MinAggregator, 'mean': AvgAggregator}

    @property
    def _widget_type(self):
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
    The Tabulator Pane wraps the [Tabulator](http://tabulator.info/)
    table to provide a full-featured interactive table.
    """

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

    hidden_columns = param.List(default=[], doc="""
        List of columns to hide.""")

    layout = param.ObjectSelector(default='fit_data_table', objects=[
        'fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table',
        'fit_columns'])

    pagination = param.ObjectSelector(default=None, allow_None=True,
                                      objects=['local', 'remote'])

    page = param.Integer(default=1, doc="""
        Currently selected page (indexed starting at 1).""")

    page_size = param.Integer(default=20, bounds=(1, None), doc="""
        Number of rows to render per page.""")

    row_height = param.Integer(default=30, doc="""
        The height of each table row.""")

    selectable = param.ObjectSelector(
        default=True, objects=[True, False, 'checkbox'], doc="""
        Whether a table's rows can be selected or not. Multiple
        selection is allowed and can be achieved by either clicking
        multiple checkboxes (if enabled) or using Shift + click on
        rows.""")

    sorters = param.List(default=[], doc="""
        A list of sorters to apply during pagination.""")

    theme = param.ObjectSelector(
        default="simple", objects=TABULATOR_THEMES, doc="""
        Tabulator CSS theme to apply to table.""")

    _widget_type = _BkTabulator

    _data_params = ['value', 'page', 'page_size', 'pagination', 'sorters']

    _config_params = ['frozen_columns', 'groups', 'selectable']

    _manual_params = BaseTable._manual_params + _config_params

    def __init__(self, value=None, **params):
        configuration = params.pop('configuration', {})
        self.style = None
        super().__init__(value=value, **params)
        self._configuration = configuration

    def _validate(self, event):
        super()._validate(event)
        if self.value is not None:
            todo = []
            if self.style is not None:
                todo = self.style._todo
            self.style = self.value.style
            self.style._todo = todo

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'frozen_rows' in msg:
            length = self._length
            msg['frozen_rows'] = [length+r if r < 0 else r
                                  for r in msg['frozen_rows']]
        if 'theme' in msg:
            if 'bootstrap' in self.theme:
                msg['theme_url'] = THEME_URL + 'bootstrap/'
            elif 'materialize' in self.theme:
                msg['theme_url'] = THEME_URL + 'materialize/'
            elif 'semantic-ui' in self.theme:
                msg['theme_url'] = THEME_URL + 'semantic-ui/'
            elif 'bulma' in self.theme:
                msg['theme_url'] = THEME_URL + 'bulma/'
            else:
                msg['theme_url'] = THEME_URL
            theme = 'tabulator' if self.theme == 'default' else 'tabulator_'+self.theme 
            _BkTabulator.__css__ = [msg['theme_url'] + theme + '.min.css']
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

    def _sort_df(self, df):
        if not self.sorters:
            return df
        return df.sort_values(
            [s['field'] for s in self.sorters],
            ascending=[s['dir'] == 'asc' for s in self.sorters]
        )

    def _get_data(self):
        if self.pagination != 'remote' or self.value is None:
            return super()._get_data()
        df = self._filter_dataframe(self.value)
        df = self._sort_df(df)
        nrows = self.page_size
        start = (self.page-1)*nrows
        page_df = df.iloc[start: start+nrows]
        data = ColumnDataSource.from_df(page_df).items()
        return df, {k if isinstance(k, str) else str(k): v for k, v in data}

    @property
    def _length(self):
        return len(self._processed)

    def _get_style_data(self):
        if self.value is None:
            return {}
        if self.pagination == 'remote':
            nrows = self.page_size
            start = (self.page-1)*nrows
            df = self.value.iloc[start: start+nrows]
        else:
            df = self.value

        styler = df.style
        styler._todo = self.style._todo
        styler._compute()
        offset = len(self.indexes)

        styles = {}
        for (r, c), s in styler.ctx.items():
            if r not in styles:
                styles[int(r)] = {}
            styles[int(r)][offset+int(c)] = s
        return styles

    def _update_style(self):
        styles = self._get_style_data()
        for ref, (m, _) in self._models.items():
            m.styles = styles
            push_on_root(ref)

    @updating
    def _stream(self, stream, follow=True):
        if self.pagination == 'remote':
            length = self._length
            nrows = self.page_size
            max_page = length//nrows + bool(length%nrows)
            if self.page != max_page:
                return
        super()._stream(stream)
        self._update_style()

    def stream(self, stream_value, reset_index=True, follow=True):
        for ref, (m, _) in self._models.items():
            m.follow = follow
            push_on_root(ref)
        if follow and self.pagination:
            length = self._length
            nrows = self.page_size
            self.page = length//nrows + bool(length%nrows)
        super().stream(stream_value, reset_index)

    @updating
    def _patch(self, patch):
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
        if self.pagination == 'remote':
            self._update_style()

    def _update_cds(self, *events):
        if self._updating:
            return
        super()._update_cds(*events)
        if self.pagination:
            self._update_max_page()
            self._update_selected()
        self._update_style()

    def _update_max_page(self):
        length = self._length
        nrows = self.page_size
        max_page = length//nrows + bool(length%nrows)
        self.param.page.bounds = (1, max_page)
        for ref, (m, _) in self._models.items():
            m.max_page = max_page
            push_on_root(ref)

    def _update_selected(self, *events, indices=None):
        if self._updating:
            return
        kwargs = {}
        if self.pagination == 'remote':
            index = self.value.iloc[self.selection].index
            indices = []
            for v in index.values:
                try:
                    indices.append(self._processed.index.get_loc(v))
                except KeyError:
                    continue
            nrows = self.page_size
            start = (self.page-1)*nrows
            end = start+nrows
            kwargs['indices'] = [ind-start for ind in indices
                                 if ind>=start and ind<end]
        super()._update_selected(*events, **kwargs)

    def _update_column(self, column, array):
        if self.pagination != 'remote':
            self.value[column] = array
            return
        nrows = self.page_size
        start = (self.page-1)*nrows
        end = start+nrows
        if self.sorters:
            index = self._processed.iloc[start:end].index.values
            self.value[column].loc[index] = array
        else:
            self.value[column].iloc[start:end] = array

    def _update_selection(self, indices):
        if self.pagination != 'remote':
            self.selection = indices
        nrows = self.page_size
        start = (self.page-1)*nrows
        index = self._processed.iloc[[start+ind for ind in indices]].index
        indices = []
        for v in index.values:
            try:
                indices.append(self.value.index.get_loc(v))
            except KeyError:
                continue
        self.selection = indices

    def _get_properties(self, source):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        if self.pagination:
            length = self.page_size
        else:
            length = self._length
        if props.get('height', None) is None:
            props['height'] = length * self.row_height + 30
        props['source'] = source
        props['styles'] = self._get_style_data()
        props['columns'] = columns = self._get_columns()
        props['configuration'] = self._get_configuration(columns)
        props['page'] = self.page
        props['pagination'] = self.pagination
        props['page_size'] = self.page_size
        props['layout'] = self.layout
        props['groupby'] = self.groupby
        props['hidden_columns'] = self.hidden_columns
        process = {'theme': self.theme, 'frozen_rows': self.frozen_rows}
        props.update(self._process_param_change(process))
        if self.pagination:
            length = 0 if self._processed is None else len(self._processed)
            props['max_page'] = length//self.page_size + bool(length%self.page_size)
        return props

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super()._get_model(doc, root, parent, comm)
        if root is None:
            root = model
        self._link_props(model, ['page', 'sorters'], doc, root, comm)
        return model

    def _config_columns(self, column_objs):
        column_objs = list(column_objs)
        groups = {}
        columns = []
        if self.selectable == 'checkbox':
            columns.append({
                "formatter": "rowSelection",
                "titleFormatter": "rowSelection",
                "hozAlign": "center",
                "headerSort": False,
                "frozen": True
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

        for i, column in enumerate(ordered):
            matching_groups = [
                group for group, group_cols in self.groups.items()
                if column.field in group_cols
            ]
            col_dict = {'field': column.field}
            formatter = self.formatters.get(column.field)
            if isinstance(formatter, str):
                col_dict['formatter'] = formatter
            elif isinstance(formatter, dict):
                formatter = dict(formatter)
                col_dict['formatter'] = formatter.pop('type')
                col_dict['formatterParams'] = formatter
            editor = self.editors.get(column.field)
            if isinstance(editor, str):
                col_dict['editor'] = editor
            elif isinstance(editor, dict):
                editor = dict(editor)
                col_dict['editor'] = editor.pop('type')
                col_dict['editorParams'] = editor
            if column.field in self.frozen_columns or i in self.frozen_columns:
                col_dict['frozen'] = True
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

    def _get_configuration(self, columns):
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
        return configuration

    def download(self, filename='table.csv'):
        """
        Triggers downloading of the table as a CSV or JSON.

        Arguments
        ---------
        filename: str
            The filename to save the table as.
        """
        for ref, (m, _) in self._models.items():
            m.filename = m.filename
            push_on_root(ref)
        for ref, (m, _) in self._models.items():
            m.download = not m.download
            push_on_root(ref)

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
        button_kwargs = dict(button_kwargs)
        if 'name' not in button_kwargs:
            button_kwargs['name'] = 'Download'
        button = Button(**button_kwargs)
        button.js_on_click({'table': self}, code="""
        table.download = !table.download
        """)

        text_kwargs = dict(text_kwargs)
        if 'name' not in text_kwargs:
            text_kwargs['name'] = 'Filename'
        if 'value' not in text_kwargs:
            text_kwargs['value'] = 'table.csv'
        filename = TextInput(name='Filename', value='table.csv')
        filename.jscallback({'table': self}, value="""
        table.filename = cb_obj.value
        """)
        return filename, button
