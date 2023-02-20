"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import (
    Bool, Dict, Either, Float, Int, List, Null, String,
)
from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """

    events = Dict(String, List(String))

    run_scripts = Bool(True, help="Whether to run scripts defined within the HTML")


class JSON(Markup):
    """
    A bokeh model that renders JSON as tree.
    """

    depth = Either(Int, Float, Null, default=1, help="Depth to which the JSON tree is expanded.")

    hover_preview = Bool(default=False, help="Whether to show a hover preview for collapsed nodes.")

    theme = String(default='dark', help="Whether to expand all JSON nodes.")


class PDF(Markup):

    embed = Bool(True, help="Whether to embed the file")

    start_page = Int(default=1, help="Start page of the pdf, by default the first page.")
