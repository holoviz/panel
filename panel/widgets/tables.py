from __future__ import absolute_import, division, unicode_literals

import numpy as np
import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets.tables import (
    DataTable, DataCube, TableColumn, GroupingInfo, RowAggregator,
    NumberEditor, NumberFormatter, DateFormatter, CellEditor,
    DateEditor, StringFormatter, StringEditor, IntEditor, TextEditor,
    AvgAggregator, MaxAggregator, MinAggregator, SumAggregator
)

from ..config import config
from ..models.tabulator import DataTabulator as _BkTabulator, CSS_HREFS
from ..viewable import Layoutable
from ..util import isdatetime
from .base import Widget


class BaseTable(Widget):

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

    widths = param.ClassSelector(default={}, class_=(dict, int), doc="""
        A mapping from column name to column width or a fixed column
        width.""")

    value = param.Parameter(default=None)

    _manual_params = ['formatters', 'editors', 'widths', 'value', 'show_index']

    _rename = {'disabled': None, 'selection': None}

    def __init__(self, value=None, **params):
        super(BaseTable, self).__init__(value=value, **params)
        self._renamed_cols = {}
        self._updating = False
        self._source = ColumnDataSource()
        self.param.watch(self._validate, 'value')
        self.param.watch(self._update_column_data_source, 'value')
        self.param.watch(self._update_selected_indices, 'selection')
        self._validate(None)
        self._update_column_data_source()

    def _validate(self, event):
        if self.value is None:
            return
        cols = self.value.columns
        if len(cols) != len(cols.drop_duplicates()):
            raise ValueError('Cannot display a pandas.DataFrame with '
                             'duplicate column names.')

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
        indexes = self.indexes
        columns = []
        for col in col_names:
            if col in df.columns:
                data = df[col]
            else:
                data = df.index

            col_kwargs = {}
            kind = data.dtype.kind
            if kind == 'i':
                formatter = NumberFormatter()
                editor = IntEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]')
                editor = NumberEditor()
            elif isdatetime(data) or kind == 'M':
                formatter = DateFormatter(format='%Y-%m-%d %H:%M:%S')
                editor = DateEditor()
            else:
                formatter = StringFormatter()
                editor = StringEditor()

            if col in self.editors:
                editor = self.editors[col]

            if col in indexes or editor is None:
                editor = CellEditor()

            if col in self.formatters:
                formatter = self.formatters[col]
            if str(col) != col:
                self._renamed_cols[str(col)] = col

            if isinstance(self.widths, int):
                col_kwargs['width'] = self.widths
            elif str(col) in self.widths:
                col_kwargs['width'] = self.widths.get(str(col))

            title = str(col)
            if col in indexes and len(indexes) > 1 and self.hierarchical:
                title = 'Index: %s' % ' | '.join(indexes)
            column = TableColumn(field=str(col), title=title,
                                 editor=editor, formatter=formatter,
                                 **col_kwargs)
            columns.append(column)
        return columns

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._widget_type(**self._get_properties())
        if root is None:
            root = model
        self._link_props(model.source, ['data', ('patching', 'data')], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _manual_update(self, events, model, doc, root, parent, comm):
        for event in events:
            if event.type == 'triggered' and self._updating:
                continue
            elif event.name in ('value', 'show_index'):
                model.columns = self._get_columns()
                if isinstance(model, DataCube):
                    model.groupings = self._get_groupings()
            elif hasattr(self, '_update_' + event.name):
                getattr(self, '_update_' + event.name)(model)
            else:
                for col in model.columns:
                    if col.name in self.editors:
                        col.editor = self.editors[col.name]
                    if col.name in self.formatters:
                        col.formatter = self.formatters[col.name]
                    if col.name in self.widths:
                        col.width = self.widths[col.name]

    def _update_column_data_source(self, *events):
        if self._updating:
            return

        df = self.value.reset_index() if len(self.indexes) > 1 else self.value
        if df is None:
            data = {}
        else:
            data = {k if isinstance(k, str) else str(k): v
                    for k, v in ColumnDataSource.from_df(df).items()}
        self._source.data = data

    def _update_selected_indices(self, *events):
        self._source.selected.indices = self.selection

    def _process_events(self, events):
        if 'data' in events:
            data = events.pop('data')
            updated = False
            for k, v in data.items():
                if k in self.indexes:
                    continue
                k = self._renamed_cols.get(k, k)
                if isinstance(v, dict):
                    v = [v for _, v in sorted(v.items(), key=lambda it: int(it[0]))]
                try:
                    isequal = (self.value[k].values == np.asarray(v)).all()
                except Exception:
                    isequal = False
                if not isequal:
                    self.value[k] = v
                    updated = True
            if updated:
                self._updating = True
                try:
                    self.param.trigger('value')
                finally:
                    self._updating = False
        if 'indices' in events:
            self.selection = events.pop('indices')
        super(BaseTable, self)._process_events(events)

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
          If the stream_value is a DataFrame and `reset_index` is True
          then the index of it is reset if True. Helps to keep the
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
        if isinstance(self.value, pd.DataFrame):
            value_index_start = self.value.index.max() + 1
            if isinstance(stream_value, pd.DataFrame):
                if reset_index:
                    stream_value = stream_value.reset_index(drop=True)
                    stream_value.index += value_index_start
                self._updating = True
                self.value = pd.concat([self.value, stream_value])
                self._source.stream(stream_value)
                self._updating = False
            elif isinstance(stream_value, pd.Series):
                self._updating = True
                self.value.loc[value_index_start] = stream_value
                self._source.stream(stream_value)
                self.param.trigger("value")
                self._updating = False
            elif isinstance(stream_value, dict):
                if stream_value:
                    try:
                        stream_value = pd.DataFrame(stream_value)
                    except ValueError:
                        stream_value = pd.Series(stream_value)
                    self.stream(stream_value)
            else:
                raise ValueError("The patch value provided is not a DataFrame, Series or Dict!")
        else:
            self._updating = True
            self._source.stream(stream_value)
            self.param.trigger("value")
            self._updating = False

    def patch(self, patch_value):
        """
        Patches (updates) the existing value with the `patch_value` in
        an efficient manner.

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

        Patch a DataFrame with a Series. Please note the index is used in the update
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
        if self.value is None or self.value is self._source and isinstance(patch_value, dict):
            self._updating = True
            self._source.patch(patch_value)
            self.param.trigger("value")
            self._updating = False
            return

        import pandas as pd
        if not isinstance(self.value, pd.DataFrame):
            raise ValueError(
                f"""Patching a patch_value of type {type(patch_value)} is not supported.
                Please provide a dict"""
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
            self._updating = True
            for k, v in patch_value.items():
                for update in v:
                    self.value.loc[update[0], k] = update[1]
                self._source.patch(patch_value)
            self.param.trigger("value")
            self._updating = False
        else:
            raise ValueError(
                f"""Patching a patch_value of type {type(patch_value)} is not supported.
                Please provide a DataFrame, Series or Dict"""
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

        Describes the column autosizing mode with one of the following options:

        ``"fit_columns"``
          Compute columns widths based on cell contents but ensure the
          table fits into the available viewport. This results in no
          horizontal scrollbar showing up, but data can get unreadable
          if there is not enough space available.

        ``"fit_viewport"``
          Adjust the viewport size after computing columns widths based
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
        Integer indicating the number of columns to freeze. If set the
        first N columns will be frozen which prevents them from
        scrolling out of frame.""")

    frozen_rows = param.Integer(default=None, doc="""
       Integer indicating the number of rows to freeze. If set the
       first N rows will be frozen which prevents them from scrolling
       out of frame, if set to a negative value last N rows will be
       frozen.""")

    reorderable = param.Boolean(default=True, doc="""
        Allows the reordering of a table's columns. To reorder a
        column, click and drag a table's header to the desired
        location in the table.  The columns on either side will remain
        in their previous order.""")

    sortable = param.Boolean(default=True, doc="""
        Allows to sort table's contents. By default natural order is
        preserved.  To sort a column, click on it's header. Clicking
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

    def _get_properties(self):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        if props.get('height', None) is None:
            data = self._source.data
            length = max([len(v) for v in data.values()]) if data else 0
            props['height'] = length * self.row_height + 30
        if self.hierarchical:
            props['target'] = ColumnDataSource(data=dict(row_indices=[], labels=[]))
            props['grouping'] = self._get_groupings()
        props['source'] = self._source
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

    def _process_param_change(self, msg):
        if 'disabled' in msg:
            msg['editable'] = not msg.pop('disabled') and len(self.indexes) <= 1
        return super(DataFrame, self)._process_param_change(msg)

    def _update_aggregators(self, model):
        for g in model.grouping:
            group = self._renamed_cols.get(g.getter, g.getter)
            index = self.indexes[self.indexes.index(group)+1]
            g.aggregators = self._get_aggregators(index)


class Tabulator(BaseTable):
    """
    The Tabulator Pane wraps the [Tabulator](http://tabulator.info/)
    table to provide an awesome interactive table.
    """

    groups = param.Dict(default=None)

    layout = param.ObjectSelector(default='fit_data', objects=[
        'fit_data', 'fit_data_fill', 'fit_data_stretch', 'fit_data_table',
        'fit_columns'])

    _widget_type = _BkTabulator

    def __init__(self, value=None, **params):
        configuration = params.pop('configuration', {})
        super().__init__(value=value, **params)
        self._configuration = configuration

    def _get_properties(self):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        if props.get('height', None) is None:
            data = self._source.data
            length = max([len(v) for v in data.values()]) if data else 0
            props['height'] = length * self.row_height + 30
        props['source'] = self._source
        props['columns'] = self._get_columns()
        props['configuration'] = self.configuration
        return props

    @property
    def configuration(self):
        """
        Returns the Tabulator configuration.
        """
        configuration = dict(self._configuration)
        groups = dict(self.groups or {})
        order = []
        cols = {}
        for column in configuration.get('columns', []):
            if 'columns' in column:
                order.append(column['title'])
                groups[column['title']] = []
                for col in column['columns']:
                    field = col['field']
                    cols[field] = col
                    groups[column['title']].append(field)
            else:
                order.append(col['field'])
                cols[col['field']] = col

        columns = self._get_columns()
        config_cols = []
        for column in columns:
            editor = column.editor
            if column.field in cols:
                col = cols[column.field]
            else:
                col = {
                    'field': column.field,
                    'title': column.title
                }
            if isinstance(self.widths, int) and column.field in self.widths:
                col['width'] = column.width
            if column.field not in self.editors and 'editor' in col:
                config_cols.append(column)
                continue

            if isinstance(editor, StringEditor):
                if completions:
                    col['editor'] = 'autocomplete'
                    col['editorParams'] = editor.options
                else:
                    col['editor'] = 'input'
            elif isinstance(editor, TextEditor):
                col['editor'] = 'textarea'
            elif isinstance(editor, (IntEditor, NumberEditor)):
                col['editor'] = 'number'
                col['editorParams'] = {'step': editor.step}
            elif isinstance(editor, CheckboxEditor):
                col['editor'] = 'tickCross'
            elif isinstance(editor, SelectEditor):
                col['editor'] = "select"
                col['editorParams'] = {'values': editor.options}
            config_cols.append(column)

        ordered = []
        if order:
            config_cols = {c['field']: c for c in config_cols}
            for col in order:
                if col in groups:
                    group = {'title': col, 'columns': []}
                    for col in groups[col]:
                        group['columns'].append(config_cols[col])
                    ordered.append(group)
                else:
                    ordered.append(config_cols[col])
        else:
            for col in config_cols:
                field = col['field']
                grouped = False
                for title, group in groups.items():
                    if field in group:
                        grouped = True
                        break
                if grouped:
                    group[group.index(field)] = col
                    if group not in ordered:
                        ordered.append(group)
                else:
                    ordered.append(col)

        configuration['columns'] = ordered
        return configuration
        
    @staticmethod
    def config(css="default"):
        """
        Adds the specified css theme to pn.config.css_files

        Arguments
        ---------
        css: (Optional[str], optional)
          Defaults to "default".
        """
        if css:
            href = CSS_HREFS[css]
            if href not in config.css_files:
                config.css_files.append(href)
