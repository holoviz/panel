"""
ipydeck Example -- deck.gl Map Visualization
=============================================

This example demonstrates using ipydeck's Deck widget with Panel's
AnyWidget pane and bidirectional sync for view state, layers, and
click events.

ipydeck provides an anywidget wrapper around deck.gl, a WebGL-powered
framework for large-scale data visualization on maps. It supports
GeoJSON layers, scatterplot layers, and various base map styles.

GitHub: https://github.com/jtmiclat/ipydeck
Docs:   https://ipydeck.jtmiclat.me/

Key traitlets:
    - initial_view_state (Instance[ViewState]): Map center, zoom, pitch, bearing
    - layers (List): List of Layer objects (GeoJsonLayer, etc.)
    - map_style (Unicode): URL to a MapLibre/Mapbox style JSON
    - click (Dict): Last click event data (synced from browser)
    - height (Union[int, str]): Widget height -- COLLIDES with Panel -> renamed to w_height
    - width (Union[int, str]): Widget width -- COLLIDES with Panel -> renamed to w_width

Required package:
    pip install ipydeck

Run with:
    panel serve research/anywidget/examples/ext_ipydeck.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the deck.gl map renders with a dark basemap
    3. Verify GeoJSON point markers appear on the map (US cities)
    4. Click on a point -- the click event should appear in the sidebar
    5. Use the "Zoom to City" dropdown to change the view
    6. Try switching the base map style
    7. Check the browser console for errors (F12)

Trait Name Collisions:
    - height -> renamed to w_height
    - width -> renamed to w_width
    Both collide with Panel's sizing params and are automatically renamed.
"""

from ipydeck import Deck, GeoJsonLayer, ViewState

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create GeoJSON data for US cities
# ---------------------------------------------------------------------------

CITIES = {
    "San Francisco": {"lon": -122.4194, "lat": 37.7749, "pop": 874961},
    "New York": {"lon": -73.9857, "lat": 40.7484, "pop": 8336817},
    "Chicago": {"lon": -87.6298, "lat": 41.8781, "pop": 2693976},
    "Los Angeles": {"lon": -118.2437, "lat": 34.0522, "pop": 3979576},
    "Houston": {"lon": -95.3698, "lat": 29.7604, "pop": 2320268},
    "Phoenix": {"lon": -112.0740, "lat": 33.4484, "pop": 1680992},
    "Seattle": {"lon": -122.3321, "lat": 47.6062, "pop": 737015},
    "Denver": {"lon": -104.9903, "lat": 39.7392, "pop": 727211},
    "Miami": {"lon": -80.1918, "lat": 25.7617, "pop": 467963},
    "Boston": {"lon": -71.0589, "lat": 42.3601, "pop": 675647},
}

geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [info["lon"], info["lat"]]},
            "properties": {"name": name, "population": info["pop"]},
        }
        for name, info in CITIES.items()
    ],
}

# ---------------------------------------------------------------------------
# 2. Create the Deck widget and wrap with Panel
# ---------------------------------------------------------------------------

layer = GeoJsonLayer(
    data=geojson_data,
    get_fill_color=[0, 200, 255, 180],
    filled=True,
    stroked=True,
    get_line_color=[255, 255, 255, 200],
    get_line_width=2,
    pickable=True,
    point_type="circle",
)

initial_view = ViewState(longitude=-98.5, latitude=39.8, zoom=3, pitch=0, bearing=0)

deck = Deck(
    layers=[layer],
    initial_view_state=initial_view,
    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    height=500,
    width="100%",
)

anywidget_pane = pn.pane.AnyWidget(deck, height=550, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 3. Bidirectional sync: Panel controls -> Deck, click events -> Panel
# ---------------------------------------------------------------------------

BASE_MAP_STYLES = {
    "Dark Matter": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    "Positron (Light)": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    "Voyager": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
}

style_selector = pn.widgets.Select(
    name="Base Map Style",
    options=list(BASE_MAP_STYLES.keys()),
    value="Dark Matter",
    width=280,
)

city_selector = pn.widgets.Select(
    name="Zoom to City",
    options=["Overview (USA)"] + list(CITIES.keys()),
    value="Overview (USA)",
    width=280,
)

# Click event display
click_display = pn.pane.JSON(
    {}, name="Last Click Event", depth=4, height=150, width=280,
)


def on_style_change(event):
    component.map_style = BASE_MAP_STYLES[event.new]


style_selector.param.watch(on_style_change, "value")


def on_city_change(event):
    if event.new == "Overview (USA)":
        new_view = ViewState(longitude=-98.5, latitude=39.8, zoom=3)
    else:
        city = CITIES[event.new]
        new_view = ViewState(longitude=city["lon"], latitude=city["lat"], zoom=10)
    # Re-create the Deck with the new view state
    new_deck = Deck(
        layers=[layer],
        initial_view_state=new_view,
        map_style=BASE_MAP_STYLES[style_selector.value],
        height=500,
        width="100%",
    )
    anywidget_pane.object = new_deck


city_selector.param.watch(on_city_change, "value")


def on_click(event):
    click_display.object = event.new if event.new else {}


component.param.watch(on_click, ["click"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status_banner = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Upstream React error.</strong> ipydeck's ESM bundles React and calls
<code>ReactDOM.render()</code> which triggers <em>Minified React error #185</em>
when targeting Panel's shadow-DOM container. The error indicates the root container
argument is missing or invalid. The deck.gl canvas does not appear.
The <code>height</code> and <code>width</code> traits collide with Panel params
and are renamed to <code>w_height</code> / <code>w_width</code>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipydeck -- deck.gl Map Visualization

**[ipydeck](https://github.com/jtmiclat/ipydeck)** is an anywidget wrapper
around [deck.gl](https://deck.gl/), a WebGL-powered framework for large-scale
data visualization on maps.

## How to Use

1. **Pan and zoom** the map to explore US city locations.
2. **Click a point** on the map -- the click event data appears in the sidebar.
3. **Zoom to a city** using the dropdown to fly to a specific location.
4. **Switch base maps** between Dark Matter, Positron, and Voyager styles.

## Trait Collision Note

The `height` and `width` traitlets collide with Panel's built-in sizing
parameters. They are automatically renamed to `w_height` and `w_width`
on the component. Access via `pane.component.w_height` / `pane.component.w_width`.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("## Map Controls"),
    style_selector,
    city_selector,
    pn.pane.Markdown("## Click Events"),
    pn.pane.Markdown("_Click a point on the map:_"),
    click_display,
    width=320,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### deck.gl Map"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
