"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import numpy as np

from bokeh.models import ColumnDataSource

from ..models import PlotlyPlot
from .base import PaneBase


class Plotly(PaneBase):
    """
    Plotly panes allow rendering plotly Figures and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    _updates = True

    priority = 0.8

    @classmethod
    def applies(cls, obj):
        return ((isinstance(obj, list) and obj and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json') or (isinstance(obj, dict)
                                                   and 'data' in obj and 'layout' in obj))

    def _to_figure(self, obj):
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure):
            return obj
        elif isinstance(obj, dict):
            data, layout = obj['data'], obj['layout']
        elif isinstance(obj, tuple):
            data, layout = obj
        else:
            data, layout = obj, {}
        data = data if isinstance(data, list) else [data]
        return go.Figure(data=data, layout=layout)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        fig = self._to_figure(self.object)
        json = fig.to_plotly_json()
        traces = json['data']
        sources = []
        for trace in traces:
            data = {}
            for key, value in list(trace.items()):
                if isinstance(value, np.ndarray):
                    data[key] = trace.pop(key)
            sources.append(ColumnDataSource(data))
        model = PlotlyPlot(data=json, data_sources=sources)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        fig = self._to_figure(self.object)
        json = fig.to_plotly_json()
        traces = json['data']
        new_sources = []
        for i, trace in enumerate(traces):
            if i < len(model.data_sources):
                cds = model.data_sources[i]
            else:
                cds = ColumnDataSource()
                new_sources.append(cds)
            data = {}
            for key, value in list(trace.items()):
                if isinstance(value, np.ndarray):
                    data[key] = trace.pop(key)
            cds.data = data
        model.data = json
        if new_sources:
            model.data_sources += new_sources
