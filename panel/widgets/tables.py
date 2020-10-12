from __future__ import absolute_import, division, unicode_literals

import numpy as np
import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets.tables import (
    DataTable, DataCube, TableColumn, GroupingInfo, RowAggregator,
    NumberEditor, NumberFormatter, DateFormatter, CellEditor,
    DateEditor, StringFormatter, StringEditor, IntEditor,
    AvgAggregator, MaxAggregator, MinAggregator, SumAggregator
)

from ..viewable import Layoutable
from ..util import isdatetime
from .base import Widget


class DataFrame(Widget):

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

    editors = param.Dict(default={}, doc="""
        Bokeh CellEditor to use for a particular column
        (overrides the default chosen based on the type).""")

    hierarchical = param.Boolean(default=False, constant=True, doc="""
        Whether to generate a hierachical index.""")

    formatters = param.Dict(default={}, doc="""
        Bokeh CellFormatter to use for a particular column
        (overrides the default chosen based on the type).""")

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

    selection = param.List(default=[], doc="""
        The currently selected rows of the table.""")

    show_index = param.Boolean(default=True, doc="""
        Whether to show the index column.""")

    sortable = param.Boolean(default=True, doc="""
        Allows to sort table's contents. By default natural order is
        preserved.  To sort a column, click on it's header. Clicking
        one more time changes sort direction. Use Ctrl + click to
        return to natural order. Use Shift + click to sort multiple
        columns simultaneously.""")

    row_height = param.Integer(default=25, doc="""
        The height of each table row.""")

    widths = param.ClassSelector(default={}, class_=(dict, int), doc="""
        A mapping from column name to column width or a fixed column
        width.""")

    value = param.Parameter(default=None)

    _rename = {'editors': None, 'formatters': None, 'widths': None,
               'disabled': None, 'show_index': None}

    _manual_params = ['value', 'editors', 'formatters', 'selection',
                      'widths', 'aggregators', 'show_index']

    _aggregators = {'sum': SumAggregator, 'max': MaxAggregator,
                    'min': MinAggregator, 'mean': AvgAggregator}

    def __init__(self, value=None, **params):
        super(DataFrame, self).__init__(value=value, **params)
        self.param.watch(self._validate, 'value')
        self._validate(None)
        self._renamed_cols = {}
        self._updating = False

    def _validate(self, event):
        if self.value is None:
            return
        cols = self.value.columns
        if len(cols) != len(cols.drop_duplicates()):
            raise ValueError('Cannot display a pandas.DataFrame with '
                             'duplicate column names.')

    @property
    def indexes(self):
        import pandas as pd
        if self.value is None or not self.show_index:
            return []
        elif isinstance(self.value.index, pd.MultiIndex):
            return list(self.value.index.names)
        return [self.value.index.name or 'index']

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
        df = self.value.reset_index() if len(self.indexes) > 1 else self.value
        if df is None:
            data = {}
        else:
            data = {k if isinstance(k, str) else str(k): v
                    for k, v in ColumnDataSource.from_df(df).items()}
        if props.get('height', None) is None:
            length = max([len(v) for v in data.values()]) if data else 0
            props['height'] = length * self.row_height + 30
        if self.hierarchical:
            props['target'] = ColumnDataSource(data=dict(row_indices=[], labels=[]))
            props['grouping'] = self._get_groupings()
        props['source'] = ColumnDataSource(data=data)
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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model_type = DataCube if self.hierarchical else DataTable
        model = model_type(**self._get_properties())
        if root is None:
            root = model
        self._link_props(model.source, ['data', ('patching', 'data')], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _manual_update(self, events, model, doc, root, parent, comm):
        self._validate(None)
        for event in events:
            if event.type == 'triggered' and self._updating:
                continue
            elif event.name in ('value', 'show_index'):
                cds = model.source
                data = {k if isinstance(k, str) else str(k): v
                        for k, v in ColumnDataSource.from_df(self.value).items()}
                cds.data = data
                model.columns = self._get_columns()
                if isinstance(model, DataCube):
                    model.groupings = self._get_groupings()
            elif event.name == 'selection':
                model.source.selected.indices = self.selection
            elif event.name == 'aggregators':
                for g in model.grouping:
                    group = self._renamed_cols.get(g.getter, g.getter)
                    index = self.indexes[self.indexes.index(group)+1]
                    g.aggregators = self._get_aggregators(index)
            else:
                for col in model.columns:
                    if col.name in self.editors:
                        col.editor = self.editors[col.name]
                    if col.name in self.formatters:
                        col.formatter = self.formatters[col.name]
                    if col.name in self.widths:
                        col.width = self.widths[col.name]

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
        super(DataFrame, self)._process_events(events)

    @property
    def selected_dataframe(self):
        """
        Returns a DataFrame of the currently selected rows.
        """
        if not self.selection:
            return self.value
        return self.value.iloc[self.selection]
