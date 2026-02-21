"""
anymap-ts MapLibreMap example — Known Limitation (Large ESM Bundle)
===================================================================

This example documents a known limitation with the anymap-ts widget.
anymap-ts bundles the entire MapLibre GL JS library into its ESM module (~17 MB),
which exceeds what Panel's AnyWidget pane can handle for inline ESM serialization.

The WebSocket connection closes because the 17MB ESM payload is too large to
transmit, resulting in `Error: Lost websocket connection` in the browser.

A lightweight map example (`leaflet_map.py`) is provided as an alternative
that demonstrates the same map interaction patterns without the heavy bundle.

Run with: panel serve research/anywidget/examples/ext_anymap_ts.py
"""

from anymap_ts import MapLibreMap  # noqa: F401

import panel as pn

pn.extension()

header = pn.pane.Markdown("""
# anymap-ts MapLibreMap — Large ESM Bundle Limitation

## The Problem

**anymap-ts** bundles the entire MapLibre GL JS library into its ESM module:
- **ESM size:** ~17 MB of JavaScript
- **CSS size:** ~231 KB

Panel's `AnyWidget` pane serializes ESM as inline JavaScript and sends it via
WebSocket. For bundles this large, the WebSocket connection closes before the
payload can be transmitted:

```
Error: Lost websocket connection, 1005 ()
```

## What Works vs. What Doesn't

| Feature | Status |
|---------|--------|
| Python-side traitlet creation | Works |
| ESM extraction | Works (~17MB extracted) |
| WebSocket transmission | **Fails** (payload too large) |
| Browser-side rendering | **Fails** (never receives ESM) |

## Alternative

See `leaflet_map.py` for a lightweight map example using a custom anywidget
with CDN-loaded Leaflet.js. That example demonstrates the same patterns
(center, zoom, click events, bidirectional sync) without a heavy ESM bundle.

## Potential Fix

Support for external ESM module loading (via URL or file path) instead of
inline serialization would allow large bundled widgets like anymap-ts to work.
This is a future enhancement for Panel's AnyWidgetComponent.
""")

info = pn.pane.Markdown(f"""
## Widget Info

```
anymap-ts MapLibreMap
ESM size: ~17 MB
CSS size: ~231 KB
Traits: center, zoom, style, width, height, current_center, current_zoom, clicked, ...
```

The widget instance was created successfully on the Python side, but we skip
rendering it to avoid the WebSocket disconnection.
""")

pn.Column(
    header,
    info,
).servable()
