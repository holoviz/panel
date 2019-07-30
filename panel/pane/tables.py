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
from .base import PaneBase


class DataFrame(PaneBase):

    editors = param.Dict(default={}, doc="""
      Bokeh CellEditor to use for a particular column
      (overrides the default chosen based on the type).""")

    formatters = param.Dict(default={}, doc="""
      Bokeh CellFormatter to use for a particular column
      (overrides the default chosen based on the type).""")

    editable = param.Boolean(default=True, doc="""
      Whether the table should be editable.""")

    interactive = param.Boolean(default=False, doc="""
      Whether to display an interactive or static table.""")

    def __init__(self, object, **params):
        super(DataFrame, self).__init__(object, **params)
        self._renamed_cols = {}

    @classmethod
    def applies(cls, obj):
        if 'pandas' not in sys.modules:
            return False
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            return 1
        else:
            return None

    @property
    def _bokeh_model(self):
        return DataTable if self.interactive else Div

    def _get_columns(self):
        index = [self.object.index.name or 'index']
        col_names = index + list(self.object.columns)
        columns = []
        for col in col_names:
            if col in self.object.columns:
                data = self.object[col]
            else:
                data = self.object.index
            kind = data.dtype.kind
            if kind == 'i':
                formatter = NumberFormatter()
                editor = IntEditor()
            elif kind == 'b':
                formatter = BooleanFormatter()
                editor = CheckboxEditor()
            elif kind == 'f':
                formatter = NumberFormatter(format='0,0.0[00000]')
                editor = NumberEditor()
            elif isdatetime(data):
                dformat = Dimension.type_formatters.get(dimtype, '%Y-%m-%d %H:%M:%S')
                formatter = DateFormatter(format=dformat)
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
        if self.interactive:
            data = {k if isinstance(k, str) else str(k): v
                    for k, v in ColumnDataSource.from_df(self.object).items()}
            props['source'] = ColumnDataSource(data=data)
            props['columns'] = self._get_columns()
            props['index_position'] = None
            props['editable'] = self.editable
        else:
            props['text'] = self.object.to_html(classes=['panel-df']).replace('border="1"', '')
            if self.sizing_mode not in ['fixed', None]:
                props['style'] = dict(width='100%', height='100%')
        return props

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model(**self._get_properties())
        if self.interactive:
            self._link_props(model.source, ['data', ('patching', 'data')], doc, root, comm)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_events(self, events):
        if 'data' in events:
            for k, v in events['data'].items():
                if k == 'index':
                    continue
                k = self._renamed_cols.get(k, k)
                self.object[k] = v
