from __future__ import division, absolute_import

import os

import param
import numpy as np
from bokeh.core.properties import Dict, String, List, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from .pane import PaneBase
from .util import CUSTOM_MODELS


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __implementation__ = os.path.join(os.path.dirname(__file__), 'models', 'plotly.ts')

    data = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))


class Plotly(PaneBase):
    """
    Plotly panes allow rendering plotly Figures and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    plotly_layout = param.Dict()

    _updates = True

    precedence = 0.8

    def __init__(self, object, layout=None, **params):
        super(Plotly, self).__init__(self._to_figure(object, layout),
                                     plotly_layout=layout, **params)

    @classmethod
    def applies(cls, obj):
        return ((isinstance(obj, list) and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json'))

    def _to_figure(self, obj, layout={}):
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure):
            fig = obj
        else:
            data = obj if isinstance(obj, list) else [obj]
            fig = go.Figure(data=data, layout=layout)
        return fig

    def _get_model(self, doc, root, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        fig = self._to_figure(self.object, self.plotly_layout)
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
        self._models[root.ref['id']] = model
        self._link_object(doc, root, parent, comm)
        return model

    def _update(self, model):
        fig = self._to_figure(self.object, self.plotly_layout)
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


CUSTOM_MODELS['panel.plotly.PlotlyPlot'] = PlotlyPlot
