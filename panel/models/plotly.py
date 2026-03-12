"""
Defines a custom PlotlyPlot bokeh model to render Plotly plots.
"""
from bokeh.core.properties import (
    Any, Dict, Either, Enum, Instance, Int, List, Null, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource, LayoutDOM

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty

PLOTLY_VERSION = '3.1.0'


class PlotlyEvent(ModelEvent):

    event_name = 'plotly_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class PlotlyPlot(LayoutDOM):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """
    __css_raw__ = [
        f"{config.npm_cdn}/maplibre-gl@4.4.1/dist/maplibre-gl.css"
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        f'https://cdn.plot.ly/plotly-{PLOTLY_VERSION}.min.js'
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'Plotly': cls.__javascript__[1:]}

    __js_require__ = {
        'paths': {
            'plotly': f'https://cdn.plot.ly/plotly-{PLOTLY_VERSION}.min'
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
    viewport = Either(Dict(String, Any), Null)
    viewport_update_policy = Enum( "mouseup", "continuous", "throttle")
    viewport_update_throttle = Int()
    _render_count = Int()
