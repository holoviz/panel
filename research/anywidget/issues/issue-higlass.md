# HiGlass — Incompatibility with Panel's AnyWidget Pane

## Summary

HiGlass's `HiGlassWidget` is an anywidget that internally uses Jupyter's widget model manager (`model.widget_manager.get_model()`) to register its data-fetching tileset client. Panel's AnyWidget adapter does not implement the Jupyter widget manager protocol, causing the ESM to crash when it tries to resolve the `_tileset_client` trait. Additionally, the widget's ESM bundles the entire React-based HiGlass viewer, which may be large enough to hit WebSocket payload limits.

## Environment
- Panel: latest (PR #8428)
- higlass-python: 1.4.0
- Python: 3.10+

## Root Cause

HiGlass's ESM expects the `_tileset_client` trait to contain a Jupyter `IPY_MODEL_<id>` string that it resolves via `model.widget_manager.get_model()`. In Jupyter, this trait points to a `JupyterTilesetClient` widget that handles data fetching through the comm protocol.

In Panel's AnyWidget pane, two things go wrong:

1. **No widget_manager**: The ESM calls `model.widget_manager.get_model()` to resolve the tileset client. Panel's adapter provides only a stub widget_manager that cannot resolve model references.
2. **Trait type mismatch**: The `_tileset_client` trait is a Python widget object, not an `IPY_MODEL_xxx` string. When the ESM tries to use it (e.g., `model.get("_tileset_client").slice(...)`), it crashes with `TypeError: model.get(...).slice is not a function`.

The HiGlass ESM also bundles the full React-based viewer, which may be large enough to cause WebSocket disconnections (similar to the anymap-ts and rerun issues).

## Minimal Reproducible Example

```python
import higlass as hg

import panel as pn

pn.extension()

tileset = hg.remote(
    uid="CQMd6V_cRw6iCI_-Unl3PQ",
    server="https://higlass.io/api/v1/",
    name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
)
track = tileset.track("heatmap")
view = hg.view(hg.track("top-axis"), track)
widget = view.widget()

pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width").servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** The ESM crashes with `TypeError: model.get(...).slice is not a function` because the `_tileset_client` trait is a Python object rather than a Jupyter `IPY_MODEL_xxx` string. The widget_manager stub cannot resolve child widget references. Even with remote tilesets (which do not require the comm protocol for data fetching), the widget fails to initialize because the tileset client registration code still runs during setup.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead. The `ipywidgets_bokeh` backend provides full Jupyter kernel emulation including the `WidgetManager` needed to resolve the tileset client widget.

```python
import higlass as hg

import panel as pn

pn.extension("ipywidgets")

tileset = hg.remote(
    uid="CQMd6V_cRw6iCI_-Unl3PQ",
    server="https://higlass.io/api/v1/",
    name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
)
track = tileset.track("heatmap")
view = hg.view(hg.track("top-axis"), track)
widget = view.widget()

pn.pane.IPyWidget(widget).servable()
```

## Suggested Fix

HiGlass would need to either:
1. Make the tileset client registration optional or deferred, so the widget can render with remote tilesets without requiring widget_manager resolution.
2. Provide a standalone rendering mode that does not depend on the Jupyter widget model infrastructure for data fetching setup.

On Panel's side, supporting `widget_manager.get_model()` for compound widgets would be a significant architectural addition beyond the scope of the leaf-widget-focused AnyWidget pane.
