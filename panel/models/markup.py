"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import (
    Bool, Dict, Either, Float, Int, List, Null, String,
)
from bokeh.models.widgets import Div, Markup


class HTML(Div):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """

    events = Dict(String, List(String))


class JSON(Markup):
    """
    A bokeh model that renders JSON as tree.
    """

    depth = Either(Int, Float, Null, default=1, help="Depth to which the JSON tree is expanded.")

    hover_preview = Bool(default=False, help="Whether to show a hover preview for collapsed nodes.")

    theme = String(default='dark', help="Whether to expand all JSON nodes.")
