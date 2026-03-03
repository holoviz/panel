"""
pylifemap Example -- Tree of Life Visualization
=================================================

This example demonstrates using pylifemap's Lifemap with Panel's
AnyWidget pane. Pylifemap visualizes the NCBI taxonomy tree of life
using an interactive map interface powered by Leaflet.

IMPORTANT: The top-level `pylifemap.Lifemap` class is NOT an anywidget.
It is a plain Python object that builds a configuration and then creates
an internal anywidget via its `_to_widget()` method. Panel's AnyWidget
pane wraps this internal widget (LifemapWidgetNoDeck or LifemapWidgetDeck).

GitHub: https://github.com/juba/pylifemap
Docs:   https://juba.github.io/pylifemap/

Key traitlets (on the internal LifemapWidget):
    - data (Dict): Serialized layer data for visualization
    - layers (List): Layer configuration
    - options (Dict): Map options (center, zoom, theme, controls)
    - color_ranges (Dict): Color range definitions
    - height (Unicode): Widget height as CSS string -- COLLIDES -> renamed to w_height
    - width (Unicode): Widget width as CSS string -- COLLIDES -> renamed to w_width

Required package:
    pip install pylifemap

Run with:
    panel serve research/anywidget/examples/ext_pylifemap.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the tree of life map renders (Leaflet-based world map of taxonomy)
    3. Pan and zoom the map to explore the tree
    4. Try switching the theme using the dropdown
    5. Adjust the zoom level slider
    6. Check the browser console for errors (F12)

Trait Name Collisions:
    - height -> renamed to w_height
    - width -> renamed to w_width
    Both collide with Panel's sizing params and are automatically renamed.
"""

from pylifemap import Lifemap

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Lifemap and extract the anywidget
# ---------------------------------------------------------------------------
# pylifemap.Lifemap is NOT an anywidget itself. We use its internal
# _to_widget() method to get the actual anywidget instance.

THEMES = ("dark", "light", "lightblue", "lightgrey", "lightgreen")


def create_lifemap_widget(theme="dark", zoom=5, width=800, height=500):
    """Create a pylifemap widget with the given settings."""
    lm = Lifemap(
        width=width,
        height=height,
        theme=theme,
        zoom=zoom,
    )
    return lm._to_widget()


# Start with dark theme
widget = create_lifemap_widget(theme="dark")

anywidget_pane = pn.pane.AnyWidget(widget, height=550, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Panel controls
# ---------------------------------------------------------------------------

theme_selector = pn.widgets.Select(
    name="Theme",
    options=list(THEMES),
    value="dark",
    width=280,
)

zoom_slider = pn.widgets.IntSlider(
    name="Initial Zoom",
    start=1,
    end=10,
    step=1,
    value=5,
    width=280,
)

# Trait display
trait_display = pn.pane.JSON(
    {
        "options": widget.options,
        "w_height": getattr(component, "w_height", "N/A"),
        "w_width": getattr(component, "w_width", "N/A"),
        "num_layers": len(widget.layers),
    },
    name="Synced Traits",
    depth=3,
    width=280,
)


def on_settings_change(*events):
    """Re-create the widget when theme or zoom changes."""
    new_widget = create_lifemap_widget(
        theme=theme_selector.value,
        zoom=zoom_slider.value,
    )
    anywidget_pane.object = new_widget
    trait_display.object = {
        "options": new_widget.options,
        "w_height": new_widget.height,
        "w_width": new_widget.width,
        "num_layers": len(new_widget.layers),
    }


theme_selector.param.watch(on_settings_change, "value")
zoom_slider.param.watch(on_settings_change, "value")

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status_banner = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
The tree of life map renders via the internal anywidget extracted with
<code>Lifemap._to_widget()</code>. The top-level <code>pylifemap.Lifemap</code>
class is <strong>not</strong> an anywidget itself, so a workaround is needed.
Theme and zoom changes require re-creating the widget.
The <code>height</code> and <code>width</code> traits collide with Panel params
and are renamed to <code>w_height</code> / <code>w_width</code>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# pylifemap -- Tree of Life Map

**[pylifemap](https://github.com/juba/pylifemap)** visualizes the NCBI
taxonomy tree of life on an interactive Leaflet-based map. Species, genera,
families, and higher taxa are placed on a 2D projection of the tree.

## How to Use

1. **Pan and zoom** the map to explore the tree of life.
2. **Switch themes** using the dropdown (dark, light, lightblue, etc.).
3. **Adjust zoom** using the slider (re-creates the widget).

## Workaround Note

`pylifemap.Lifemap` is a configuration builder, not an anywidget.
To use it with `pn.pane.AnyWidget`, call `lifemap._to_widget()` to
get the internal `LifemapWidgetNoDeck` or `LifemapWidgetDeck` anywidget.
This is a private API and may change in future versions of pylifemap.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("## Map Settings"),
    theme_selector,
    zoom_slider,
    pn.pane.Markdown("## Synced Traits"),
    trait_display,
    width=320,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Tree of Life"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
