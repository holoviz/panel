"""Defines a custom DeckGLPlot to render DeckGL Plots

[Deck.gl](https://deck.gl/#/) is an awesome WebGL-powered framework for visual exploratory data
analysis of large datasets.

And now DeckGL provides Python bindings. See

- [DeckGL Docs](https://deckgl.readthedocs.io/en/latest/)
- [PyDeck Repo](https://github.com/uber/deck.gl/tree/master/bindings/pydeck)
"""

from collections import OrderedDict

from bokeh.core.properties import (
    Any, Bool, Dict, Either, Instance, List, Override, String
)
from bokeh.models import HTMLBox, ColumnDataSource

from ..io.resources import bundled_files
from ..util import classproperty


class DeckGLPlot(HTMLBox):
    """A Bokeh model that wraps around a DeckGL plot and renders it inside a HTMLBox"""

    __css_raw__ = ["https://api.mapbox.com/mapbox-gl-js/v1.7.0/mapbox-gl.css"]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        "https://cdn.jsdelivr.net/npm/deck.gl@8.1.12/dist.min.js",
        "https://cdn.jsdelivr.net/npm/@deck.gl/json@8.1.12/dist.min.js",
        "https://cdn.jsdelivr.net/npm/@loaders.gl/csv@2.0.2/dist/dist.min.js",
        "https://cdn.jsdelivr.net/npm/@loaders.gl/json@2.0.2/dist/dist.min.js",
        "https://cdn.jsdelivr.net/npm/@loaders.gl/3d-tiles@2.0.2/dist/dist.min.js",
        "https://api.mapbox.com/mapbox-gl-js/v1.7.0/mapbox-gl.js",
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'deck': cls.__javascript__[:-1],
            'mapboxgl': cls.__javascript__[-1:]
        }

    __js_require__ = {
        'paths': OrderedDict([
            ("deck.gl", "https://cdn.jsdelivr.net/npm/@deck.gl/jupyter-widget@^8.1.2/dist/index"),
            ("mapbox-gl", 'https://cdn.jsdelivr.net/npm/mapbox-gl@1.7.0/dist/mapbox-gl.min'),
        ]),
        'exports': {"deck.gl": "deck", "mapbox-gl": "mapboxgl"}
    }

    data = Dict(String, Any)

    data_sources = List(Instance(ColumnDataSource))

    initialViewState = Dict(String, Any)

    layers = List(Dict(String, Any))

    mapbox_api_key = String()

    tooltip = Either(Bool, Dict(Any, Any))

    clickState = Dict(String, Any)

    hoverState = Dict(String, Any)

    viewState = Dict(String, Any)

    height = Override(default=400)

    width = Override(default=600)
