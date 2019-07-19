"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

import numpy as np

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm
import param

from .base import PaneBase


class Plotly(PaneBase):
    """
    Plotly panes allow rendering plotly Figures and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    config = param.Dict(doc="""config data""")
    relayout_data = param.Dict(doc="""relayout callback data""")
    restyle_data = param.List(doc="""restyle callback data""")
    click_data = param.Dict(doc="""click callback data""")
    hover_data = param.Dict(doc="""hover callback data""")
    clickannotation_data = param.Dict(doc="""clickannotation callback data""")
    selected_data = param.Dict(doc="""selected callback data""")

    _py2js_addTraces = param.Dict(doc="""addTraces message data""")
    _py2js_restyle = param.Dict(doc="""restule message data""")
    _py2js_relayout = param.Dict(doc="""relayout message data""")
    _py2js_update = param.Dict(doc="""update message data""")
    _py2js_animate = param.Dict(doc="""animate message data""")
    _py2js_deleteTraces = param.Dict(doc="""deleteTraces message data""")
    _py2js_moveTraces = param.Dict(doc="""moveTraces message data""")

    _updates = True

    priority = 0.8

    @classmethod
    def applies(cls, obj):
        return ((isinstance(obj, list) and obj and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json') or (isinstance(obj, dict)
                                                   and 'data' in obj and 'layout' in obj))

    def __init__(self, object=None, **params):
        import plotly.graph_objs as go
        super(Plotly, self).__init__(object, **params)

        if type(object) is go.Figure:

            # Monkey patch the message stubs used by FigureWidget.
            # We only patch `Figure` objects (not subclasses like FigureWidget) so
            # we don't interfere with subclasses that override these methods.
            fig = object
            fig._send_addTraces_msg = self._send_addTraces_msg
            fig._send_moveTraces_msg = self._send_moveTraces_msg
            fig._send_deleteTraces_msg = self._send_deleteTraces_msg
            fig._send_restyle_msg = self._send_restyle_msg
            fig._send_relayout_msg = self._send_relayout_msg
            fig._send_update_msg = self._send_update_msg
            fig._send_animate_msg = self._send_animate_msg

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

    @staticmethod
    def _get_sources(json):
        sources = []
        traces = json.get('data', [])
        for trace in traces:
            data = {}
            Plotly._get_sources_for_trace(trace, data)
            sources.append(ColumnDataSource(data))
        return sources

    @staticmethod
    def _get_sources_for_trace(json, data, parent_path=''):
        for key, value in list(json.items()):
            full_path = key if not parent_path else (parent_path + '.' + key)
            if isinstance(value, np.ndarray):
                # Extract numpy array
                data[full_path] = [json.pop(key)]
            elif isinstance(value, dict):
                # Recurse into dictionaries:
                Plotly._get_sources_for_trace(value, data=data, parent_path=full_path)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # recurse into object arrays:
                for i, element in enumerate(value):
                    element_path = full_path + '.' + str(i)
                    Plotly._get_sources_for_trace(
                        element, data=data, parent_path=element_path
                    )

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
            sources = Plotly._get_sources(json)
        model = PlotlyPlot(data=json.get('data', []),
                           layout=json.get('layout', {}),
                           config=self.config,
                           data_sources=sources)

        if root is None:
            root = model

        self._link_props(
            model, [
                'config', 'relayout_data', 'restyle_data', 'click_data',  'hover_data',
                'clickannotation_data', 'selected_data',
                '_py2js_addTraces',
                '_py2js_restyle',
                '_py2js_relayout',
                '_py2js_update',
                '_py2js_animate',
                '_py2js_deleteTraces',
                '_py2js_moveTraces',
            ],
            doc,
            root,
            comm
        )

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

    def _send_addTraces_msg(self, new_traces_data):
        add_traces_msg = {"trace_data": new_traces_data}
        self._py2js_addTraces = add_traces_msg
        self._py2js_addTraces = None

    def _send_moveTraces_msg(self, current_inds, new_inds):
        move_msg = {"current_trace_inds": current_inds, "new_trace_inds": new_inds}
        self._py2js_moveTraces = move_msg
        self._py2js_moveTraces = None

    def _send_deleteTraces_msg(self, delete_inds):
        delete_msg = {"delete_inds": delete_inds}
        self._py2js_deleteTraces = delete_msg
        self._py2js_deleteTraces = None

    def _send_restyle_msg(self, restyle_data, trace_indexes=None, **_):
        restyle_msg = {
            "restyle_data": restyle_data,
            "restyle_traces": trace_indexes,
        }

        self._py2js_restyle = restyle_msg
        self._py2js_restyle = None

    def _send_relayout_msg(self, layout_data, **_):
        msg_data = {"relayout_data": layout_data}

        self._py2js_relayout = msg_data
        self._py2js_relayout = None

    def _send_update_msg(self, restyle_data, relayout_data, trace_indexes=None, **_):
        update_msg = {
            "style_data": restyle_data,
            "layout_data": relayout_data,
            "style_traces": trace_indexes,
        }

        self._py2js_update = update_msg
        self._py2js_update = None

    def _send_animate_msg(
        self, styles_data, relayout_data, trace_indexes, animation_opts
    ):
        animate_msg = {
            "style_data": styles_data,
            "layout_data": relayout_data,
            "style_traces": trace_indexes,
            "animation_opts": animation_opts,
        }

        self._py2js_animate = animate_msg
        self._py2js_animate = None
