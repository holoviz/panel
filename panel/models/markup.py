"""
Custom bokeh Markup models.
"""
from typing import Any

from bokeh.core.properties import (
    Bool, Dict, Either, Float, Int, List, Null, String,
)
from bokeh.events import ModelEvent
from bokeh.models.widgets import Markup


class HTMLStreamEvent(ModelEvent):

    event_name = 'html_stream'

    def __init__(self, model, patch=None, start=None):
        self.patch = patch
        self.start = start
        super().__init__(model=model)

    def event_values(self) -> dict[str, Any]:
        return dict(super().event_values(), patch=self.patch, start=self.start)


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

    embed = Bool(False, help="Whether to embed the file")

    start_page = Int(default=1, help="Start page of the pdf, by default the first page.")
