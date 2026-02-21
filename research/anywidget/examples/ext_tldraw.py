"""
jupyter-tldraw Example — Free Whiteboard in Panel
===================================================

This example demonstrates using jupyter-tldraw's TldrawWidget (a free
whiteboard / infinite canvas) with Panel's AnyWidget pane.

The TldrawWidget provides a full drawing canvas with tools for freehand
drawing, shapes, text, and more — powered by the tldraw SDK.

Key traitlets:
    - width (Int): Widget width in pixels (default 800)
    - height (Int): Widget height in pixels (default 500)

Required package:
    pip install tldraw

Run with:
    panel serve research/anywidget/examples/ext_tldraw.py
"""

from tldraw import TldrawWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the TldrawWidget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

widget = TldrawWidget(width=900, height=550)
anywidget_pane = pn.pane.AnyWidget(widget)

# ---------------------------------------------------------------------------
# 2. Panel controls for widget dimensions
# ---------------------------------------------------------------------------

component = anywidget_pane.component

width_slider = pn.widgets.IntSlider(
    name="Canvas Width", start=400, end=1200, value=900, width=300
)
height_slider = pn.widgets.IntSlider(
    name="Canvas Height", start=300, end=800, value=550, width=300
)

# Panel -> Widget (through component params)
width_slider.param.watch(
    lambda e: setattr(component, "width", e.new), "value"
)
height_slider.param.watch(
    lambda e: setattr(component, "height", e.new), "value"
)

# Widget -> Panel (through component param.watch)
def on_component_change(*events):
    for event in events:
        if event.name == "width":
            width_slider.value = event.new
        elif event.name == "height":
            height_slider.value = event.new

component.param.watch(on_component_change, ["width", "height"])

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# jupyter-tldraw — Free Whiteboard in Panel

**tldraw** is a free whiteboard / infinite canvas powered by the
[tldraw SDK](https://tldraw.dev/). This example renders it natively
in Panel using the `AnyWidget` pane.

## Drawing Tools

Use the toolbar at the top to:
- **Select** and move shapes
- **Draw** freehand lines
- Create **rectangles**, **ellipses**, **arrows**, and **text**
- **Erase** elements
- Use **sticky notes** and more

## Bidirectional Sync

The width and height sliders below control the canvas dimensions.
Changes sync bidirectionally between Panel sliders and the widget.
""", sizing_mode="stretch_width")

controls = pn.Row(width_slider, height_slider)

pn.Column(
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
