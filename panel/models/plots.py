"""
Defines custom bokeh models to render external Javascript based plots.
"""
import os

from bokeh.core.properties import Dict, String, List, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from ..util import CUSTOM_MODELS


class VtkPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vtk.ts')

    data = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))


CUSTOM_MODELS['panel.models.plots.VtkPlot'] = VtkPlot
