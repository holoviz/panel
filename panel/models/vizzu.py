"""
Defines custom VizzuChart bokeh model to render Vizzu charts.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Instance, Int, List, String,
)
from bokeh.events import ModelEvent
from bokeh.models import LayoutDOM
from bokeh.models.sources import DataSource

from ..config import config
from ..util import classproperty

VIZZU_VERSION = "0.15"

class VizzuEvent(ModelEvent):

    event_name = 'vizzu_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class VizzuChart(LayoutDOM):
    """
    A Bokeh model that wraps around a Vizzu chart and renders it
    inside a Bokeh.
    """

    __javascript_module_exports__ = ['Vizzu']

    __javascript_modules__ = [
        f"{config.npm_cdn}/vizzu@{VIZZU_VERSION}/dist/vizzu.min.js"
    ]

    @classproperty
    def __js_skip__(cls):
        return {
            'Vizzu': cls.__javascript__[0]
        }

    animation = Dict(String, Any)

    config = Dict(String, Any)

    columns = List(Dict(String, Any))

    source = Instance(DataSource, help="""
    Local data source to use when rendering glyphs on the plot.
    """)

    duration = Int(500)

    style = Dict(String, Any)

    tooltip = Bool()
