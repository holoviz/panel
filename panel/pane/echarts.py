from __future__ import annotations

import sys
import typing as t

from collections import defaultdict

import param

from bokeh.core.serialization import Serializer
from bokeh.models import CustomJS
from pyviz_comms import JupyterComm

from ..util import lazy_load
from ..viewable import Viewable
from .base import ModelPane

if t.TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class ECharts(ModelPane):
    """
    ECharts panes allow rendering echarts.js dictionaries and pyecharts plots.

    Reference: https://panel.holoviz.org/reference/panes/ECharts.html

    :Example:

    >>> pn.extension('echarts')
    >>> ECharts(some_echart_dict_or_pyecharts_object, height=480, width=640)
    """

    object = param.Parameter(default=None, doc="""
        The Echarts object being wrapped. Can be an Echarts dictionary or a pyecharts chart""")

    options: dict[str, t.Any] | None = param.Dict(default=None, doc="""
        An optional dict of options passed to Echarts.setOption. Allows to fine-tune the rendering behavior.
        For example, you might want to use `options={ "replaceMerge": ['series'] })` when updating
        the `objects` with a value containing a smaller number of series.
        """)  # type: ignore[assignment, ty:invalid-assignment]

    renderer: t.Literal["canvas", "svg"] = param.Selector(
        default="canvas", objects=["canvas", "svg"], doc="""
       Whether to render as HTML canvas or SVG""")  # type: ignore[assignment, ty:invalid-assignment]

    theme: t.Literal["default", "light", "dark"] = param.Selector(
        default="default", objects=["default", "light", "dark"], doc="""
       Theme to apply to plots.""")  # type: ignore[assignment, ty:invalid-assignment]

    priority: t.ClassVar[float | bool | None] = None

    _rename: t.ClassVar[Mapping[str, str | None]] = {"object": "data"}

    _rerender_params: t.ClassVar[list[str]] = []

    _updates: t.ClassVar[bool] = True

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._py_callbacks = defaultdict(lambda: defaultdict(list))
        self._js_callbacks = defaultdict(list)

    @classmethod
    def applies(cls, object: t.Any, **params) -> float | bool | None:
        if isinstance(object, dict):
            return 0
        elif cls.is_pyecharts(object):
            return 0.8
        return None

    @classmethod
    def is_pyecharts(cls, obj):
        if 'pyecharts' in sys.modules:
            import pyecharts
            return isinstance(obj, pyecharts.charts.chart.Chart)
        return False

    def _process_event(self, event):
        callbacks = self._py_callbacks.get(event.type, {})
        for cb in callbacks.get(None, []):
            cb(event)
        if event.query is None:
            return
        for cb in callbacks.get(event.query, []):
            cb(event)

    def _get_js_events(self, ref):
        js_events = defaultdict(list)
        for event, specs in self._js_callbacks.items():
            for (query, code, args) in specs:
                models = {
                    name: viewable._models[ref][0] for name, viewable in args.items()
                    if ref in viewable._models
                }
                js_events[event].append({'query': query, 'callback': CustomJS(code=code, args=models)})
        return dict(js_events)

    def _serialize(self, obj):
        if hasattr(obj, 'opts'):
            obj = obj.opts
        if isinstance(obj, dict):
            data = {k: self._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            data = [self._serialize(v) for v in obj]
        else:
            data = obj
        return data

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'data' not in props:
            return props
        data = props['data'] or {}
        if not isinstance(data, dict):
            w, h = data.width, data.height
            props['data'] = data = self._serialize(data.get_options())
            if not self.height and h:
                props['height'] = int(h.replace('px', ''))
            if not self.width and w:
                props['width'] = int(w.replace('px', ''))
        else:
            props['data'] = data
        if data.get('responsive'):
            props['sizing_mode'] = 'stretch_both'
        return props

    def _get_properties(self, doc: Document | None) -> dict[str, t.Any]:
        props = super()._get_properties(doc)
        props['event_config'] = {
            event: list(queries) for event, queries in self._py_callbacks.items()
        }
        return props

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if self.is_pyecharts(self.object):
            from pyecharts.commons.utils import JsCode
            try:
                Serializer.register(JsCode, lambda obj, __: obj.js_code)  # type: ignore
            except AssertionError:
                pass

        ECharts._bokeh_model = lazy_load(
            'panel.models.echarts', 'ECharts', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('echarts_event', model=model, doc=doc, comm=comm)
        return model

    def on_event(self, event: str, callback: Callable, query: str | None = None):
        """
        Register anevent handler which triggers when the specified event is triggered.

        Reference: https://apache.github.io/echarts-handbook/en/concepts/event/

        Parameters
        ----------
        event: str
            The name of the event to register a handler on, e.g. 'click'.
        callback: str | CustomJS
            The event handler to be executed when the event fires.
        query: str | None
            A query that determines when the event fires.
        """
        self._py_callbacks[event][query].append(callback)
        event_config = {event: list(queries) for event, queries in self._py_callbacks.items()}
        for ref, (model, _) in self._models.copy().items():
            self._apply_update({}, {'event_config': event_config}, model, ref)

    def js_on_event(self, event: str, callback: str | CustomJS, query: str | None = None, **args):
        """
        Register a Javascript event handler which triggers when the
        specified event is triggered. The callback can be a snippet
        of Javascript code or a bokeh CustomJS object making it possible
        to manipulate other models in response to an event.

        Reference: https://apache.github.io/echarts-handbook/en/concepts/event/

        Parameters
        ----------
        event: str
            The name of the event to register a handler on, e.g. 'click'.
        code: str
            The event handler to be executed when the event fires.
        query: str | None
            A query that determines when the event fires.
        args: Viewable
            A dictionary of Viewables to make available in the namespace
            of the object.
        """
        self._js_callbacks[event].append((query, callback, args))
        for ref, (model, _) in self._models.copy().items():
            js_events = self._get_js_events(ref)
            self._apply_update({}, {'js_events': js_events}, model, ref)


def setup_js_callbacks(root_view, root_model):
    if 'panel.models.echarts' not in sys.modules:
        return
    ref = root_model.ref['id']
    for pane in root_view.select(ECharts):
        if ref in pane._models:
            pane._models[ref][0].js_events = pane._get_js_events(ref)

Viewable._preprocessing_hooks.append(setup_js_callbacks)
