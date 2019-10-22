"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
from bokeh.core.properties import Dict, String, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from ..util import public

@public
class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __javascript__ = ["https://cdn.jsdelivr.net/npm/vega@5.3.1",
                      'https://cdn.jsdelivr.net/npm/vega-lite@3.2.1',
                      'https://cdn.jsdelivr.net/npm/vega-embed@4.0.0-rc1']

    __js_require__ = {
        'baseUrl': 'https://cdn.jsdelivr.net/npm/',
        'paths': {
            "vega-embed":  "vega-embed@4.0.0/build/vega-embed.min",
            "vega-lite": "vega-lite@3.2.1/build/vega-lite.min",
            "vega": "vega@5.3.1/build/vega.min"
        },
        'exports': {'vega-embed': 'vegaEmbed', 'vega': 'vega', 'vega-lite': 'vl'}
    }

    data = Dict(String, Any)

    data_sources = Dict(String, Instance(ColumnDataSource))
