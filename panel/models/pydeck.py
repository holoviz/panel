"""Defines a custom PyDeckPlot to render PyDeck Plots

[Deck.gl](https://deck.gl/#/) is an awesome WebGL-powered framework for visual exploratory data
analysis of large datasets.

And now PyDeck provides Python bindings. See

- [PyDeck Docs](https://deckgl.readthedocs.io/en/latest/)
- [PyDeck Repo](https://github.com/uber/deck.gl/tree/master/bindings/pydeck)
"""
from bokeh.core.properties import Dict, String, List, Any, Instance, Enum, Int, Bool
from bokeh.models import LayoutDOM, ColumnDataSource


class PyDeckPlot(LayoutDOM):
    """A Bokeh model that wraps around a PyDeck plot and renders it inside a HTMLBox"""

    json_input = String()
    mapbox_api_key = String()
    tooltip = Bool()  # Or Dict(String, Any)

    # description = String()
    # initial_view_state = Dict(String, Any)
    # layers = List(Dict(String, Any))
    # map_style = String()
    # mapbox_key = String()
    # selected_data = List(Dict(String, Any))
    # views = List(Dict(String, Any))
