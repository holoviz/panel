# anymap-ts — Incompatibility with Panel's AnyWidget Pane

## Summary

The `anymap-ts` package inlines the entire MapLibre GL JS library (~17 MB) into its `_esm` string. Panel's AnyWidget pane serializes ESM via WebSocket JSON, and a 17 MB payload exceeds Bokeh's WebSocket transmission limit, causing the connection to drop before the ESM arrives in the browser. This is an upstream bundling issue in anymap-ts.

## Environment
- Panel: latest (PR #8428)
- anymap-ts: 0.13.2
- Python: 3.10+

## Root Cause

anymap-ts bundles the entire MapLibre GL JS library directly into the widget's `_esm` string attribute, resulting in an approximately 17 MB ESM payload. Panel's AnyWidget pane extracts this `_esm` string and sends it as part of a WebSocket JSON message to the browser. Bokeh's WebSocket transport cannot handle a message this large, and the connection closes before the payload can be transmitted:

```
Error: Lost websocket connection, 1005 ()
```

The fix belongs upstream: anymap-ts should load MapLibre GL JS from a CDN (e.g., `import('https://esm.sh/maplibre-gl')`) instead of bundling the entire library inline. This would reduce the ESM payload from ~17 MB to a few KB.

An upstream issue has been filed: [opengeos/anymap-ts#92](https://github.com/opengeos/anymap-ts/issues/92).

## Minimal Reproducible Example

```python
from anymap_ts import MapLibreMap

import panel as pn

pn.extension()

m = MapLibreMap(center=[0, 0], zoom=2, height="400px", width="600px")

# This will fail — ~17 MB ESM payload kills the WebSocket
pn.pane.AnyWidget(m).servable()
```

## Expected vs Actual
- **Expected:** Widget renders in Panel's AnyWidget pane
- **Actual:** The WebSocket connection closes immediately because the ~17 MB ESM payload cannot be transmitted as inline JSON. The browser shows `Error: Lost websocket connection, 1005`. Python-side trait creation works normally; the failure occurs only during browser-side ESM delivery.

## Context

This issue was discovered while testing compatibility of anywidget-based widgets with Panel's `pn.pane.AnyWidget` pane (PR [#8428](https://github.com/holoviz/panel/pull/8428)). The AnyWidget pane provides a Param-integrated wrapper for leaf anywidgets.

## Workaround

Use `pn.pane.IPyWidget` with `pn.extension("ipywidgets")` instead. The `ipywidgets_bokeh` backend uses CDN-based module loading, so the large ESM bundle loads from a URL rather than being inlined in the WebSocket payload.

```python
from anymap_ts import MapLibreMap

import panel as pn

pn.extension("ipywidgets")

m = MapLibreMap(center=[0, 0], zoom=2, height="400px", width="600px")

pn.pane.IPyWidget(m).servable()
```

Alternatively, for a working map in Panel's AnyWidget pane, use a CDN-loaded approach like the `leaflet_map.py` example which loads Leaflet.js from a CDN and keeps the ESM payload small.

## Suggested Fix

**Upstream (anymap-ts):** Load MapLibre GL JS from a CDN instead of bundling it inline:

```javascript
// Instead of bundling the entire library:
// import maplibregl from './maplibre-gl.js'  // ~17 MB inline

// Load from CDN:
const maplibregl = await import('https://esm.sh/maplibre-gl@4')
```

This would reduce the ESM from ~17 MB to a few KB, making it compatible with any WebSocket-based transport.

**Panel side:** Supporting external ESM loading via URL (rather than only inline serialization) would provide a general solution for widgets with large bundles.
