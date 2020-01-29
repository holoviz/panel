"""Defines a custom DeckGLPlot to render DeckGL Plots

[Deck.gl](https://deck.gl/#/) is an awesome WebGL-powered framework for visual exploratory data
analysis of large datasets.

And now DeckGL provides Python bindings. See

- [DeckGL Docs](https://deckgl.readthedocs.io/en/latest/)
- [PyDeck Repo](https://github.com/uber/deck.gl/tree/master/bindings/pydeck)
"""

from collections import OrderedDict

from bokeh.core.properties import String, Bool, JSON, Override
from bokeh.models import HTMLBox


class DeckGLPlot(HTMLBox):
    """A Bokeh model that wraps around a DeckGL plot and renders it inside a HTMLBox"""

    __css__ = ["https://api.mapbox.com/mapbox-gl-js/v1.7.0/mapbox-gl.css"]

    __javascript__ = ["https://cdn.jsdelivr.net/npm/deck.gl@8.1.0-alpha.1/dist.min.js",
                      "https://cdn.jsdelivr.net/npm/@deck.gl/json@8.1.0-alpha.1/dist/dist.dev.js",
                      "https://cdn.jsdelivr.net/npm/@loaders.gl/csv@2.0.2/dist/dist.min.js",
                      "https://cdn.jsdelivr.net/npm/@loaders.gl/json@2.0.2/dist/dist.min.js",
                      "https://cdn.jsdelivr.net/npm/@loaders.gl/3d-tiles@2.0.2/dist/dist.min.js",
                      "https://api.mapbox.com/mapbox-gl-js/v1.7.0/mapbox-gl.js",
    ]

    __js_skip__ = {'deck': __javascript__[:-1], 'mapboxgl': __javascript__[-1:]}

    __js_require__ = {
        'paths': OrderedDict([
            ("deck.gl", "https://cdn.jsdelivr.net/npm/@deck.gl/jupyter-widget@^8.0.0/dist/index"),
            ("mapbox-gl", 'https://cdn.jsdelivr.net/npm/mapbox-gl@1.6.1/dist/mapbox-gl.min'),
        ]),
        'exports': {"deck.gl": "deck", "mapbox-gl": "mapboxgl"}
    }

    json_input = JSON()
    mapbox_api_key = String()
    tooltip = Bool()

    height = Override(default=400)
    width = Override(default=600)
