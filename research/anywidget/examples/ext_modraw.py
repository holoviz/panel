"""
modraw Example -- tldraw-based Drawing Widget
==============================================

This example demonstrates using the modraw library's Draw widget
with Panel's AnyWidget pane and bidirectional sync.

modraw is a tldraw-based drawing widget that provides a full whiteboard /
infinite canvas. Unlike the separate `tldraw` package (jupyter-tldraw),
modraw exposes a `base64` trait that syncs the drawing content back to
Python as a base64-encoded PNG image.

GitHub: https://github.com/koaning/modraw
Docs:   https://github.com/koaning/modraw#readme

Key traitlets:
    - width (Int): Canvas width in pixels (default 800)
    - height (Int): Canvas height in pixels (default 500)
    - base64 (Unicode): Base64-encoded PNG of the canvas contents

NOTE: modraw's `width` and `height` traits collide with Panel's Layoutable
params. They are renamed to `w_width` and `w_height` on the component.

Required package:
    pip install modraw

Run with:
    panel serve research/anywidget/examples/ext_modraw.py --port 6115
"""

from modraw import Draw

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Draw widget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

widget = Draw(width=850, height=500)
anywidget_pane = pn.pane.AnyWidget(widget)

# ---------------------------------------------------------------------------
# 2. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# NOTE: modraw's `width` and `height` traits collide with Panel's Layoutable
# params and are renamed to `w_width` and `w_height` on the component.

width_slider = pn.widgets.IntSlider(
    name="Canvas Width (w_width)", start=400, end=1200, value=850, width=300
)
height_slider = pn.widgets.IntSlider(
    name="Canvas Height (w_height)", start=300, end=800, value=500, width=300
)

# Panel -> Widget: set the RENAMED trait params
width_slider.param.watch(
    lambda e: setattr(component, "w_width", e.new), "value"
)
height_slider.param.watch(
    lambda e: setattr(component, "w_height", e.new), "value"
)

# Widget -> Panel: watch the renamed trait params
def on_component_change(*events):
    for event in events:
        if event.name == "w_width":
            width_slider.value = event.new
        elif event.name == "w_height":
            height_slider.value = event.new

component.param.watch(on_component_change, ["w_width", "w_height"])

# Display synced trait values
dim_display = pn.pane.Markdown(pn.bind(
    lambda w, h: f"**Current dimensions:** {w} x {h} px",
    component.param.w_width,
    component.param.w_height,
))

# Show base64 data length (indicator that drawing is being synced)
base64_display = pn.pane.Markdown(pn.bind(
    lambda b: (
        f"**Canvas data:** {'Has content' if b else 'Empty'} "
        f"({len(b):,} chars base64)"
    ),
    component.param.base64,
))

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
Widget renders, tldraw tools work, and canvas data (base64) syncs back
to Python. Unlike the <code>tldraw</code> package, <strong>modraw exposes
the drawing as base64</strong>, enabling Python-side image export.
Width/height sync bidirectionally via renamed traits
(<code>w_width</code>, <code>w_height</code>).
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# modraw -- tldraw-based Drawing Widget

**modraw** is a drawing widget powered by the [tldraw](https://tldraw.dev/) SDK.
It provides a full whiteboard with freehand drawing, shapes, text, and more.

## How to Draw

1. Use the **toolbar** at the bottom to select drawing tools:
   - **Draw** tool for freehand strokes
   - **Shape** tools for rectangles, ellipses, arrows, etc.
   - **Text** tool for adding text
   - **Eraser** for removing elements
2. **Click and drag** on the canvas to draw
3. The canvas content is exported as a base64-encoded PNG and synced to Python

## Key Advantage over jupyter-tldraw

While both `modraw` and `tldraw` (jupyter-tldraw) use the tldraw SDK, **modraw
exports the drawing as a `base64` trait**, making the drawn content accessible
from Python. The `tldraw` package only syncs width/height.

## Panel Controls (bidirectional sync)

- **Canvas Width / Height** sliders resize the canvas via renamed traits
- Dimension values display in real time

## Trait Collision Note

modraw's `width` and `height` traitlets collide with Panel's `Layoutable`
parameters. They are automatically renamed to `w_width` and `w_height` on
the component. Access them via `pane.component.w_width`.

## Testing Instructions

1. Run: `panel serve research/anywidget/examples/ext_modraw.py --port 6115`
2. Verify the tldraw canvas renders with toolbar
3. Draw shapes and freehand strokes -- the "Canvas data" should update
4. Drag the Width/Height sliders -- the canvas should resize
5. Compare with `ext_tldraw.py` -- modraw provides base64 export that tldraw lacks
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    pn.Row(width_slider, height_slider),
    dim_display,
    base64_display,
)

pn.Column(
    status,
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
