# Rerun SDK Viewer — Incompatibility with Panel's AnyWidget Pane

## Summary

The `rerun-notebook` package bundles the entire Rerun Viewer compiled to WebAssembly (~31 MiB for `re_viewer_bg.wasm`) plus a JavaScript glue file. Panel's AnyWidget pane serializes ESM as inline JavaScript and sends it over WebSocket. A payload this large exceeds Bokeh's WebSocket JSON transmission limit, causing the connection to drop before the assets arrive in the browser.

## Environment
- Panel: latest (PR #8428)
- rerun-sdk: 0.29.2 (with `[notebook]` extra)
- Python: 3.10+

## Root Cause

Panel's AnyWidget pane extracts the widget's `_esm` source and inlines it into a WebSocket JSON message sent to the browser. The rerun-notebook widget's assets include:

- **`re_viewer_bg.wasm`**: ~31 MiB WebAssembly binary containing the full Rerun Viewer
- **`widget.js`**: JavaScript glue code that loads and initializes the WASM module

When these assets are serialized into the WebSocket JSON payload, the message size far exceeds what Bokeh's WebSocket transport can handle. The connection closes with:

```
Error: Lost websocket connection, 1005 ()
```

The rerun-notebook package supports alternative asset loading modes via the `RERUN_NOTEBOOK_ASSET` environment variable (`inline`, `serve-local`, remote CDN, custom URL), but these modes rely on anywidget's internal asset resolution and file serving mechanisms, which are not available through Panel's AnyWidget pane.

## Minimal Reproducible Example

```python
import rerun as rr

import panel as pn

pn.extension()

rec = rr.memory_recording()
rr.init("example", recording=rec)
rr.log("point", rr.Points3D([[0, 0, 0], [1, 1, 1]]))

viewer = rec.show(width=800, height=600)

# This will fail — ~31 MiB WASM payload kills the WebSocket
pn.pane.AnyWidget(viewer).servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** The WebSocket connection closes immediately because the ~31 MiB WASM binary plus glue JavaScript cannot be transmitted as an inline JSON payload. The browser shows `Error: Lost websocket connection, 1005`.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead. The `ipywidgets_bokeh` backend uses CDN-based module loading, so the WASM binary loads from a URL rather than being inlined in the WebSocket payload.

```python
import rerun as rr

import panel as pn

pn.extension("ipywidgets")

rec = rr.memory_recording()
rr.init("example", recording=rec)
rr.log("point", rr.Points3D([[0, 0, 0], [1, 1, 1]]))

viewer = rec.show(width=800, height=600)

pn.pane.IPyWidget(viewer).servable()
```

## Suggested Fix

Two approaches could address this on Panel's side:

1. **External ESM module loading**: Support loading ESM from a URL or local file path instead of inlining it in the WebSocket JSON. This would allow large bundled widgets to serve their assets separately.
2. **Asset server proxying**: Proxy the widget's asset server through Panel's Tornado server, enabling rerun-notebook's `serve-local` mode to function correctly. This would allow the WASM binary to be fetched via HTTP rather than transmitted via WebSocket.

On the upstream side, rerun-notebook could provide an option to load assets from a user-specified CDN URL without relying on anywidget's internal asset resolution.
