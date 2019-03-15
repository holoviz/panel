# coding: utf-8
"""
Defines a VtkPane which renders a vtk plot using VtkPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

from ..models import VtkPlot
from .base import PaneBase


class Vtk(PaneBase):
    """
    Vtk panes allow rendering Vtk objects.
    """

    _updates = True

    priority = 0.8

    @classmethod
    def applies(cls, obj):
        return hasattr(obj, 'vtkjs') or (isinstance(obj, dict)
                                         and 'vtkjs' in obj)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if self.object is None:
            vtkjs = None
        else:
            vtkjs = self.object.vtkjs
        model = VtkPlot(vtkjs=vtkjs)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        if self.object is None:
            vtkjs = None
        else:
            vtkjs = self.object.vtkjs
        model.vtkjs = vtkjs
