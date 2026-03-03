"""
Playwright test for the leaflet map anywidget example.

Tests:
    1. Widget renders (map container appears)
    2. No unexpected console errors
    3. Browser -> Python sync (click on map, coordinates update in Python)
    4. Python -> Browser sync (change zoom from Python, map zooms)

Note: These tests load Leaflet.js from CDN, so they require network access.
"""
import anywidget
import pytest
import traitlets

import panel as pn

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# --- Widget definition (simplified from research/anywidget/examples/leaflet_map.py) ---

class LeafletMapWidget(anywidget.AnyWidget):
    center_lat = traitlets.Float(40.7128).tag(sync=True)
    center_lng = traitlets.Float(-74.0060).tag(sync=True)
    zoom = traitlets.Int(10).tag(sync=True)
    clicked_lat = traitlets.Float(0.0).tag(sync=True)
    clicked_lng = traitlets.Float(0.0).tag(sync=True)
    click_count = traitlets.Int(0).tag(sync=True)

    _css = """
    .leaflet-tile-pane img { position: absolute; }
    .leaflet-container { overflow: hidden; }
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

        let mapDiv = document.createElement("div");
        mapDiv.style.width = "600px";
        mapDiv.style.height = "400px";
        mapDiv.style.border = "2px solid #ccc";
        mapDiv.className = "leaflet-map-test";
        el.appendChild(mapDiv);

        let map = window.L.map(mapDiv).setView(
            [model.get("center_lat"), model.get("center_lng")],
            model.get("zoom")
        );

        window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        setTimeout(function() { map.invalidateSize(); }, 200);

        let clickMarker = null;

        map.on("click", function(e) {
            model.set("clicked_lat", e.latlng.lat);
            model.set("clicked_lng", e.latlng.lng);
            model.set("click_count", model.get("click_count") + 1);
            model.save_changes();

            if (clickMarker) {
                clickMarker.setLatLng(e.latlng);
            } else {
                clickMarker = window.L.marker(e.latlng).addTo(map);
            }
        });

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

        let externalUpdate = false;
        model.on("change:zoom", function() {
            let newZoom = model.get("zoom");
            if (!externalUpdate && map.getZoom() !== newZoom) {
                externalUpdate = true;
                map.setZoom(newZoom);
                setTimeout(function() { externalUpdate = false; }, 500);
            }
        });
    }
    export default { render };
    """


def test_leaflet_map_renders(page):
    """Map widget renders and Leaflet container is visible."""
    widget = LeafletMapWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Wait for Leaflet to load and render the map container
    map_div = page.locator(".leaflet-map-test")
    expect(map_div).to_be_visible(timeout=15000)

    # Leaflet adds .leaflet-container class when initialized
    leaflet_container = page.locator(".leaflet-container")
    expect(leaflet_container).to_be_visible(timeout=15000)

    assert_no_console_errors(msgs)


def test_leaflet_map_click_syncs(page):
    """Clicking on the map updates click coordinates in Python (browser -> Python sync)."""
    widget = LeafletMapWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    leaflet_container = page.locator(".leaflet-container")
    expect(leaflet_container).to_be_visible(timeout=15000)

    # Wait for map tiles to start loading
    page.wait_for_timeout(1000)

    assert widget.click_count == 0

    # Click on the center of the map
    leaflet_container.click()

    # Wait for Python-side click_count to update
    wait_until(lambda: widget.click_count == 1, page, timeout=10000)
    assert pane.component.click_count == 1
    assert widget.clicked_lat != 0.0 or widget.clicked_lng != 0.0

    assert_no_console_errors(msgs)


def test_leaflet_map_python_zoom(page):
    """Changing zoom from Python updates the map (Python -> browser sync)."""
    widget = LeafletMapWidget(zoom=10)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    leaflet_container = page.locator(".leaflet-container")
    expect(leaflet_container).to_be_visible(timeout=15000)

    # Wait for initial render
    page.wait_for_timeout(1000)

    # Change zoom from Python
    pane.component.zoom = 5

    # Wait for the zoom to propagate back after the map animation
    wait_until(lambda: widget.zoom == 5, page, timeout=10000)

    assert_no_console_errors(msgs)
