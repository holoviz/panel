"""
Defines custom ECharts bokeh model to render Vega json plots.
"""
from bokeh.core.properties import (
    Any, Dict, Enum, String,
)
from bokeh.models import LayoutDOM

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class ECharts(LayoutDOM):
    """
    A Bokeh model that wraps around an ECharts plot and renders it
    inside a Bokeh.
    """

    __javascript_raw__ = [
        f"{config.npm_cdn}/echarts@5.0.2/dist/echarts.min.js",
        f"{config.npm_cdn}/echarts-gl@2.0.2/dist/echarts-gl.min.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'echarts': cls.__javascript__[:1]
        }

    __js_require__ = {
        'paths': {
            "echarts":  f"{config.npm_cdn}/echarts@5.0.2/dist/echarts.min",
            "echarts-gl": f"{config.npm_cdn}/echarts-gl@2.0.2/dist/echarts-gl.min.js"
        },
        'exports': {}
    }

    data = Dict(String, Any)

    renderer = Enum("canvas", "svg")

    theme = Enum("default", "light", "dark")
