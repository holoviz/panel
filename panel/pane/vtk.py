# coding: utf-8
"""
Defines a PlotlyPane which renders a plotly plot using PlotlyPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

from ..models import VtkPlot
from .base import PaneBase


class Vtk(PaneBase):
    """
    Vtk panes allow rendering Vtk objects.

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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if self.object is None:
            json, sources = None, []
        else:
            fig = self._to_figure(self.object)
            json = fig.to_plotly_json()
            sources = self._get_sources(json)
        model = VtkPlot(data=json, data_sources=sources)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model
