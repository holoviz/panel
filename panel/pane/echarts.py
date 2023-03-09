from __future__ import annotations

import json
import sys

from typing import (
    TYPE_CHECKING, Any, ClassVar, List, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import ModelPane

if TYPE_CHECKING:
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

    renderer = param.ObjectSelector(default="canvas", objects=["canvas", "svg"], doc="""
       Whether to render as HTML canvas or SVG""")

    theme = param.ObjectSelector(default="default", objects=["default", "light", "dark"], doc="""
       Theme to apply to plots.""")

    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {"object": "data"}

    _rerender_params: ClassVar[List[str]] = []

    _updates: ClassVar[bool] = True

    @classmethod
    def applies(cls, obj: Any, **params) -> float | bool | None:
        if isinstance(obj, dict):
            return 0
        elif cls.is_pyecharts(obj):
            return 0.8
        return None

    @classmethod
    def is_pyecharts(cls, obj):
        if 'pyecharts' in sys.modules:
            import pyecharts
            return isinstance(obj, pyecharts.charts.chart.Chart)
        return False

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        self._bokeh_model = lazy_load(
            'panel.models.echarts', 'ECharts', isinstance(comm, JupyterComm), root
        )
        return super()._get_model(doc, root, parent, comm)

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'data' not in props:
            return props
        data = props['data'] or {}
        if not isinstance(data, dict):
            w, h = data.width, data.height
            props['data'] = data = json.loads(data.dump_options())
            if not self.height and h:
                props['height'] = int(h.replace('px', ''))
            if not self.width and w:
                props['width'] = int(w.replace('px', ''))
        else:
            props['data'] = data
        if data.get('responsive'):
            props['sizing_mode'] = 'stretch_both'
        return props
