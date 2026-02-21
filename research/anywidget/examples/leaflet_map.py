"""
Lightweight Map Example — AnyWidget Pane + CDN Leaflet.js

This example demonstrates a map widget using a custom anywidget with
Leaflet.js loaded from CDN. Unlike anymap-ts (which bundles ~17MB of MapLibre),
this widget loads Leaflet (~40KB) dynamically from CDN, keeping the ESM small.

Features:
- Map centered on New York with zoom control
- Click events captured and synced to Python
- Bidirectional zoom sync with Panel slider
- Lightweight: ESM is ~2KB, Leaflet loaded from CDN

Run with: panel serve research/anywidget/examples/leaflet_map.py
"""

import anywidget
import traitlets

import panel as pn

pn.extension()


class LeafletMapWidget(anywidget.AnyWidget):
    """A lightweight map widget using Leaflet.js from CDN."""

    center_lat = traitlets.Float(40.7128).tag(sync=True)
    center_lng = traitlets.Float(-74.0060).tag(sync=True)
    zoom = traitlets.Int(10).tag(sync=True)
    clicked_lat = traitlets.Float(0.0).tag(sync=True)
    clicked_lng = traitlets.Float(0.0).tag(sync=True)
    click_count = traitlets.Int(0).tag(sync=True)

    _css = """
    /* Fix Leaflet tile rendering in Panel's container */
    .leaflet-tile-pane img {
        position: absolute;
    }
    .leaflet-container {
        overflow: hidden;
    }
    """

    _esm = """
    async function render({ model, el }) {
        // Load Leaflet CSS
        if (!document.querySelector('link[href*="leaflet"]')) {
            let link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
            document.head.appendChild(link);
        }

        // Load Leaflet JS
        if (!window.L) {
            await new Promise((resolve, reject) => {
                let script = document.createElement("script");
                script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        // Create map container with explicit dimensions
        let wrapper = document.createElement("div");
        wrapper.style.width = "800px";
        wrapper.style.height = "500px";
        wrapper.style.position = "relative";

        let mapDiv = document.createElement("div");
        mapDiv.style.width = "800px";
        mapDiv.style.height = "500px";
        mapDiv.style.border = "2px solid #ccc";
        mapDiv.style.borderRadius = "8px";
        wrapper.appendChild(mapDiv);
        el.appendChild(wrapper);

        // Initialize map
        let map = window.L.map(mapDiv).setView(
            [model.get("center_lat"), model.get("center_lng")],
            model.get("zoom")
        );

        // Add tile layer (OpenStreetMap)
        window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Fix tile rendering: invalidate size after container is fully laid out
        setTimeout(function() { map.invalidateSize(); }, 100);
        setTimeout(function() { map.invalidateSize(); }, 500);
        setTimeout(function() { map.invalidateSize(); }, 1000);

        // Click marker
        let clickMarker = null;

        // Handle map clicks
        map.on("click", function(e) {
            model.set("clicked_lat", e.latlng.lat);
            model.set("clicked_lng", e.latlng.lng);
            model.set("click_count", model.get("click_count") + 1);
            model.save_changes();

            // Show marker at click position
            if (clickMarker) {
                clickMarker.setLatLng(e.latlng);
            } else {
                clickMarker = window.L.marker(e.latlng).addTo(map);
            }
            clickMarker.bindPopup(
                "Lat: " + e.latlng.lat.toFixed(4) + "<br>Lng: " + e.latlng.lng.toFixed(4)
            ).openPopup();
        });

        // Handle all map state changes (zoom + move) in one debounced handler
        // to avoid sending partial updates during zoom transitions
        let syncTimeout = null;
        function syncMapState() {
            clearTimeout(syncTimeout);
            syncTimeout = setTimeout(function() {
                let center = map.getCenter();
                let z = map.getZoom();
                if (center && center.lat != null && center.lng != null && z != null) {
                    model.set("zoom", z);
                    model.set("center_lat", center.lat);
                    model.set("center_lng", center.lng);
                    model.save_changes();
                }
            }, 50);
        }

        map.on("zoomend", syncMapState);
        map.on("moveend", syncMapState);

        // Listen for external zoom changes (from Python/Panel)
        let externalUpdate = false;
        model.on("change:zoom", function() {
            let newZoom = model.get("zoom");
            if (!externalUpdate && map.getZoom() !== newZoom) {
                externalUpdate = true;
                map.setZoom(newZoom);
                setTimeout(function() { externalUpdate = false; }, 500);
            }
        });

        // Listen for external center changes (from Python/Panel)
        model.on("change:center_lat", function() {
            let lat = model.get("center_lat");
            let lng = model.get("center_lng");
            let current = map.getCenter();
            if (Math.abs(current.lat - lat) > 0.0001 || Math.abs(current.lng - lng) > 0.0001) {
                map.setView([lat, lng], map.getZoom());
            }
        });
        model.on("change:center_lng", function() {
            let lat = model.get("center_lat");
            let lng = model.get("center_lng");
            let current = map.getCenter();
            if (Math.abs(current.lat - lat) > 0.0001 || Math.abs(current.lng - lng) > 0.0001) {
                map.setView([lat, lng], map.getZoom());
            }
        });
    }
    export default { render };
    """


# Create the map widget and pane
map_widget = LeafletMapWidget()
map_pane = pn.pane.AnyWidget(map_widget)

# pane.component is available immediately — use param API
component = map_pane.component

# Panel controls for bidirectional sync using pn.bind on component params
zoom_slider = pn.widgets.IntSlider(
    name="Zoom Level",
    start=1,
    end=19,
    value=map_widget.zoom,
    step=1,
)

center_display = pn.pane.Markdown(pn.bind(
    lambda lat, lng: f"**Center:** Lat {lat:.4f}, Lng {lng:.4f}",
    component.param.center_lat, component.param.center_lng
))

click_display = pn.pane.Markdown(pn.bind(
    lambda lat, lng, count: (
        f"**Last click:** Lat {lat:.4f}, Lng {lng:.4f} (click #{count})"
        if count > 0
        else "**Last click:** (click on the map)"
    ),
    component.param.clicked_lat, component.param.clicked_lng, component.param.click_count
))

# Bidirectional zoom sync via param API
component.param.watch(lambda e: setattr(zoom_slider, 'value', e.new), ['zoom'])
zoom_slider.param.watch(lambda e: setattr(component, 'zoom', e.new), ['value'])

# Layout
header = pn.pane.Markdown("""
# Leaflet Map Example — AnyWidget Pane + CDN Loading

This example demonstrates a **lightweight map** using a custom anywidget with
[Leaflet.js](https://leafletjs.com) loaded from CDN (~40KB). Unlike anymap-ts
(which bundles ~17MB of MapLibre), this widget keeps its ESM small (~2KB) and
loads the mapping library dynamically.

**Try it:**
1. **Pan and zoom** the map — center and zoom update in the Panel widgets below.
2. **Click on the map** — a marker appears and the click coordinates are displayed.
3. **Drag the zoom slider** — the map zooms to the selected level.
""")

pn.Column(
    header,
    pn.pane.Markdown("### Anywidget (browser-side Leaflet map)"),
    map_pane,
    pn.pane.Markdown("### Panel Widgets (Python-side controls)"),
    zoom_slider,
    center_display,
    click_display,
).servable()
