"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

import numpy as np

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

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

    def _get_sources(self, json):
        sources = []
        traces = json['data']
        for trace in traces:
            data = {}
            for key, value in list(trace.items()):
                if isinstance(value, np.ndarray):
                    data[key] = [trace.pop(key)]
            sources.append(ColumnDataSource(data))
        return sources

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if 'panel.models.plotly' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('PlotlyPlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'plotly\')\n')
            from ..models.plotly import PlotlyPlot
        else:
            PlotlyPlot = getattr(sys.modules['panel.models.plotly'], 'PlotlyPlot')

        if self.object is None:
            json, sources = {}, []
        else:
            fig = self._to_figure(self.object)
            json = fig.to_plotly_json()
            sources = self._get_sources(json)
        model = PlotlyPlot(data=json.get('data', []), layout=json.get('layout', {}),
                           data_sources=sources)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        if self.object is None:
            model.update(data=[], layout={})
            return


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
            for key, new in list(trace.items()):
                if isinstance(new, np.ndarray):
                    try:
                        old = cds.data.get(key)[0]
                        update_array = (
                            (type(old) != type(new)) or
                            (new.shape != old.shape) or
                            (new != old).all())
                    except:
                        update_array = True
                    if update_array:
                        cds.data[key] = [trace.pop(key)]

        try:
            update_layout = model.layout != json.get('layout')
        except:
            update_layout = True

        # Determine if model needs updates
        if (len(model.data) != len(traces)):
            update_data = True
        else:
            update_data = False
            for new, old in zip(traces, model.data):
                try:
                    update_data = (
                        {k: v for k, v in new.items() if k != 'uid'} !=
                        {k: v for k, v in old.items() if k != 'uid'})
                except:
                    update_data = True
                if update_data:
                    break

        if new_sources:
            model.data_sources += new_sources

        if update_data:
            model.data = json.get('data')

        if update_layout:
            model.layout = json.get('layout')
