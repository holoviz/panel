"""
ipymafs Example -- Interactive Math Visualizations
=====================================================

This example demonstrates using ipymafs with Panel's AnyWidget pane.
ipymafs provides interactive math function visualizations built on
the Mafs JavaScript library (https://mafs.dev/).

GitHub: https://github.com/nickmcintyre/ipymafs

Available widget classes:
    - Line: Renders a line from the origin to a point defined by ``my_vector``
    - Bezier: Renders an interactive Bezier curve with a draggable control point
    - Ellipse: Renders an interactive ellipse (no public traitlets)

Key traitlets:
    - Line.my_vector (Any): A 2-element list [x, y] defining the line
      endpoint (default: [5, 5])
    - Bezier.my_x_coord (Float): X-coordinate of the Bezier control point
      (default: -5.0)

Required package:
    pip install ipymafs

Run with:
    panel serve research/anywidget/examples/ext_ipymafs.py
"""

from ipymafs import Bezier, Ellipse, Line

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create ipymafs widgets
# ---------------------------------------------------------------------------

line_widget = Line()
bezier_widget = Bezier()
ellipse_widget = Ellipse()

# Wrap each with Panel's AnyWidget pane.
# Mafs renders large SVG canvases; use enough height to avoid overlap.
_aw_kwargs = dict(height=550, sizing_mode="stretch_width")
line_pane = pn.pane.AnyWidget(line_widget, **_aw_kwargs)
bezier_pane = pn.pane.AnyWidget(bezier_widget, **_aw_kwargs)
ellipse_pane = pn.pane.AnyWidget(ellipse_widget, **_aw_kwargs)

line_component = line_pane.component
bezier_component = bezier_pane.component

# ---------------------------------------------------------------------------
# 2. Controls for the Line widget (bidirectional sync)
# ---------------------------------------------------------------------------

x_slider = pn.widgets.FloatSlider(
    name="Vector X",
    start=-10,
    end=10,
    value=line_component.my_vector[0],
    step=0.5,
    width=250,
)

y_slider = pn.widgets.FloatSlider(
    name="Vector Y",
    start=-10,
    end=10,
    value=line_component.my_vector[1],
    step=0.5,
    width=250,
)


def update_line_vector(event):
    """Panel -> Widget: update the line vector when sliders change."""
    line_component.my_vector = [x_slider.value, y_slider.value]


x_slider.param.watch(update_line_vector, "value")
y_slider.param.watch(update_line_vector, "value")

# Widget -> Panel: display current vector
vector_display = pn.pane.Markdown(
    pn.bind(
        lambda v: f"**Current vector:** [{v[0]}, {v[1]}]" if v else "**Current vector:** --",
        line_component.param.my_vector,
    ),
    sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 3. Controls for the Bezier widget (bidirectional sync)
# ---------------------------------------------------------------------------

bezier_x_slider = pn.widgets.FloatSlider(
    name="Bezier Control X",
    start=-10,
    end=10,
    value=bezier_component.my_x_coord,
    step=0.5,
    width=250,
)

# Panel -> Widget
bezier_x_slider.param.watch(
    lambda e: setattr(bezier_component, 'my_x_coord', e.new), ['value']
)

# Widget -> Panel
bezier_component.param.watch(
    lambda e: setattr(bezier_x_slider, 'value', e.new), ['my_x_coord']
)

# Display current value
bezier_display = pn.pane.Markdown(
    pn.bind(
        lambda x: f"**Bezier control X:** {x}",
        bezier_component.param.my_x_coord,
    ),
    sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
ipymafs Line, Bezier, and Ellipse widgets render interactive math visualizations
using the Mafs.dev library. The <code>my_vector</code> trait on Line and
<code>my_x_coord</code> on Bezier sync bidirectionally with Panel sliders.
All three widget types render correctly.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipymafs -- Interactive Math Visualizations

[GitHub](https://github.com/nickmcintyre/ipymafs) |
[Mafs.dev](https://mafs.dev/)

Interactive math function plots powered by the Mafs JavaScript library.

## How to Test

1. **Line widget:** Drag the X/Y sliders to change the vector endpoint.
   The line on the coordinate grid should update in real time.
2. **Bezier widget:** Use the slider to move the control point X coordinate,
   or drag the control point directly in the visualization.
3. **Ellipse widget:** Renders an interactive ellipse -- drag to modify it
   directly in the browser.
""", sizing_mode="stretch_width")

line_controls = pn.Column(
    pn.pane.Markdown("### Line Controls"),
    x_slider,
    y_slider,
    vector_display,
    width=300,
)

bezier_controls = pn.Column(
    pn.pane.Markdown("### Bezier Controls"),
    bezier_x_slider,
    bezier_display,
    width=300,
)

pn.Column(
    status,
    header,
    pn.pane.Markdown("---"),
    pn.pane.Markdown("## Line"),
    line_pane,
    pn.Row(line_controls),
    pn.pane.Markdown("---"),
    pn.pane.Markdown("## Bezier Curve"),
    bezier_pane,
    pn.Row(bezier_controls),
    pn.pane.Markdown("---"),
    pn.pane.Markdown("## Ellipse"),
    ellipse_pane,
    pn.pane.Markdown("*Ellipse has no public traitlets -- interact directly by dragging in the visualization.*"),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
