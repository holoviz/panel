from __future__ import absolute_import, division, unicode_literals

import sys

import param
import numpy as np

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from .base import PaneBase


def ds_as_cds(dataset):
    """
    Converts Vega dataset into Bokeh ColumnDataSource data
    """
    if len(dataset) == 0:
        return {}
    data = {k: [] for k, v in dataset[0].items()}
    for item in dataset:
        for k, v in item.items():
            data[k].append(v)
    data = {k: np.asarray(v) for k, v in data.items()}
    return data


class Vega(PaneBase):
    """
    Vega panes allow rendering Vega plots and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    margin = param.Parameter(default=(5, 5, 30, 5), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    priority = 0.8

    _updates = True

    @classmethod
    def is_altair(cls, obj):
        if 'altair' in sys.modules:
            import altair as alt
            return isinstance(obj, alt.api.TopLevelMixin)
        return False

    @classmethod
    def applies(cls, obj):
        if isinstance(obj, dict) and 'vega' in obj.get('$schema', '').lower():
            return True
        return cls.is_altair(obj)

    @classmethod
    def _to_json(cls, obj):
        if isinstance(obj, dict):
            json = dict(obj)
            if 'data' in json:
                json['data'] = dict(json['data'])
            return json
        return obj.to_dict()

    def _get_sources(self, json, sources):
        for name, data in json.pop('datasets', {}).items():
            if name in sources:
                continue
            columns = set(data[0]) if data else []
            if self.is_altair(self.object):
                import altair as alt
                if (not isinstance(self.object.data, alt.Data) and
                    columns == set(self.object.data)):
                    data = ColumnDataSource.from_df(self.object.data)
                else:
                    data = ds_as_cds(data)
                sources[name] = ColumnDataSource(data=data)
            else:
                sources[name] = ColumnDataSource(data=ds_as_cds(data))
        data = json.get('data', {}).pop('values', {})
        if data:
            sources['data'] = ColumnDataSource(data=ds_as_cds(data))

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if 'panel.models.vega' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('VegaPlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'vega\')\n')
            from ..models.vega import VegaPlot
        else:
            VegaPlot = getattr(sys.modules['panel.models.vega'], 'VegaPlot')

        sources = {}
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, sources)
        props = self._process_param_change(self._init_properties())
        model = VegaPlot(data=json, data_sources=sources, **props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, model.data_sources)
        model.data = json
