"""
Defines custom VizzuChart bokeh model to render Vizzu charts.
"""
from bokeh.core.properties import (
    Any, Dict, Instance, Int, List, String,
)
from bokeh.models import LayoutDOM
from bokeh.models.sources import DataSource

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class VizzuChart(LayoutDOM):
    """
    A Bokeh model that wraps around an Vizzu chart and renders it
    inside a Bokeh.
    """

    __javascript_module_exports__ = ['Vizzu']

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/vizzu@latest/dist/vizzu.min.js"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')

    config = Dict(String, Any)

    columns = List(Dict(String, Any))

    source = Instance(DataSource, help="""
    Local data source to use when rendering glyphs on the plot.
    """)

    config = Dict(String, Any)

    duration = Int(500)

    style = Dict(String, Any)
