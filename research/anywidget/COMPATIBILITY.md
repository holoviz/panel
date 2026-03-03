# AnyWidget Compatibility Guide for Panel

This document provides a systematic overview of anywidget compatibility with Panel's `AnyWidget` pane. It covers what works, what doesn't, known issues, and workarounds.

## Quick Start

```python
import panel as pn

pn.extension()

# For any anywidget-based widget:
widget = SomeAnyWidget()
pane = pn.pane.AnyWidget(widget)
pane.servable()

# Access synced parameters via the component:
component = pane.component
component.param.watch(callback, ["some_trait"])
```

## Compatibility Matrix

### Fully Working

| Widget | Package | Install | Bidirectional Sync | Notes |
|--------|---------|---------|-------------------|-------|
| Custom inline widgets | N/A | N/A | YES | Counter, slider, multi-trait, styled card, canvas draw, toggle theme, leaflet map, todo list |
| Altair JupyterChart | `altair` | `pip install altair` | Python→Browser | Vega-Lite charts render correctly |
| drawdata ScatterWidget | `drawdata` | `pip install drawdata` | YES | Known `circle_brush` init error in console (upstream bug, harmless) |
| Mosaic MosaicWidget | `mosaic-widget` | `pip install mosaic-widget` | YES | DuckDB-WASM queries, interactive selections sync via `params` |
| ipyaladin AladinLite | `ipyaladin` | `pip install ipyaladin` | Python→Browser | Some console warnings from CDN loading (harmless) |

### Working with Caveats

| Widget | Package | Issue | Workaround |
|--------|---------|-------|------------|
| jupyter-scatter | `jupyter-scatter` | WebGL canvas sizing in shadow DOM may cause crash on first render | Set explicit `height` on the pane: `pn.pane.AnyWidget(widget, height=500)` |
| pygv Browser | `pygv` | ESM reads config once; no bidirectional sync of navigation state | Replace `pane.object` with a new Browser instance to navigate |
| wigglystuff | `wigglystuff` | TangleSlider, Dial, Slider work. Canvas-based components (RangeSlider, etc.) have ESM issues | Use the components that work; avoid canvas-based ones |

### Requires Configuration

| Widget | Package | Requirement | Solution |
|--------|---------|-------------|----------|
| quak | `quak` | SharedArrayBuffer (COOP/COEP headers) | Use `transforms=[SecurityHeadersTransform]` with `pn.serve()` |

### Not Compatible (Use IPyWidget pane instead)

| Widget | Package | Reason | Alternative |
|--------|---------|--------|-------------|
| lonboard | `lonboard` | Compound widget — uses `IPY_MODEL_` references for child widgets (layers, controls, basemap). Requires full `WidgetManager` with `get_model()` | `pn.extension("ipywidgets"); pn.pane.IPyWidget(widget)` |

### Known Upstream Issues

| Widget | Package | Issue | Status |
|--------|---------|-------|--------|
| tldraw | `tldraw` | ESM uses `_asyncOptionalChain` from Sucrase, incompatible with `es-module-shims` | Upstream ESM bundling issue |
| drawdata | `drawdata` | `circle_brush` init error on first render | Harmless, widget works after init |

## Architecture: How the AnyWidget Pane Works

### Trait-to-Param Mapping

Panel's AnyWidget pane extracts traitlets from the anywidget instance and creates corresponding `param.Parameter` objects on a dynamic `AnyWidgetComponent` subclass. This enables full Param ecosystem integration (`param.watch`, `pn.bind`, `.rx`).

### Trait Name Collision Handling

When a traitlet name collides with Panel's built-in parameter names (e.g., `height`, `width`, `connect`), the pane renames the parameter with a `w_` prefix:

```python
pane = pn.pane.AnyWidget(widget)
component = pane.component

# Original trait "height" → renamed to "w_height"
component.w_height = 500

# Check the full mapping:
print(component._trait_name_map)
# {'height': 'w_height', 'width': 'w_width', 'connect': 'w_connect', ...}
```

The adapter on the JavaScript side transparently translates between the original trait names (used by the ESM) and the renamed parameter names.

### Binary Data Transfer

Binary data (e.g., Arrow buffers, numpy arrays) is transferred via base64 encoding:

- **Python → Browser**: `memoryview`/`bytes` values are base64-encoded as `{_pnl_bytes: "..."}` in JSON, then decoded to `DataView` on the JS side.
- **Browser → Python**: `DataView`/`TypedArray` values are converted to `ArrayBuffer` for Bokeh's `bp.Bytes` transport.
- **Messages**: `model.send(content, callbacks, buffers)` base64-encodes any `ArrayBuffer`/`DataView` buffers under a `_b64_buffers` key.

### ESM Loading

Widget ESM code is loaded via `es-module-shims` (`importShim()`), which supports import maps. The ESM is compiled with Sucrase (TypeScript/JSX transforms) before loading. For widgets with large bundles, the ESM is inlined in the WebSocket JSON message.

### What Makes a Widget Compatible?

A widget works with Panel's AnyWidget pane if it:

1. **Is a leaf widget** — has flat, JSON-serializable traits (not `IPY_MODEL_` references to child widgets)
2. **Uses standard anywidget protocol** — `model.get()`, `model.set()`, `model.save_changes()`, `model.on()`, `model.off()`
3. **Has ESM compatible with `es-module-shims`** — no Sucrase helper function issues
4. **Doesn't require Jupyter kernel** — no `comm` channels, no `widget_manager`

### What Makes a Widget Incompatible?

1. **Compound widgets** (e.g., lonboard) — reference child widgets via `IPY_MODEL_<id>` strings
2. **Kernel-dependent widgets** — require Jupyter comm channels or full `WidgetManager`
3. **ESM compatibility issues** — Sucrase helper functions, CDN-only modules that need CORS
4. **Binary transport via comm channels** — widgets that send large binary data through ipywidgets' native binary comm protocol

## Comparison with Other Environments

### vs. Jupyter

Jupyter provides a full kernel with `WidgetManager`, `CommManager`, and native binary transport. All anywidgets work in Jupyter, including compound widgets.

Panel's AnyWidget pane provides **Param ecosystem integration** (reactive parameters, `param.watch`, `pn.bind`, `.rx`) that Jupyter doesn't have, but cannot support compound widgets.

### vs. Marimo

Marimo replaces the widget's `comm` object while keeping traitlets as the authority. Panel maps traitlets to Param parameters. Both approaches work for leaf anywidgets.

Key differences:
- Marimo: dirty-field tracking in `save_changes()`, content-hash ESM dedup
- Panel: full Param ecosystem integration, trait name collision handling

### vs. IPyWidget pane (`pn.pane.IPyWidget`)

Panel's `IPyWidget` pane (using `ipywidgets_bokeh`) provides full Jupyter kernel emulation inside the Bokeh server. It supports compound widgets, binary transport, and `WidgetManager`. Use it for widgets that don't work with the AnyWidget pane.

| Feature | AnyWidget pane | IPyWidget pane |
|---------|---------------|----------------|
| Param integration | Full (`param.watch`, `.rx`, `pn.bind`) | Limited |
| Compound widgets | No | Yes |
| Binary transport | Via base64 | Native |
| Kernel required | No | Yes (ipywidgets_bokeh) |
| ESM loading | `es-module-shims` | CDN/requirejs |
| Performance | Better for simple widgets | Better for complex widgets |

## Troubleshooting

### Widget doesn't render

1. Check browser console for errors
2. Verify the widget is a leaf anywidget (not a compound widget)
3. Try setting explicit dimensions: `pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")`
4. Check if the ESM bundle has compatibility issues with `es-module-shims`

### Trait values don't sync

1. Check `pane.component._trait_name_map` for renamed traits
2. Access renamed traits via `component.w_<name>` (e.g., `component.w_height`)
3. Verify the trait type is JSON-serializable

### Console errors but widget works

Some widgets produce harmless console errors during initialization (e.g., drawdata's `circle_brush` error). If the widget renders and functions correctly, these can be safely ignored.

### SharedArrayBuffer not available

Widgets using DuckDB-WASM or WebAssembly may need COOP/COEP headers:

```python
import tornado.web

class SecurityHeadersTransform(tornado.web.OutputTransform):
    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return status_code, headers, chunk

pn.serve(app, transforms=[SecurityHeadersTransform])
```
