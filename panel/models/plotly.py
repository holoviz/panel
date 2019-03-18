"""
Defines a custom PlotlyPlot bokeh model to render Plotly plots. 
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

    __javascript__ = ['https://cdn.plot.ly/plotly-latest.min.js']

    __js_require__ = {'paths': {'plotly': 'https://cdn.plot.ly/plotly-latest.min'},
                      'exports': {'plotly': 'Plotly'}}

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plotly.ts')

    data = List(Any)

    layout = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))


CUSTOM_MODELS['panel.models.plotly.PlotlyPlot'] = PlotlyPlot
