"""
Rerun SDK Viewer — Known Limitation (Large WASM Bundle)
=======================================================

This example documents a known limitation with the Rerun SDK viewer widget.
The rerun-notebook package bundles the entire Rerun Viewer compiled to
WebAssembly (~31 MiB for re_viewer_bg.wasm) plus a widget.js glue file.

This exceeds what Panel's AnyWidget pane can handle for inline ESM
serialization. The WebSocket connection will close because the payload
is too large to transmit, similar to the anymap-ts limitation.

Note: rerun-notebook supports alternative asset loading modes
(remote CDN, local server, custom URL) via the RERUN_NOTEBOOK_ASSET
environment variable, but these rely on anywidget's internal asset
serving which is not available through Panel's AnyWidget pane.

Required packages:
    pip install "rerun-sdk[notebook]"

Run with:
    panel serve research/anywidget/examples/ext_rerun.py
"""

import rerun as rr  # noqa: F401

import panel as pn

pn.extension()

header = pn.pane.Markdown("""
# Rerun SDK Viewer — Large WASM Bundle Limitation

## The Problem

**rerun-notebook** bundles the entire Rerun Viewer as WebAssembly:
- **WASM size:** ~31 MiB (`re_viewer_bg.wasm`)
- **widget.js:** JavaScript glue code for the Jupyter widget

Panel's `AnyWidget` pane serializes ESM as inline JavaScript and sends it via
WebSocket. For bundles this large, the WebSocket connection closes before the
payload can be transmitted:

```
Error: Lost websocket connection, 1005 ()
```

## Asset Loading Modes

rerun-notebook supports several asset loading strategies via the
`RERUN_NOTEBOOK_ASSET` environment variable:

| Mode | Value | Description |
|------|-------|-------------|
| Remote (default) | *unset* | Loads from `https://app.rerun.io` |
| Inline | `inline` | Transmits assets directly (memory leak) |
| Local server | `serve-local` | Launches a local asset server thread |
| Custom URL | `https://...` | Loads from a user-hosted location |

However, these modes rely on anywidget's internal asset resolution which
bypasses the ESM extraction that Panel's AnyWidget pane uses.

## What Works vs. What Doesn't

| Feature | Status |
|---------|--------|
| Python-side import | Works |
| Recording data with `rr.log()` | Works (Python-side) |
| ESM extraction | **Fails** (WASM too large) |
| WebSocket transmission | **Fails** (payload too large) |
| Browser-side rendering | **Fails** (never receives assets) |

## Alternative

For 3D visualization in Panel, consider using:
- `pn.pane.VTK` for VTK-based 3D rendering
- `pn.pane.Plotly` with 3D scatter/surface plots
- Custom `ReactiveESM` with Three.js loaded from CDN

## Potential Fix

Support for external ESM module loading (via URL or file path) instead of
inline serialization would allow large bundled widgets like rerun-notebook
to work. Additionally, proxying the asset server through Panel's Tornado
server could enable the `serve-local` mode to function correctly.
""")

info = pn.pane.Markdown("""
## Widget Info

```
rerun-notebook Viewer
WASM size: ~31 MiB (re_viewer_bg.wasm)
Asset loading: CDN / inline / serve-local / custom URL
Key API: rr.init(), rr.log(), rr.notebook_show()
```

The Rerun SDK was imported successfully on the Python side, but we skip
rendering the viewer widget to avoid the WebSocket disconnection.
""")

pn.Column(
    header,
    info,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
