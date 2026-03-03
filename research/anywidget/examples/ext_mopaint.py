"""
mopaint Example -- MS Paint-like Drawing Canvas
================================================

This example demonstrates using the mopaint library's Paint widget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

mopaint provides a simple MS Paint-like drawing interface with tools
for freehand drawing, thick marker, eraser, and color selection. The
drawing can be exported as a PIL Image or base64 string.

GitHub: https://github.com/koaning/mopaint
Docs:   https://github.com/koaning/mopaint#readme

Key traitlets:
    - width (Int): Canvas width in pixels (default 889)
    - height (Int): Canvas height in pixels (default 500)
    - base64 (Unicode): Base64-encoded PNG of the canvas contents
    - store_background (Bool): Include white background in export (default True)

NOTE: mopaint's `width` and `height` traits collide with Panel's Layoutable
params. They are renamed to `w_width` and `w_height` on the component.

Required package:
    pip install mopaint

Run with:
    panel serve research/anywidget/examples/ext_mopaint.py --port 6114
"""

from mopaint import Paint

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Paint widget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

widget = Paint(width=750, height=450)
anywidget_pane = pn.pane.AnyWidget(widget)

# ---------------------------------------------------------------------------
# 2. Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# NOTE: mopaint's `width` and `height` traits collide with Panel's Layoutable
# params and are renamed to `w_width` and `w_height` on the component.

width_slider = pn.widgets.IntSlider(
    name="Canvas Width (w_width)", start=400, end=1200, value=750, width=300
)
height_slider = pn.widgets.IntSlider(
    name="Canvas Height (w_height)", start=200, end=800, value=450, width=300
)
store_bg_toggle = pn.widgets.Toggle(
    name="Store Background", value=True, width=200,
    button_type="success",
)

# Panel -> Widget: set the RENAMED trait params
width_slider.param.watch(
    lambda e: setattr(component, "w_width", e.new), "value"
)
height_slider.param.watch(
    lambda e: setattr(component, "w_height", e.new), "value"
)
store_bg_toggle.param.watch(
    lambda e: setattr(component, "store_background", e.new), "value"
)

# Widget -> Panel: watch the renamed trait params
def on_component_change(*events):
    for event in events:
        if event.name == "w_width":
            width_slider.value = event.new
        elif event.name == "w_height":
            height_slider.value = event.new
        elif event.name == "store_background":
            store_bg_toggle.value = event.new

component.param.watch(on_component_change, ["w_width", "w_height", "store_background"])

# Display synced trait values
dim_display = pn.pane.Markdown(pn.bind(
    lambda w, h, bg: (
        f"**Dimensions:** {w} x {h} px | "
        f"**Store Background:** {bg}"
    ),
    component.param.w_width,
    component.param.w_height,
    component.param.store_background,
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
Widget renders, drawing tools work, and canvas data (base64) syncs back
to Python. Width/height sync bidirectionally via renamed traits
(<code>w_width</code>, <code>w_height</code>).
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# mopaint -- MS Paint-like Drawing Canvas

**mopaint** provides a simple Paint-like drawing interface in the browser.

## How to Draw

1. **Select a tool** from the toolbar: Brush, Thick Marker, or Eraser
2. **Pick a color** from the color palette
3. **Draw** on the canvas by clicking and dragging
4. The base64-encoded canvas contents sync back to Python in real time

## Panel Controls (bidirectional sync)

- **Canvas Width / Height** sliders resize the canvas
- **Store Background** toggle controls whether the white background is
  included when exporting the image

## Trait Collision Note

mopaint's `width` and `height` traitlets collide with Panel's `Layoutable`
parameters. They are automatically renamed to `w_width` and `w_height` on
the component. Access them via `pane.component.w_width` or check
`pane.component._trait_name_map`.

## Testing Instructions

1. Run: `panel serve research/anywidget/examples/ext_mopaint.py --port 6114`
2. Verify the drawing canvas renders with toolbar (brush, marker, eraser, colors)
3. Draw on the canvas -- the "Canvas data" indicator should update
4. Drag the Width/Height sliders -- the canvas should resize
5. Toggle "Store Background" and verify the value updates
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    pn.Row(width_slider, height_slider),
    store_bg_toggle,
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
