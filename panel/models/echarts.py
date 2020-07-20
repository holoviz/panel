"""
Defines custom ECharts bokeh model to render Vega json plots.
"""
from bokeh.core.properties import Dict, String, Any, Instance, Enum
from bokeh.models import LayoutDOM, ColumnDataSource


class ECharts(LayoutDOM):
    """
    A Bokeh model that wraps around an ECharts plot and renders it
    inside a Bokeh.
    """

    __javascript__ = ["https://cdn.jsdelivr.net/npm/echarts@4.8.0/dist/echarts.min.js"]

    __js_skip__ = {
        'echarts': __javascript__[:1]}

    __js_require__ = {
        'baseUrl': 'https://cdn.jsdelivr.net/npm/',
        'paths': {
            "echarts":  "echarts@4.8.0/dist/echarts.min"
        },
        'exports': {}
    }

    data = Dict(String, Any)

    theme = Enum("default", "light", "dark")
