"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
from bokeh.core.properties import Any, Dict, Instance, Nullable, String
from bokeh.models import LayoutDOM, ColumnDataSource

from ..io.resources import bundled_files
from ..util import classproperty


class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __javascript_raw__ = [
        "https://cdn.jsdelivr.net/npm/vega@5",
        'https://cdn.jsdelivr.net/npm/vega-lite@4',
        'https://cdn.jsdelivr.net/npm/vega-embed@6'
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
        'baseUrl': 'https://cdn.jsdelivr.net/npm/',
        'paths': {
            "vega-embed":  "vega-embed@6/build/vega-embed.min",
            "vega-lite": "vega-lite@4/build/vega-lite.min",
            "vega": "vega@5/build/vega.min"
        },
        'exports': {'vega-embed': 'vegaEmbed', 'vega': 'vega', 'vega-lite': 'vl'}
    }

    data = Nullable(Dict(String, Any))

    data_sources = Dict(String, Instance(ColumnDataSource))
