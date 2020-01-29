"""
Defines a custom PlotlyPlot bokeh model to render Plotly plots.
"""
from bokeh.core.properties import Dict, String, List, Any, Instance, Enum, Int
from bokeh.models import LayoutDOM, ColumnDataSource


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __javascript__ = ['https://cdn.plot.ly/plotly-latest.min.js']

    __js_skip__ = {'Plotly': __javascript__}

    __js_require__ = {'paths': {'plotly': 'https://cdn.plot.ly/plotly-latest.min'},
                      'exports': {'plotly': 'Plotly'}}

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
    viewport_update_policy = Enum( "mouseup", "continuous", "throttle")
    viewport_update_throttle = Int()
    _render_count = Int()
