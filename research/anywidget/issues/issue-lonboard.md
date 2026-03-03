# Lonboard — Incompatibility with Panel's AnyWidget Pane

## Summary

Lonboard's `Map` widget is a compound widget that references child widgets (layers, controls, basemap, view) via `IPY_MODEL_<id>` strings using ipywidgets' `widget_serialization` protocol. Panel's AnyWidget pane only supports leaf anywidgets with flat, JSON-serializable traits and cannot resolve `IPY_MODEL_` references. The lonboard ESM calls `model.widget_manager.get_model(id)` to look up each child widget, and our adapter's stub `widget_manager` cannot fulfill those calls.

## Environment
- Panel: latest (PR #8428)
- lonboard: 0.14.0
- Python: 3.10+

## Root Cause

Lonboard's `Map` is not a simple leaf anywidget. It is a compound widget tree where the top-level Map references child widgets via `IPY_MODEL_<id>` strings:

```
Map (anywidget.AnyWidget)
  layers:   ["IPY_MODEL_abc123", "IPY_MODEL_def456"]   <-- child widget refs
  controls: ["IPY_MODEL_ghi789"]                         <-- child widget refs
  basemap:  "IPY_MODEL_jkl012"                           <-- child widget ref
  view:     "IPY_MODEL_mno345"                           <-- child widget ref
```

Each child (ScatterplotLayer, PathLayer, MaplibreBasemap, etc.) is itself an ipywidgets Widget with its own traits, binary data, and comms. The lonboard ESM calls `model.widget_manager.get_model(id)` to resolve each child. Panel's AnyWidget adapter provides only a stub `widget_manager`, so these calls fail.

There are four specific incompatibilities:

1. **No widget_manager**: The ESM calls `model.widget_manager.get_model(id)` to resolve layers, controls, basemap, and view. Panel's adapter returns a stub.
2. **Widget tree is not flat**: The `layers` trait serializes to `["IPY_MODEL_..."]` strings, not actual data. Each layer has its own nested state.
3. **Binary Parquet data**: Layer geometry is serialized as Parquet bytes sent through ipywidgets' binary comm protocol, which Panel does not implement.
4. **3 MB ESM bundle**: Panel inlines ESM in WebSocket JSON. The ~3 MB bundle approaches transmission limits.

## Minimal Reproducible Example

```python
import geopandas as gpd
import lonboard

import panel as pn

pn.extension()

gdf = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
layer = lonboard.SolidPolygonLayer.from_geopandas(gdf, opacity=0.5)
m = lonboard.Map(layers=[layer])

# This will fail — Map is a compound widget
pn.pane.AnyWidget(m).servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** The ESM fails to resolve child widgets. Calls to `model.widget_manager.get_model(id)` for layers, controls, basemap, and view return errors because Panel's adapter provides only a stub widget_manager without real model resolution.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead. The `ipywidgets_bokeh` backend provides full Jupyter kernel emulation inside the Bokeh server, including a real `WidgetManager` that can resolve `IPY_MODEL_` references, binary buffer transport, and CDN-based module loading.

```python
import geopandas as gpd
import lonboard

import panel as pn

pn.extension("ipywidgets")

gdf = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
layer = lonboard.SolidPolygonLayer.from_geopandas(gdf, opacity=0.5)
m = lonboard.Map(layers=[layer])

pn.pane.IPyWidget(m).servable()
```

## Suggested Fix

Supporting compound widgets would require implementing a full `WidgetManager` with `get_model()` resolution inside Panel's AnyWidget adapter. This is a fundamental architectural gap — the AnyWidget pane is designed for leaf widgets with flat traits. Compound widgets that reference child widgets via `IPY_MODEL_` strings should use the IPyWidget pane instead.
