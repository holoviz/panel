"""
Defines custom VegaPlot bokeh model to render Vega json plots.
"""
from __future__ import annotations

from typing import Literal

from bokeh.core.enums import enumeration
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, Instance, Int, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models import ColumnDataSource, LayoutDOM

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty

VEGA_VERSION = "6.1.2"
VEGA_LITE_VERSION = "6.3.0"
VEGA_EMBED_VERSION = "7.0.2"

VegaThemeType = Literal[
        'excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight', 'dark',
        'latimes', 'urbaninstitute', 'googlecharts', 'powerbi', 'carbonwhite', 'carbong10', 'carbong90', 'carbong100']
VegaTheme = enumeration(VegaThemeType)

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
        f"{config.npm_cdn}/vega@{VEGA_VERSION}",
        f"{config.npm_cdn}/vega-lite@{VEGA_LITE_VERSION}",
        f"{config.npm_cdn}/vega-embed@{VEGA_EMBED_VERSION}"
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
            "vega-embed":  f"{config.npm_cdn}/vega-embed@{VEGA_EMBED_VERSION}/build/vega-embed.min",
            "vega-lite": f"{config.npm_cdn}/vega-lite@{VEGA_LITE_VERSION}/build/vega-lite.min",
            "vega": f"{config.npm_cdn}/vega@{VEGA_VERSION}/build/vega.min"
        },
        'exports': {'vega-embed': 'vegaEmbed', 'vega': 'vega', 'vega-lite': 'vl'}
    }

    data = Nullable(Dict(String, Any))

    data_sources = Dict(String, Instance(ColumnDataSource))

    events = List(String)

    show_actions = Bool(False)

    theme = Nullable(Enum(VegaTheme))

    throttle = Dict(String, Int)
