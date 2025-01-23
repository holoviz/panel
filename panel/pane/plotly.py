"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
import param

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..util import lazy_load
from ..util.checks import datetime_types, isdatetime
from ..viewable import Layoutable
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Plotly(ModelPane):
    """
    The `Plotly` pane renders Plotly plots inside a panel.

    Note that

    - the Panel `extension` has to be loaded with `plotly` as an argument to
    ensure that Plotly.js is initialized.
    - it supports click, hover and selection events.
    - it optimizes the plot rendering by using binary serialization for any
    array data found on the Plotly object.

    Reference: https://panel.holoviz.org/reference/panes/Plotly.html

    :Example:

    >>> pn.extension('plotly')
    >>> Plotly(some_plotly_figure, width=500, height=500)
    """

    click_data = param.Dict(doc="Click event data from `plotly_click` event.")

    doubleclick_data = param.Dict(doc="Click event data from `plotly_doubleclick` event.")

    clickannotation_data = param.Dict(doc="Clickannotation event data from `plotly_clickannotation` event.")

    config = param.Dict(nested_refs=True, doc="""
        Plotly configuration options. See https://plotly.com/javascript/configuration-options/""")

    hover_data = param.Dict(doc="Hover event data from `plotly_hover` and `plotly_unhover` events.")

    link_figure = param.Boolean(default=True, doc="""
       Attach callbacks to the Plotly figure to update output when it
       is modified in place.""")

    relayout_data = param.Dict(nested_refs=True, doc="Relayout event data from `plotly_relayout` event")

    restyle_data = param.List(nested_refs=True, doc="Restyle event data from `plotly_restyle` event")

    selected_data = param.Dict(nested_refs=True, doc="Selected event data from `plotly_selected` and `plotly_deselect` events.")

    viewport = param.Dict(nested_refs=True, doc="""Current viewport state, i.e. the x- and y-axis limits of the displayed plot.
                          Updated on `plotly_relayout`, `plotly_relayouting` and `plotly_restyle` events.""")

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

    priority: ClassVar[float | bool | None] = 0.8

    _updates: ClassVar[bool] = True

    _rename: ClassVar[Mapping[str, str | None]] = {
        'link_figure': None,
        'object': None,
        'doubleclick_data': None,
        'click_data': None,
        'clickannotation_data': None,
        'hover_data': None,
        'selected_data': None
    }

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
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
        if isinstance(obj, (go.Figure, go.FigureWidget)):
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
            full_path = key if not parent_path else f"{parent_path}.{key}"
            if isinstance(value, np.ndarray):
                array = json.pop(key)
                data[full_path] = [array]
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

    @param.depends('object', 'link_figure', watch=True)
    def _update_figure(self):
        import plotly.graph_objs as go

        if (self.object is None or type(self.object) not in (go.Figure, go.FigureWidget) or
            self.object is self._figure or not self.link_figure):
            return

        # Monkey patch the message stubs used by FigureWidget.
        fig = self.object
        fig._send_addTraces_msg = lambda *_, **__: self._update_from_figure('add')
        fig._send_deleteTraces_msg = lambda *_, **__: self._update_from_figure('delete')
        fig._send_moveTraces_msg = lambda *_, **__: self._update_from_figure('move')
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
        relayout_data = self._clean_relayout_data(self.relayout_data)
        # The _compound_array_props are sometimes not correctly reset
        # which means that they are desynchronized with _props causing
        # incorrect lookups and potential errors when updating a property
        self._figure.layout._compound_array_props.clear()
        self._figure.plotly_relayout(relayout_data)

    @staticmethod
    def _clean_relayout_data(relayout_data):
        return {
            key: val for key, val in relayout_data.items() if not key.endswith("._derived")
        }

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
        for ref, (m, _) in self._models.copy().items():
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
                    (type(old) is not type(new)) or
                    (new.shape != old.shape) or
                    (new != old).any())
            except Exception:
                update_array = True

            if update_array:
                update_sources = True
                cds.data[key] = [new]

        for key in list(cds.data):
            if key not in trace_arrays:
                del cds.data[key]
                update_sources = True

        return update_sources

    @staticmethod
    def _plotly_json_wrapper(fig):
        """Wraps around to_plotly_json and applies necessary fixes.

        For #382: Map datetime elements to strings.
        """
        json = fig.to_plotly_json()
        layout = json['layout']
        data = json['data']
        shapes = layout.get('shapes', [])
        for trace in data+shapes:
            for key in trace:
                if not isdatetime(trace[key]):
                    continue
                arr = trace[key]
                if isinstance(arr, np.ndarray):
                    arr = arr.astype(str)
                elif isinstance(arr, datetime_types):
                    arr = str(arr)
                else:
                    arr = [str(v) for v in arr]
                trace[key] = arr
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
        params['frames'] = json.get('frames', [])
        if layout.get('autosize') and self.sizing_mode is self.param.sizing_mode.default:
            params['sizing_mode'] = 'stretch_both'
            if 'styles' not in params:
                params['styles'] = {}
        return params

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'layout' in props or 'stylesheets' in props:
            if 'layout' in props:
                layout = props['layout']
            elif self._models:
                # Improve lookup of current layout
                layout = list(self._models.values())[0][0].layout
            else:
                return props
            btn_color = layout.get('template', {}).get('layout', {}).get('font', {}).get('color', 'black')
            props['stylesheets'] = props.get('stylesheets', []) + [
                f':host {{ --plotly-icon-color: gray; --plotly-active-icon-color: {btn_color}; }}'
            ]
        return props

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        Plotly._bokeh_model = lazy_load(
            'panel.models.plotly', 'PlotlyPlot', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('plotly_event', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event):
        etype = event.data['type']
        data = event.data['data']
        pname = f'{etype}_data'
        if getattr(self, pname) == data:
            self.param.trigger(pname)
        else:
            self.param.update(**{pname: data})

        if data is None or not hasattr(self.object, '_handler_js2py_pointsCallback'):
            return

        points = data['points']
        num_points = len(points)

        has_nested_point_objects = True
        for point_obj in points:
            has_nested_point_objects = has_nested_point_objects and 'pointNumbers' in point_obj
            if not has_nested_point_objects:
                break

        num_point_numbers = num_points
        if has_nested_point_objects:
            num_point_numbers = 0
            for point_obj in points:
                num_point_numbers += len(point_obj['pointNumbers'])

        points_object = {
            'trace_indexes': [],
            'point_indexes': [],
            'xs': [],
            'ys': [],
        }

        # Add z if present
        has_z = points[0] is not None and 'z' in points[0]
        if has_z:
            points_object['zs'] = []

        if has_nested_point_objects:
            for point_obj in points:
                for i in range(len(point_obj['pointNumbers'])):
                    points_object['point_indexes'].append(point_obj['pointNumbers'][i])
                    points_object['xs'].append(point_obj['x'])
                    points_object['ys'].append(point_obj['y'])
                    points_object['trace_indexes'].append(point_obj['curveNumber'])
                    if has_z and 'z' in point_obj:
                        points_object['zs'].append(point_obj['z'])

            single_trace = True
            for i in range(1, num_point_numbers):
                single_trace = single_trace and (points_object['trace_indexes'][i - 1] == points_object['trace_indexes'][i])
                if not single_trace:
                    break

            if single_trace:
                points_object['point_indexes'].sort()
        else:
            for point_obj in points:
                points_object['trace_indexes'].append(point_obj['curveNumber'])
                points_object['point_indexes'].append(point_obj['pointNumber'])
                points_object['xs'].append(point_obj['x'])
                points_object['ys'].append(point_obj['y'])
                if has_z and 'z' in point_obj:
                    points_object['zs'].append(point_obj['z'])

        self._figure._handler_js2py_pointsCallback(
            {
                "new": dict(
                    event_type=f'plotly_{etype}',
                    points=points_object,
                    selector=data.get('selector', None),
                    device_state=data.get('device_state', None)
                )
            }
        )

    def _update(self, ref: str, model: Model) -> None:
        if self.object is None:
            model.update(data=[], layout={})
            model._render_count += 1
            return

        fig = self._to_figure(self.object)
        json = self._plotly_json_wrapper(fig)
        layout = json.get('layout')
        frames = json.get('frames')

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

        # Determine if layout needs update
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

        # Determine if frames needs update
        try:
            update_frames = model.frames != frames
        except Exception:
            update_frames = True

        updates: dict[str, Any] = {}
        if self.sizing_mode is self.param.sizing_mode.default and 'autosize' in layout:
            autosize = layout.get('autosize')
            styles = dict(model.styles)
            if autosize and model.sizing_mode != 'stretch_both':
                updates['sizing_mode'] = 'stretch_both'
                styles['display'] = 'contents'
            elif not autosize and model.sizing_mode != 'fixed':
                updates['sizing_mode'] = 'fixed'
                if 'display' in styles:
                    del styles['display']

        if new_sources:
            updates['data_sources'] = model.data_sources + new_sources

        if update_data:
            updates['data'] = json.get('data')

        if update_layout:
            updates['layout'] = layout

        if update_frames:
            updates['frames'] = frames or []

        if updates:
            model.update(**updates)

        # Check if we should trigger rendering
        if updates or update_sources:
            model._render_count += 1
