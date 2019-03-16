# coding: utf-8
"""
Defines custom VTKPlot bokeh model to render VTK objects.
"""
import os

from bokeh.core.properties import String, Bool
from bokeh.models import HTMLBox

from ..util import CUSTOM_MODELS


class VTKPlot(HTMLBox):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """

    __javascript__ = ["https://unpkg.com/vtk.js@8.3.15/dist/vtk.js"]

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vtk.ts')

    vtkjs = String

    append = Bool(default=False)


CUSTOM_MODELS['panel.models.plots.VTKPlot'] = VTKPlot
