"""
Lonboard Map — Known Limitation (Large ESM Bundle)
===================================================

This example documents a known limitation with the lonboard Map widget.
Lonboard bundles the entire deck.gl library and its GeoArrow bindings
into its ESM module, resulting in a very large JavaScript payload.

Lonboard's Map class subclasses anywidget.AnyWidget and dynamically
fetches its ESM bundle. The bundle includes deck.gl, GeoArrow rendering,
and MapLibre GL JS — totaling several megabytes of JavaScript. This
exceeds what Panel's AnyWidget pane can transmit via WebSocket.

Additionally, lonboard uses Apache Arrow (PyArrow) for high-performance
binary data transfer to the GPU. The layer data is serialized as Parquet
and decoded client-side via the @geoarrow/deck.gl-layers library. This
binary serialization path is not supported by Panel's AnyWidget pane
which only handles JSON-serializable traitlets.

Required packages:
    pip install lonboard geopandas

Run with:
    panel serve research/anywidget/examples/lonboard_example.py
"""

import panel as pn

try:
    import lonboard  # noqa: F401
except ImportError as e:
    raise ImportError(
        "This example requires lonboard. "
        "Please install it with: pip install lonboard geopandas"
    ) from e

pn.extension()

header = pn.pane.Markdown("""
# Lonboard Map — Large ESM Bundle Limitation

## The Problem

**Lonboard** bundles the entire deck.gl visualization framework into its ESM:
- **ESM bundle:** Several megabytes of JavaScript (deck.gl + MapLibre GL + GeoArrow)
- **Binary data:** Layer data is serialized as Apache Arrow / Parquet (not JSON)

Panel's `AnyWidget` pane serializes ESM as inline JavaScript and sends it via
WebSocket. For bundles this large, the WebSocket connection closes before the
payload can be transmitted.

Additionally, lonboard uses Apache Arrow binary serialization for layer data
(points, lines, polygons). Panel's AnyWidget pane currently only syncs
JSON-serializable traitlets, so the binary GeoArrow data transfer path
would not work even if the ESM bundle were small enough.

## What Works vs. What Doesn't

| Feature | Status |
|---------|--------|
| Python-side layer creation | Works |
| GeoDataFrame to layer conversion | Works |
| ESM extraction | **May fail** (large bundle) |
| WebSocket transmission | **Fails** (payload too large) |
| Binary Arrow data sync | **Not supported** (non-JSON traitlets) |
| Browser-side map rendering | **Fails** |

## Alternative

For geospatial visualization in Panel, consider:
- `pn.pane.DeckGL` for deck.gl-based maps (native Panel support)
- The `leaflet_map.py` example in this directory for a lightweight
  anywidget map using CDN-loaded Leaflet.js
- `folium` or `ipyleaflet` for interactive web maps

## Potential Fix

Two enhancements would be needed:
1. **External ESM loading** — serve the ESM bundle from a URL rather than
   inlining it in the WebSocket message.
2. **Binary traitlet support** — handle Apache Arrow / Parquet data
   serialization alongside JSON traitlets.

## Lonboard Key Properties

```
lonboard.Map
  layers: list[BaseLayer]  — ScatterplotLayer, PathLayer, SolidPolygonLayer, etc.
  view_state: dict          — {longitude, latitude, zoom, pitch, bearing}
  show_tooltip: bool        — hover tooltips
  picking_radius: int       — interaction detection radius in pixels
  basemap: MaplibreBasemap  — background tile layer
```
""")

pn.Column(
    header,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
