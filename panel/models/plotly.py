"""
Defines a custom PlotlyPlot bokeh model to render Plotly plots. 
"""
import os

from bokeh.core.properties import Dict, String, List, Any, Instance, Enum, Int
from bokeh.models import LayoutDOM, ColumnDataSource

from ..compiler import CUSTOM_MODELS


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __javascript__ = ['https://cdn.plot.ly/plotly-latest.min.js',
                      'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.min.js']

    __js_require__ = {'paths': {'plotly': 'https://cdn.plot.ly/plotly-latest.min',
                                'lodash': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.min'},
                      'exports': {'plotly': 'Plotly',
                                  'lodash': '_'}}

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plotly.ts')

    data = List(Any)

    layout = Dict(String, Any)

    config = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))

    # Callback properties
    relayout_data = Dict(String, Any)
    restyle_data = List(Any)
    click_data = Dict(String, Any)
    hover_data = Dict(String, Any)
    clickannotation_data = Dict(String, Any)
    selected_data = Dict(String, Any)
    viewport = Dict(String, Any)
    viewport_update_policy = Enum("continuous", "mouseup", "throttle")
    viewport_update_throttle = Int()
    _render_count = Int()


CUSTOM_MODELS['panel.models.plotly.PlotlyPlot'] = PlotlyPlot
