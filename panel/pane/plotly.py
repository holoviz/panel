"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
import numpy as np
import param

from bokeh.models import ColumnDataSource, CustomJS, Tabs
from pyviz_comms import JupyterComm

from .base import PaneBase
from ..util import isdatetime, lazy_load
from ..viewable import Layoutable, Viewable



class Plotly(PaneBase):
    """
    Plotly panes allow rendering plotly Figures and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    click_data = param.Dict(doc="Click callback data")

    clickannotation_data = param.Dict(doc="Clickannotation callback data")

    config = param.Dict(doc="Config data")

    hover_data = param.Dict(doc="Hover callback data")

    relayout_data = param.Dict(doc="Relayout callback data")

    restyle_data = param.List(doc="Restyle callback data")

    selected_data = param.Dict(doc="Selected callback data")

    viewport = param.Dict(doc="Current viewport state")

    viewport_update_policy = param.Selector(default="mouseup", doc="""
        Policy by which the viewport parameter is updated during user interactions.

        * "mouseup": updates are synchronized when mouse button is
          released after panning
        * "continuous": updates are synchronized continually while panning
        * "throttle": updates are synchronized while panning, at 
          intervals determined by the viewport_update_throttle parameter
        """, objects=["mouseup", "continuous", "throttle"])

    viewport_update_throttle = param.Integer(default=200, bounds=(0, None), doc="""
        Time interval in milliseconds at which viewport updates are
        synchronized when viewport_update_policy is "throttle".""")

    _render_count = param.Integer(default=0, doc="""
        Number of renders, increment to trigger re-render""")

    priority = 0.8

    _updates = True

    @classmethod
    def applies(cls, obj):
        return ((isinstance(obj, list) and obj and all(cls.applies(o) for o in obj)) or
                hasattr(obj, 'to_plotly_json') or (isinstance(obj, dict)
                                                   and 'data' in obj and 'layout' in obj))

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._figure = None
        self._event = None
        self._update_figure()

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
            full_path = key if not parent_path else "{}.{}".format(parent_path, key)
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

    @param.depends('object', watch=True)
    def _update_figure(self):
        import plotly.graph_objs as go

        if (self.object is None or type(self.object) is not go.Figure or
            self.object is self._figure):
            return

        # Monkey patch the message stubs used by FigureWidget.
        # We only patch `Figure` objects (not subclasses like FigureWidget) so
        # we don't interfere with subclasses that override these methods.
        fig = self.object
        fig._send_addTraces_msg = lambda *_, **__: self._update_from_figure('add')
        fig._send_moveTraces_msg = lambda *_, **__: self._update_from_figure('move')
        fig._send_deleteTraces_msg = lambda *_, **__: self._update_from_figure('delete')
        fig._send_restyle_msg = self._send_restyle_msg
        fig._send_relayout_msg = self._send_relayout_msg
        fig._send_update_msg = self._send_update_msg
        fig._send_animate_msg = lambda *_, **__: self._update_from_figure('animate')
        self._figure = fig

    def _send_relayout_msg(self, relayout_data, source_view_id=None):
        self._send_update_msg({}, relayout_data, None, source_view_id)

    def _send_restyle_msg(self, restyle_data, trace_indexes=None, source_view_id=None):
        self._send_update_msg(restyle_data, {}, trace_indexes, source_view_id)

    @param.depends('restyle_data', watch=True)
    def _update_figure_style(self):
        if self._figure is None or self.restyle_data is None:
            return
        self._figure.plotly_restyle(*self.restyle_data)

    @param.depends('relayout_data', watch=True)
    def _update_figure_layout(self):
        if self._figure is None or self.relayout_data is None:
            return
        self._figure.plotly_relayout(self.relayout_data)

    def _send_update_msg(
        self, restyle_data, relayout_data, trace_indexes=None, source_view_id=None
    ):
        if source_view_id:
            return
        trace_indexes = self._figure._normalize_trace_indexes(trace_indexes)
        msg = {}
        if relayout_data:
            msg['relayout'] = relayout_data
        if restyle_data:
            msg['restyle'] = {'data': restyle_data, 'traces': trace_indexes}
        for ref, (m, _) in self._models.items():
            self._apply_update([], msg, m, ref)

    def _update_from_figure(self, event, *args, **kwargs):
        self._event = event
        try:
            self.param.trigger('object')
        finally:
            self._event = None

    def _update_data_sources(self, cds, trace):
        trace_arrays = {}
        Plotly._get_sources_for_trace(trace, trace_arrays)

        update_sources = False
        for key, new_col in trace_arrays.items():
            new = new_col[0]

            try:
                old = cds.data.get(key)[0]
                update_array = (
                    (type(old) != type(new)) or
                    (new.shape != old.shape) or
                    (new != old).any())
            except Exception:
                update_array = True

            if update_array:
                update_sources = True
                cds.data[key] = [new]

        return update_sources

    @staticmethod
    def _plotly_json_wrapper(fig):
        """Wraps around to_plotly_json and applies necessary fixes.

        For #382: Map datetime elements to strings.
        """
        json = fig.to_plotly_json()
        data = json['data']

        for idx in range(len(data)):
            for key in data[idx]:
                if isdatetime(data[idx][key]):
                    arr = data[idx][key]
                    if isinstance(arr, np.ndarray):
                        arr = arr.astype(str) 
                    else:
                        arr = [str(v) for v in arr]
                    data[idx][key] = arr
        return json

    def _init_params(self):
        viewport_params = [p for p in self.param if 'viewport' in p]
        parameters = list(Layoutable.param)+viewport_params
        params = {p: getattr(self, p) for p in parameters
                  if getattr(self, p) is not None}

        if self.object is None:
            json, sources = {}, []
        else:
            fig = self._to_figure(self.object)
            json = self._plotly_json_wrapper(fig)
            sources = Plotly._get_sources(json)

        params['_render_count'] = self._render_count
        params['config'] = self.config or {}
        params['data'] = json.get('data', [])
        params['data_sources'] = sources
        params['layout'] = layout = json.get('layout', {})
        if layout.get('autosize') and self.sizing_mode is self.param.sizing_mode.default:
            params['sizing_mode'] = 'stretch_both'
        return params

    def _get_model(self, doc, root=None, parent=None, comm=None):
        PlotlyPlot = lazy_load('panel.models.plotly', 'PlotlyPlot', isinstance(comm, JupyterComm))
        model = PlotlyPlot(**self._init_params())
        if root is None:
            root = model
        self._link_props(model, self._linkable_params, doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        if _patch_tabs_plotly not in Viewable._preprocessing_hooks:
            Viewable._preprocessing_hooks.append(_patch_tabs_plotly)
        return model

    def _update(self, ref=None, model=None):
        if self.object is None:
            model.update(data=[], layout={})
            model._render_count += 1
            return

        fig = self._to_figure(self.object)
        json = self._plotly_json_wrapper(fig)
        layout = json.get('layout')

        traces = json['data']
        new_sources = []
        update_sources = False
        for i, trace in enumerate(traces):
            if i < len(model.data_sources):
                cds = model.data_sources[i]
            else:
                cds = ColumnDataSource()
                new_sources.append(cds)

            update_sources = self._update_data_sources(cds, trace) or update_sources

        try:
            update_layout = model.layout != layout
        except Exception:
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
                        {k: v for k, v in old.items() if k != 'uid'}
                    )
                except Exception:
                    update_data = True
                if update_data:
                    break

        updates = {}
        if self.sizing_mode is self.param.sizing_mode.default and 'autosize' in layout:
            autosize = layout.get('autosize')
            if autosize and model.sizing_mode != 'stretch_both':
                updates['sizing_mode'] = 'stretch_both'
            elif not autosize and model.sizing_mode != 'fixed':
                updates['sizing_mode'] = 'fixed'

        if new_sources:
            updates['data_sources'] = model.data_sources + new_sources

        if update_data:
            updates['data'] = json.get('data')

        if update_layout:
            updates['layout'] = layout

        if updates:
            model.update(**updates)

        # Check if we should trigger rendering
        if updates or update_sources:
            model._render_count += 1


def _patch_tabs_plotly(viewable, root):
    """
    A preprocessing hook which ensures that any Plotly panes rendered
    inside Tabs are only visible when the tab they are in is active.
    This is a workaround for https://github.com/holoviz/panel/issues/804.
    """
    from ..models.plotly import PlotlyPlot

    # Clear args on old callback so references aren't picked up
    old_callbacks = {}
    for tmodel in root.select({'type': Tabs}):
        old_callbacks[tmodel] = {
            k: [cb for cb in cbs] for k, cbs in tmodel.js_property_callbacks.items()
        }
        for cb in tmodel.js_property_callbacks.get('change:active', []):
            if any(tag.startswith('plotly_tab_fix') for tag in cb.tags):
                # Have to unset owners so property is not notified
                owners = cb.args._owners
                cb.args._owners = set()
                cb.args.clear()
                cb.args._owners = owners

    tabs_models = list(root.select({'type': Tabs}))
    plotly_models = list(root.select({'type': PlotlyPlot}))

    tab_callbacks = {}
    for model in plotly_models:
        parent_tabs = [tmodel for tmodel in tabs_models if tmodel.select_one({'id': model.id})]
        active = True
        args = {'model': model}
        tag = f'plotly_tab_fix{model.id}'

        # Generate condition that determines whether tab containing
        # the plot is active
        condition = ''
        for tabs in list(parent_tabs):
            # Find tab that contains plot
            found = False
            for i, tab in enumerate(tabs.tabs):
                if tab.select_one({'id': model.id}):
                    found = True
                    break
            if not found:
                parent_tabs.remove(tabs)
                continue
            if condition:
                condition += ' && '
            condition += f"(tabs_{tabs.id}.active == {i})"
            args.update({f'tabs_{tabs.id}': tabs})
            active &= tabs.active == i

        model.visible = active
        code = f'model.visible = {condition};'
        for tabs in parent_tabs:
            tab_key = f'tabs_{tabs.id}'
            cb_args = dict(args)
            cb_code = code.replace(tab_key, 'cb_obj')
            cb_args.pop(tab_key)
            callback = CustomJS(args=cb_args, code=cb_code, tags=[tag])
            if tabs not in tab_callbacks:
                tab_callbacks[tabs] = []
            tab_callbacks[tabs].append(callback)

    for tabs, callbacks in tab_callbacks.items():
        new_cbs = []
        for cb in callbacks:
            found = False
            for old_cb in tabs.js_property_callbacks.get('change:active', []):
                if cb.tags[0] in old_cb.tags:
                    found = True
                    old_cb.update(code=cb.code)
                    # Reapply args without notifying property system
                    owners = old_cb.args._owners
                    old_cb.args._owners = set()
                    old_cb.args.update(cb.args)
                    old_cb.args._owners = owners
            if not found:
                new_cbs.append(cb)
        if new_cbs:
            tabs.js_on_change('active', *new_cbs)
