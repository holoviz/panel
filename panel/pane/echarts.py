from __future__ import absolute_import, division, unicode_literals

import sys

import param

from pyviz_comms import JupyterComm

from ..viewable import Layoutable
from .base import PaneBase


class ECharts(PaneBase):
    """
    ECharts panes allow rendering echarts.js plots.
    """

    renderer = param.ObjectSelector(default="canvas", objects=["canvas", "svg"], doc="""
       Whether to render as HTML canvas or SVG""")

    theme = param.ObjectSelector(default="default", objects=["default", "light", "dark"], doc="""
       Theme to apply to plots.""")

    priority = 0

    _rename = {"object": "data"}

    _rerender_params = []

    _updates = True

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, dict)

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
        self._get_dimensions(self.object, props)
        data = {} if self.object is None else dict(self.object)
        model = ECharts(data=data, **props)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref=None, model=None):
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        self._get_dimensions(self.object, props)
        props['data'] = {} if self.object else dict(self.object)
        model.update(**props)
