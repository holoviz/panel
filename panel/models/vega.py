"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
import os

from bokeh.core.properties import Dict, String, Any, Instance
from bokeh.models import LayoutDOM, ColumnDataSource

from ..util import CUSTOM_MODELS

class VegaPlot(LayoutDOM):
    """
    A Bokeh model that wraps around a Vega plot and renders it inside
    a Bokeh plot.
    """

    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/vega/5.2.0/vega.min.js",
                      'https://cdnjs.cloudflare.com/ajax/libs/vega-lite/2.6.0/vega-lite.min.js',
                      'https://cdnjs.cloudflare.com/ajax/libs/vega-embed/3.30.0/vega-embed.min.js']

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vega.ts')

    data = Dict(String, Any)

    data_sources = Dict(String, Instance(ColumnDataSource))


CUSTOM_MODELS['panel.models.vega.VegaPlot'] = VegaPlot
