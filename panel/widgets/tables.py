import sys
import threading

import param

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import (
    Div, DataTable, TableColumn, NumberEditor, NumberFormatter,
    DateFormatter, DateEditor, StringFormatter, StringEditor, IntEditor,
    CheckboxEditor, BooleanFormatter
)

from ..io import state
from ..viewable import Layoutable
from .base import Widget


class DataFrame(Widget):

    editors = param.Dict(default={}, doc="""
      Bokeh CellEditor to use for a particular column
      (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, doc="""
      Bokeh CellFormatter to use for a particular column
      (overrides the default chosen based on the type).""")

    editable = param.Boolean(default=True, doc="""
      Whether the table should be editable.""")

    selection = param.List(default=[], doc="""
      The currently selected rows of the table.""")

    value = param.Parameter(default=None)

    def __init__(self, value=None, **params):
        super(DataFrame, self).__init__(value=value, **params)
        self._renamed_cols = {}

    def _get_columns(self):
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
            column = TableColumn(field=str(col), title=str(col),
                                 editor=editor, formatter=formatter)
            columns.append(column)
        return columns

    def _get_properties(self):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        data = {k if isinstance(k, str) else str(k): v
                for k, v in ColumnDataSource.from_df(self.value).items()}
        props['source'] = ColumnDataSource(data=data)
        props['columns'] = self._get_columns()
        props['index_position'] = None
        props['editable'] = self.editable
        return props

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = DataTable(**self._get_properties())
        if root is None:
            root = model
        self._link_props(model.source, ['data', ('patching', 'data')], doc, root, comm)
        self._link_props(model.source.selected, ['indices'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_events(self, events):
        if 'data' in events:
            data = events.pop('data')
            for k, v in data.items():
                if k == 'index':
                    continue
                k = self._renamed_cols.get(k, k)
                self.value[k] = v
        if 'indices' in events:
            self.selected = events.pop('indices')
        super(DataFrame, self)._process_events(events)
