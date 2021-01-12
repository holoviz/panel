"""
Custom bokeh Markup models.
"""
import bokeh.core.properties as bp

from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """

    events = bp.Dict(bp.String, bp.List(bp.String))


class JSON(Markup):
    """
    A bokeh model that renders JSON as tree.
    """

    depth = bp.Either(bp.Int, bp.Float, default=1, help="Depth to which the JSON tree is expanded.")

    hover_preview = bp.Bool(default=False, help="Whether to show a hover preview for collapsed nodes.")

    theme = bp.String(default='dark', help="Whether to expand all JSON nodes.")
