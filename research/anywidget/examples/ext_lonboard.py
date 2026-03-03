"""
Lonboard Map — Compound AnyWidget Example
==========================================

Renders a lonboard Map with ScatterplotLayer using Panel's AnyWidget pane.
Lonboard is a *compound widget*: its Map references child widgets (layers,
controls, basemap) via ``IPY_MODEL_<id>`` strings using ipywidgets'
``widget_serialization`` protocol.  Panel's compound widget support resolves
these references via ``widget_manager.get_model(id)`` on the JS side.

GitHub: https://github.com/developmentseed/lonboard
Docs:   https://developmentseed.org/lonboard/

Required packages:
    geopandas, lonboard, shapely

Run with:
    panel serve research/anywidget/examples/ext_lonboard.py --dev
"""

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

import lonboard

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample geodata (4 US cities)
# ---------------------------------------------------------------------------

cities = gpd.GeoDataFrame(
    {
        "name": ["New York", "San Francisco", "Chicago", "Houston"],
        "pop_millions": [8.3, 0.87, 2.7, 2.3],
    },
    geometry=[
        Point(-73.9857, 40.7484),
        Point(-122.4194, 37.7749),
        Point(-87.6298, 41.8781),
        Point(-95.3698, 29.7604),
    ],
    crs="EPSG:4326",
)

# ---------------------------------------------------------------------------
# 2. Build lonboard Map with a ScatterplotLayer
# ---------------------------------------------------------------------------

layer = lonboard.ScatterplotLayer.from_geopandas(
    cities,
    get_radius=100_000,
    get_fill_color=[255, 0, 80, 200],
)

m = lonboard.Map(layers=[layer])

# ---------------------------------------------------------------------------
# 3. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(m, height=500, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# Lonboard Map — Compound AnyWidget

[GitHub](https://github.com/developmentseed/lonboard) |
[Docs](https://developmentseed.org/lonboard/)

This example renders a **lonboard** Map with a ScatterplotLayer showing
4 US cities. Lonboard is a *compound widget* — its Map references child
widgets (layers, controls, basemap) via `IPY_MODEL_` strings. Panel's
compound widget support resolves these through `widget_manager.get_model()`.
""")

pn.Column(
    header,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
