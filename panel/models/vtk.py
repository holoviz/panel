# coding: utf-8
"""
Defines custom VtkPlot bokeh model to render Vtk objects.
"""
import os

from bokeh.core.properties import String, Bool
from bokeh.models import LayoutDOM

from ..util import CUSTOM_MODELS


class VtkPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """
    __javascript__ = ["https://unpkg.com/vtk.js@8.3.15/dist/vtk.js"]

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vtk.ts')

    vtkjs = String
    append = Bool(default=False)


CUSTOM_MODELS['panel.models.plots.VtkPlot'] = VtkPlot
