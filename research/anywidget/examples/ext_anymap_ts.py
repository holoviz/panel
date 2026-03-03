"""
anymap-ts MapLibreMap — Known Limitation (Large ESM Bundle)
===========================================================

anymap-ts inlines the entire MapLibre GL JS library (~17 MB) into its ``_esm``
string.  Panel serializes ESM via WebSocket, so the 17 MB payload kills the
connection before it arrives.  This is an upstream issue — anymap-ts should
load MapLibre GL JS from a CDN instead of bundling it inline.

GitHub: https://github.com/opengeos/anymap-ts

See: https://github.com/opengeos/anymap-ts/issues/92

For a working map example, see ``leaflet_map.py`` (CDN-loaded Leaflet.js).

Run with: panel serve research/anywidget/examples/ext_anymap_ts.py
"""

from anymap_ts import MapLibreMap  # noqa: F401

import panel as pn

pn.extension()

warning = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
THIS WIDGET DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Reason:</strong> anymap-ts inlines the entire MapLibre GL JS library
(~17 MB) into its ESM string. Panel serializes ESM via WebSocket, so the
17 MB payload kills the connection before it arrives
(<code>Error: Lost websocket connection, 1005</code>).
This is an <strong>upstream anymap-ts issue</strong>.
See <a href="https://github.com/opengeos/anymap-ts/issues/92">opengeos/anymap-ts#92</a>.
For a working map example, see <code>leaflet_map.py</code>.
</p>
</div>
""")

header = pn.pane.Markdown("""
# anymap-ts MapLibreMap — Large ESM Bundle Limitation

[GitHub](https://github.com/opengeos/anymap-ts)

## What Works vs. What Doesn't

| Feature | Status |
|---------|--------|
| Python-side traitlet creation | Works |
| ESM extraction | Works (~17MB extracted) |
| WebSocket transmission | **Fails** (payload too large) |
| Browser-side rendering | **Fails** (never receives ESM) |

## Upstream Fix Needed

The fix belongs upstream: anymap-ts should load MapLibre GL JS from a CDN
(e.g. `import('https://esm.sh/maplibre-gl')`) instead of bundling it inline.
This would reduce the ESM payload from ~17 MB to a few KB.
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
    warning,
    header,
    info,
).servable()
