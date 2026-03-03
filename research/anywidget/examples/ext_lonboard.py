"""
Lonboard Map — Compound Widget (Requires IPyWidget Pane)
=========================================================

This example documents why lonboard does NOT work with Panel's AnyWidget pane
and shows the correct approach using ``pn.pane.IPyWidget`` instead.

Lonboard is a *compound widget*: its Map references child widgets (layers,
controls, basemap) via ``IPY_MODEL_<id>`` strings using ipywidgets'
``widget_serialization`` protocol.  The AnyWidget pane only supports *leaf*
anywidgets with flat, JSON-serializable traits.

GitHub: https://github.com/developmentseed/lonboard
Docs:   https://developmentseed.org/lonboard/

To render lonboard in Panel, use the IPyWidget pane with ipywidgets_bokeh:

    pn.extension("ipywidgets")
    m = lonboard.Map(layers=[...])
    pn.pane.IPyWidget(m)

Required packages:
    pip install lonboard geopandas ipywidgets_bokeh

Run with:
    panel serve research/anywidget/examples/ext_lonboard.py
"""

import lonboard  # noqa: F401

import panel as pn

pn.extension()

status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> Lonboard is a <em>compound widget</em> &mdash; its Map references
child widgets (layers, controls, basemap) via <code>IPY_MODEL_</code> strings.
The AnyWidget pane only supports leaf widgets with flat traits.
Use <code>pn.pane.IPyWidget</code> with <code>pn.extension("ipywidgets")</code> instead.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# Lonboard Map -- Why AnyWidget Pane Doesn't Work

## The Root Cause: Compound Widget Architecture

Lonboard's Map is not a simple anywidget.  It is a **compound widget tree**:

```
Map (anywidget.AnyWidget)
  layers:   ["IPY_MODEL_abc123", "IPY_MODEL_def456"]  <-- child widget refs
  controls: ["IPY_MODEL_ghi789"]                       <-- child widget refs
  basemap:  "IPY_MODEL_jkl012"                         <-- child widget ref
  view:     "IPY_MODEL_mno345"                         <-- child widget ref
```

Each child (ScatterplotLayer, PathLayer, MaplibreBasemap, etc.) is itself an
ipywidgets Widget with its own traits, binary data, and comms.

The AnyWidget pane extracts traits from a **single** widget and converts them
to Panel params.  It cannot resolve `IPY_MODEL_` references to child widgets.
The lonboard ESM calls `model.widget_manager.get_model(id)` to look up each
child -- and our adapter's stub `widget_manager` rejects those calls.

## Four Specific Incompatibilities

| Issue | Detail |
|-------|--------|
| **No widget_manager** | ESM calls `model.widget_manager.get_model(id)` to resolve layers, controls, basemap, view.  Our adapter returns a stub. |
| **Widget tree is not flat** | `layers` serializes to `["IPY_MODEL_..."]` strings, not actual data.  Each layer has its own nested state. |
| **Binary Parquet data** | Layer geometry is serialized as Parquet bytes sent through ipywidgets' binary comm protocol. |
| **3 MB ESM bundle** | Panel inlines ESM in WebSocket JSON.  The 3 MB bundle exceeds transmission limits. |

## The Correct Approach: IPyWidget + ipywidgets_bokeh

ipywidgets_bokeh provides a **full Jupyter kernel emulation** inside the Bokeh
server, including:
- A real `WidgetManager` that can resolve `IPY_MODEL_` references
- Binary buffer transport through the comm protocol
- CDN-based module loading (so the 3 MB ESM loads from unpkg, not WebSocket)
- Full comm channel for live bidirectional updates

```python
import geopandas as gpd
import lonboard

import panel as pn

pn.extension("ipywidgets")  # enables ipywidgets_bokeh

gdf = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
layer = lonboard.SolidPolygonLayer.from_geopandas(gdf, opacity=0.5)
m = lonboard.Map(layers=[layer])

pn.pane.IPyWidget(m).servable()
```

## Summary

| Pane | Works with lonboard? | Why? |
|------|---------------------|------|
| `pn.pane.AnyWidget` | No | Extracts flat traits, no widget_manager, no IPY_MODEL resolution |
| `pn.pane.IPyWidget` | **Yes** | Full ipywidgets kernel emulation via ipywidgets_bokeh |
""")

pn.Column(
    status,
    header,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
