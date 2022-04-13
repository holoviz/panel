import sys
import json

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import PaneBase


class ECharts(PaneBase):
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

    priority = None

    _rename = {"object": "data"}

    _rerender_params = []

    _updates = True

    @classmethod
    def applies(cls, obj, **params):
        if isinstance(obj, dict):
            return 0
        elif "pyecharts." in repr(obj.__class__):
            return 0.8
        return None

    @classmethod
    def _get_dimensions(cls, props):
        if json is None:
            return
        responsive = props.get('data', {}).get('responsive')
        if responsive:
            props['sizing_mode'] = 'stretch_both'
        else:
            props['sizing_mode'] = 'fixed'

    def _get_model(self, doc, root=None, parent=None, comm=None):
        ECharts = lazy_load('panel.models.echarts', 'ECharts', isinstance(comm, JupyterComm), root)
        props = self._get_echart_dict(self.object)
        props.update(self._process_param_change(self._init_params()))
        self._get_dimensions(props)
        model = ECharts(**props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'data' in msg:
            msg.update(self._get_echart_dict(msg['data']))
        return msg

    def _get_echart_dict(self, object):
        if isinstance(object, dict):
            return {'data': dict(object)}
        elif "pyecharts" in sys.modules:
            import pyecharts  # pylint: disable=import-outside-toplevel,import-error
            if isinstance(object, pyecharts.charts.chart.Chart):
                w, h = object.width, object.height
                params = {'data': json.loads(object.dump_options())}
                if not self.height and h:
                    params['height'] = int(h.replace('px', ''))
                if not self.width and w:
                    params['width'] = int(w.replace('px', ''))
                return params
        return {}
