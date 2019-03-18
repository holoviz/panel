"""
Defines custom bokeh models to render external Javascript based plots. 
"""
import os

from bokeh.core.properties import Dict, String, List, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from ..compiler import CUSTOM_MODELS


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plotly.ts')

    data = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))


class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vega.ts')

    data = Dict(String, Any)

    data_sources = Dict(String, Instance(ColumnDataSource))


CUSTOM_MODELS['panel.models.plots.PlotlyPlot'] = PlotlyPlot
CUSTOM_MODELS['panel.models.plots.VegaPlot'] = VegaPlot
