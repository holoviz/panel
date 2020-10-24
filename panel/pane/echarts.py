from __future__ import absolute_import, division, unicode_literals

import sys
import json

import param

from pyviz_comms import JupyterComm

from ..viewable import Layoutable
from .base import PaneBase



class ECharts(PaneBase):
    """
    ECharts panes allow rendering echarts.js plots.
    """
    object = param.Parameter(default=None, doc="""
        The Echarts object being wrapped. Can be an Echarts dictionary or a pyecharts chart""")

    renderer = param.ObjectSelector(default="canvas", objects=["canvas", "svg"], doc="""
       Whether to render as HTML canvas or SVG""")

    theme = param.ObjectSelector(default="default", objects=["default", "light", "dark"], doc="""
       Theme to apply to plots.""")

    priority = 0

    _rename = {"object": "data"}

    _rerender_params = []

    _updates = True

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, dict) or "pyecharts." in repr(obj.__class__)

    @classmethod
    def _get_dimensions(cls, json, props):
        if json is None:
            return
        responsive = json.get('responsive')
        if responsive:
            props['sizing_mode'] = 'stretch_both'
        else:
            props['sizing_mode'] = 'fixed'

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if 'panel.models.echarts' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('EChart was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'echart\')\n')
            from ..models.echarts import ECharts
        else:
            ECharts = getattr(sys.modules['panel.models.echarts'], 'ECharts')

        props = self._process_param_change(self._init_properties())
        echart = self._get_echart_dict(self.object)
        self._get_dimensions(echart, props)
        model = ECharts(data=echart, **props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref=None, model=None):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        echart = self._get_echart_dict(self.object)
        self._get_dimensions(echart, props)
        props['data'] = echart
        model.update(**props)

    @classmethod
    def _get_echart_dict(cls, object):
        if object is None:
            return {}
        if isinstance(object, dict):
            return dict(object)
        if "pyecharts" in sys.modules:
            import pyecharts  # pylint: disable=import-outside-toplevel,import-error

            if isinstance(object, pyecharts.charts.chart.Chart):
                return json.loads(object.dump_options())

        return {}
