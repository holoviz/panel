from __future__ import annotations

import datetime as dt
import sys

from typing import (
    TYPE_CHECKING, ClassVar, List, Optional,
)

import numpy as np
import param

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..reactive import SyncableData
from ..util import lazy_load
from .base import PaneBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Vizzu(PaneBase, SyncableData):
    """
    The `Vizzu` pane provides an interactive visualization component for
    large, real-time datasets built on the Vizzu project.

    Reference: https://panel.holoviz.org/reference/panes/Vizzu.html

    :Example:

    >>> Vizzu(df)
    """

    config = param.Dict(default={})

    columns = param.List(default=[])

    duration = param.Integer(default=500)

    style = param.Dict()

    _data_params: ClassVar[List[str]] = ['object']

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

    def _get_data(self):
        if self.object is None:
            return {}, {}
        if isinstance(self.object, dict):
            data = self.object
        else:
            data = {col: self.object[col].values for col in self.object.columns}
        return data, {str(k): v for k, v in data.items()}

    def _init_params(self):
        props = super()._init_params()
        props['duration'] = self.duration
        props['source'] = ColumnDataSource(data=self._data)
        props['columns'] = columns = self.columns
        if columns:
            return props
        for col, array in self._data.items():
            if not isinstance(array, np.ndarray):
                array = np.asarray(array)
            kind = array.dtype.kind
            if kind == 'M':
                columns.append({'name': col, 'type': 'datetime'})
            elif kind in 'uif':
                columns.append({'name': col, 'type': 'measure'})
            elif kind in 'bsU':
                columns.append({'name': col, 'type': 'dimension'})
            else:
                if len(array):
                    value = array[0]
                    print(value)
                    if isinstance(value, dt.date):
                        columns.append({'name': col, 'type': 'date'})
                    elif isinstance(value, dt.datetime):
                        columns.append({'name': col, 'type': 'datetime'})
                    elif isinstance(value, str):
                        columns.append({'name': col, 'type': 'measure'})
                    elif isinstance(value, (float, np.float, int, np.int)):
                        columns.append({'name': col, 'type': 'measure'})
                    else:
                        columns.append({'name': col, 'type': 'dimension'})
                else:
                    columns.append({'name': col, 'type': 'dimension'})
        return props

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        VizzuChart = lazy_load('panel.models.vizzu', 'VizzuChart', isinstance(comm, JupyterComm), root)
        properties = self._process_param_change(self._init_params())
        model = VizzuChart(**properties)
        if root is None:
            root = model
        synced = list(set([p for p in self.param if (self.param[p].precedence or 0) > -1]) ^ (set(PaneBase.param) | set(SyncableData.param)))
        self._link_props(model, synced, doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref: str, model: Model) -> None:
        pass
