"""
Defines custom bokeh model to render ECharts plots.
"""
from bokeh.core.properties import (
    Any, Dict, Enum, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import LayoutDOM

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class EChartsEvent(ModelEvent):

    event_name = 'echarts_event'

    def __init__(self, model, type=None, data=None, query=None):
        self.type = type
        self.data = data
        self.query = query
        super().__init__(model=model)


class ECharts(LayoutDOM):
    """
    A Bokeh model that wraps around an ECharts plot and renders it
    inside a Bokeh.
    """

    __javascript_raw__ = [
        f"{config.npm_cdn}/echarts@5.4.1/dist/echarts.min.js",
        f"{config.npm_cdn}/echarts-gl@2.0.9/dist/echarts-gl.min.js"
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
            "echarts":  f"{config.npm_cdn}/echarts@5.4.1/dist/echarts.min",
            "echarts-gl": f"{config.npm_cdn}/echarts-gl@2.0.9/dist/echarts-gl.min"
        },
        'exports': {}
    }

    data = Nullable(Dict(String, Any))

    options = Nullable(Dict(String, Any))

    event_config = Dict(String, Any)

    js_events = Dict(String, List(Any))

    renderer = Enum("canvas", "svg")

    theme = Enum("default", "light", "dark")
