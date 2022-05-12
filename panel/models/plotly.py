"""
Defines a custom PlotlyPlot bokeh model to render Plotly plots.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Int, Instance, List, Null, Nullable, String
)
from bokeh.models import LayoutDOM, ColumnDataSource

from ..io.resources import JS_URLS, bundled_files
from ..util import classproperty


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __javascript_raw__ = [
        JS_URLS['jQuery'],
        'https://cdn.plot.ly/plotly-2.10.1.min.js'
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'Plotly': cls.__javascript__[1:]}

    __js_require__ = {
        'paths': {
            'plotly': 'https://cdn.plot.ly/plotly-2.10.1.min'
        },
        'exports': {'plotly': 'Plotly'}
    }

    data = List(Any)

    layout = Dict(String, Any)

    frames = List(Any)

    config = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))

    relayout = Nullable(Dict(String, Any))

    restyle = Nullable(Dict(String, Any))

    # Callback properties
    relayout_data = Dict(String, Any)
    restyle_data = List(Any)
    click_data = Either(Dict(String, Any), Null)
    hover_data = Either(Dict(String, Any), Null)
    clickannotation_data = Either(Dict(String, Any), Null)
    selected_data = Either(Dict(String, Any), Null)
    viewport = Either(Dict(String, Any), Null)
    viewport_update_policy = Enum( "mouseup", "continuous", "throttle")
    viewport_update_throttle = Int()
    visibility = Bool(True)
    _render_count = Int()
