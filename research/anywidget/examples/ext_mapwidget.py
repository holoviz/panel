"""
mapwidget Example -- MapLibre GL Interactive Maps
==================================================

This example demonstrates using mapwidget's MapLibre Map widget
with Panel's AnyWidget pane and bidirectional sync between the
widget and Panel controls.

mapwidget provides MapLibre GL JS maps as anywidget-based widgets.
The map loads tiles from the network and supports pan, zoom, and
click interactions.

GitHub: https://github.com/eoda-dev/py-maplibregl
Docs:   https://eoda-dev.github.io/py-maplibregl/

Key traitlets:
    - center (List): [lat, lng] center point
    - zoom (Float): Zoom level
    - bounds (List): Map bounds [[sw_lat, sw_lng], [ne_lat, ne_lng]]
    - clicked_latlng (List): Last clicked [lat, lng] or [None, None]
    - height (Unicode): Height string like "400px" (collides with Panel)
    - width (Unicode): Width string like "600px" (collides with Panel)
    - calls (List): List of method calls to execute on the map

NOTE: The ``height`` and ``width`` traitlets collide with Panel's
Layoutable params, so they are renamed to ``w_height`` and ``w_width``
on the component. Dimension forwarding will handle sizing.

Required package:
    pip install mapwidget

Run with:
    panel serve research/anywidget/examples/ext_mapwidget.py
"""

import mapwidget.maplibre as maplibre

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the MapLibre Map widget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

# NOTE: width="100%" doesn't work well in Panel's shadow DOM because
# the parent container may not have explicit width. Use pixel values instead.
widget = maplibre.Map(center=[40, -100], zoom=4, height="500px", width="800px")
anywidget_pane = pn.pane.AnyWidget(widget, width=820, height=520)

# ---------------------------------------------------------------------------
# 2. Wire up Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# MapLibre GL CSS needs to be inside the shadow DOM for proper rendering.
# The ESM loads it into document.head, but that's outside the shadow DOM.
component._stylesheets = list(component._stylesheets) + [
    "https://unpkg.com/maplibre-gl@5.5.0/dist/maplibre-gl.css"
]

# --- Latitude / Longitude sliders ---
lat_slider = pn.widgets.FloatSlider(
    name="Latitude", start=-90, end=90, value=40, step=0.5, width=300
)
lng_slider = pn.widgets.FloatSlider(
    name="Longitude", start=-180, end=180, value=-100, step=0.5, width=300
)
zoom_slider = pn.widgets.FloatSlider(
    name="Zoom", start=1, end=18, value=4, step=0.5, width=300
)

# Panel -> Widget: mapwidget ESM doesn't listen for "change:center" or
# "change:zoom" directly. Instead, it supports a `calls` trait that invokes
# map methods (e.g. map.setCenter(), map.setZoom(), map.flyTo()).
# We use this mechanism to drive the map from Python.
def on_lat_change(event):
    lng = lng_slider.value
    component.calls = [{"method": "setCenter", "args": [[lng, event.new]]}]

def on_lng_change(event):
    lat = lat_slider.value
    component.calls = [{"method": "setCenter", "args": [[event.new, lat]]}]

def on_zoom_change(event):
    component.calls = [{"method": "setZoom", "args": [event.new]}]

lat_slider.param.watch(on_lat_change, "value")
lng_slider.param.watch(on_lng_change, "value")
zoom_slider.param.watch(on_zoom_change, "value")

# Widget -> Panel (through component param.watch):
def on_component_change(*events):
    for event in events:
        if event.name == "center":
            center = event.new
            if center and len(center) >= 2:
                lat_slider.value = round(center[0], 2)
                lng_slider.value = round(center[1], 2)
        elif event.name == "zoom":
            zoom_slider.value = round(event.new, 1)

component.param.watch(on_component_change, ["center", "zoom"])

# --- Click display ---
click_display = pn.pane.Markdown(
    "**Clicked:** None (click on the map)", sizing_mode="stretch_width"
)

def on_click_change(*events):
    for event in events:
        if event.name == "clicked_latlng":
            latlng = event.new
            if latlng and len(latlng) >= 2 and latlng[0] is not None:
                click_display.object = (
                    f"**Clicked:** ({latlng[0]:.4f}, {latlng[1]:.4f})"
                )
            else:
                click_display.object = "**Clicked:** None"

component.param.watch(on_click_change, ["clicked_latlng"])

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# mapwidget MapLibre GL -- Interactive Map in Panel

**mapwidget** provides MapLibre GL JS maps as anywidget-based widgets.
The map renders interactive vector tiles with smooth panning and zooming.

## How to Interact

- **Pan:** Click and drag to move the map
- **Zoom:** Scroll to zoom in/out, or use the zoom slider
- **Click:** Click on the map to see coordinates in the "Clicked" readout
- **Controls:** Use the sliders to set latitude, longitude, and zoom level

## Bidirectional Sync

The sliders below are bidirectionally synced with the map. Moving the map
updates the sliders, and moving the sliders updates the map.

## Testing Instructions

1. Verify the map renders with tiles visible
2. Drag the Latitude slider -- the map should pan north/south
3. Drag the Longitude slider -- the map should pan east/west
4. Drag the Zoom slider -- the map should zoom in/out
5. Pan the map by dragging -- sliders should update
6. Click on the map -- coordinates should appear in the "Clicked" readout
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Map Controls"),
    lat_slider,
    lng_slider,
    zoom_slider,
    pn.pane.Markdown("### Interaction Feedback"),
    click_display,
    width=350,
)

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
MapLibre GL map renders with interactive tiles. Bidirectional sync works for
<code>center</code>, <code>zoom</code>, and <code>clicked_latlng</code>.
Python-to-browser navigation uses the <code>calls</code> trait pattern
(e.g. <code>setCenter</code>, <code>setZoom</code>).
MapLibre CSS is injected into the shadow DOM via <code>_stylesheets</code>.
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### MapLibre GL Map"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
