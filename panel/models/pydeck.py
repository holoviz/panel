"""Defines a custom PyDeckPlot to render PyDeck Plots

[Deck.gl](https://deck.gl/#/) is an awesome WebGL-powered framework for visual exploratory data
analysis of large datasets.

And now PyDeck provides Python bindings. See

- [PyDeck Docs](https://deckgl.readthedocs.io/en/latest/)
- [PyDeck Repo](https://github.com/uber/deck.gl/tree/master/bindings/pydeck)
"""

from collections import OrderedDict

from bokeh.core.properties import Dict, String, List, Any, Instance, Enum, Int, Bool, JSON, Override
from bokeh.models import HTMLBox


class PyDeckPlot(HTMLBox):
    """A Bokeh model that wraps around a PyDeck plot and renders it inside a HTMLBox"""

    __css__ = ["https://cdn.jsdelivr.net/npm/mapbox-gl@1.6.1/dist/mapbox-gl.css"]

    __javascript__ = ["https://cdn.jsdelivr.net/npm/deck.gl@8.1.0-alpha.1/dist.min.js",
                      "https://cdn.jsdelivr.net/npm/@deck.gl/json@8.1.0-alpha.1/dist/dist.dev.js",
                      "https://cdn.jsdelivr.net/npm/mapbox-gl@1.6.1",
                      "https://cdn.jsdelivr.net/npm/@loaders.gl/csv@2.0.2/dist/dist.min.js",
                      "https://cdn.jsdelivr.net/npm/@loaders.gl/3d-tiles@2.0.2/dist/dist.min.js"]

    __js_require__ = {
        'paths': OrderedDict([
            ("deck.gl", "https://cdn.jsdelivr.net/npm/@deck.gl/jupyter-widget@^8.0.0/dist/index"),
            ("mapbox-gl", 'https://cdn.jsdelivr.net/npm/mapbox-gl@1.6.1/dist/mapbox-gl.min'),
        ]),
        'exports': {"deck.gl": "deck", "mapbox-gl": "mapboxgl"}
    }

    json_input = JSON()
    mapbox_api_key = String()
    tooltip = Bool()  # Or Dict(String, Any)
    _render_count = Int()

    height = Override(default=400)
    width = Override(default=600)

    # description = String()
    # initial_view_state = Dict(String, Any)
    # layers = List(Dict(String, Any))
    # map_style = String()
    # mapbox_key = String()
    # selected_data = List(Dict(String, Any))
    # views = List(Dict(String, Any))
