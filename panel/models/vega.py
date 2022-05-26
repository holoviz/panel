"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, Instance, Int, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource, LayoutDOM

from ..io.resources import bundled_files
from ..util import classproperty


class VegaEvent(ModelEvent):

    event_name = 'vega_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __javascript_raw__ = [
        "https://cdn.jsdelivr.net/npm/vega@5",
        "https://cdn.jsdelivr.net/npm/vega-lite@5",
        "https://cdn.jsdelivr.net/npm/vega-embed@6"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'vega': cls.__javascript__[:1],
            'vegaLite': cls.__javascript__[1:2],
            'vegaEmbed': cls.__javascript__[2:]
        }

    __js_require__ = {
        'paths': {
            "vega-embed":  "https://cdn.jsdelivr.net/npm/vega-embed@6/build/vega-embed.min",
            "vega-lite": "https://cdn.jsdelivr.net/npm/vega-lite@5/build/vega-lite.min",
            "vega": "https://cdn.jsdelivr.net/npm/vega@5/build/vega.min"
        },
        'exports': {'vega-embed': 'vegaEmbed', 'vega': 'vega', 'vega-lite': 'vl'}
    }

    data = Nullable(Dict(String, Any))

    data_sources = Dict(String, Instance(ColumnDataSource))

    events = List(String)

    show_actions = Bool(False)

    theme = Nullable(Enum('excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight', 'dark',
                 'latimes', 'urbaninstitute', 'googlecharts', default=None))

    throttle = Dict(String, Int)
