"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
import os

from bokeh.core.properties import Dict, String, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from ..compiler import CUSTOM_MODELS


class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __javascript__ = ["https://cdn.jsdelivr.net/npm/vega@5.3.1",
                      'https://cdn.jsdelivr.net/npm/vega-lite@3.0.0',
                      'https://cdn.jsdelivr.net/npm/vega-embed@4.0.0-rc1']

    __js_require__ = {
        'baseUrl': 'https://cdn.jsdelivr.net/npm/',
        'paths': {
            "vega-embed":  "vega-embed@4.0.0/build/vega-embed.min",
            "vega-lite": "vega-lite@3.0.0/build/vega-lite.min",
            "vega": "vega@5.3.1/build/vega.min"
        },
        'exports': {'vega-embed': 'vegaEmbed', 'vega': 'vega', 'vega-lite': 'vl'}
    }

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vega.ts')

    data = Dict(String, Any)

    data_sources = Dict(String, Instance(ColumnDataSource))


CUSTOM_MODELS['panel.models.vega.VegaPlot'] = VegaPlot
