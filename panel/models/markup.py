"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import Bool, Either, Int, Float, Nullable, String
from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """


class JSON(Markup):
    """
    A bokeh model that renders JSON as tree.
    """

    depth = Either(Nullable(Int), Float, default=1, help="Depth to which the JSON tree is expanded.")

    hover_preview = Bool(default=False, help="Whether to show a hover preview for collapsed nodes.")

    theme = String(default='dark', help="Whether to expand all JSON nodes.")
