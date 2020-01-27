from __future__ import absolute_import, division, unicode_literals

import numpy as np
import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import (
    DataTable, TableColumn, NumberEditor, NumberFormatter,
    DateFormatter, DateEditor, StringFormatter, StringEditor, IntEditor
)

from ..viewable import Layoutable
from ..util import isdatetime
from .base import Widget


class DataFrame(Widget):

    editors = param.Dict(default={}, doc="""
      Bokeh CellEditor to use for a particular column
      (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, doc="""
      Bokeh CellFormatter to use for a particular column
      (overrides the default chosen based on the type).""")

    fit_columns = param.Boolean(default=True, doc="""
      Whether columns should expand to the available width.
      This results in no horizontal scrollbar showing up, but data
      can get unreadable if there is no enough space available.""")

    selection = param.List(default=[], doc="""
      The currently selected rows of the table.""")

    row_height = param.Integer(default=25, doc="""
      The height of each table row.""")

    widths = param.Dict(default={}, doc="""
      A mapping from column name to column width.""")

    value = param.Parameter(default=None)

    _rename = {'editors': None, 'formatters': None, 'widths': None,
               'disabled': None}

    _manual_params = ['value', 'editors', 'formatters', 'selection', 'widths']

    def __init__(self, value=None, **params):
        super(DataFrame, self).__init__(value=value, **params)
        self._renamed_cols = {}

    def _get_columns(self):
        if self.value is None:
            return []

        index = [self.value.index.name or 'index']
        col_names = index + list(self.value.columns)
        columns = []
        for col in col_names:
            if col in self.value.columns:
                data = self.value[col]
            else:
                data = self.value.index
            kind = data.dtype.kind
            if kind == 'i':
                formatter = NumberFormatter()
                editor = IntEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]')
                editor = NumberEditor()
            elif isdatetime(data):
                formatter = DateFormatter(format='%Y-%m-%d %H:%M:%S')
                editor = DateEditor()
            else:
                formatter = StringFormatter()
                editor = StringEditor()
            if col in self.editors:
                editor = self.editors[col]
            if col in self.formatters:
                formatter = self.formatters[col]
            if str(col) != col:
                self._renamed_cols[str(col)] = col
            width = self.widths.get(str(col))
            column = TableColumn(field=str(col), title=str(col),
                                 editor=editor, formatter=formatter,
                                 width=width)
            columns.append(column)
        return columns

    def _get_properties(self):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        if self.value is None:
            data = {}
        else:
            data = {k if isinstance(k, str) else str(k): v
                    for k, v in ColumnDataSource.from_df(self.value).items()}
        if props.get('height', None) is None:
            length = max([len(v) for v in data.values()]) if data else 0
            props['height'] = length * self.row_height + 30
        props['source'] = ColumnDataSource(data=data)
        props['columns'] = self._get_columns()
        props['index_position'] = None
        props['fit_columns'] = self.fit_columns
        props['row_height'] = self.row_height
        props['editable'] = not self.disabled
        return props

    def _process_param_change(self, msg):
        if 'disabled' in msg:
            msg['editable'] = not msg.pop('disabled')
        return super(DataFrame, self)._process_param_change(msg)
    
    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = DataTable(**self._get_properties())
        if root is None:
            root = model
        self._link_props(model.source, ['data', ('patching', 'data')], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _manual_update(self, events, model, doc, root, parent, comm):
        for event in events:
            if event.name == 'value':
                cds = model.source
                data = {k if isinstance(k, str) else str(k): v
                        for k, v in ColumnDataSource.from_df(self.value).items()}
                cds.data = data
                model.columns = self._get_columns()
            elif event.name == 'selection':
                model.source.selected.indices = self.selection
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
                if k == 'index':
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
                self.param.trigger('value')
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
