"""
drawdata Example with Bidirectional Sync
=========================================

This example demonstrates using the drawdata library's ScatterWidget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

KNOWN ISSUE: drawdata's ESM bundle (487KB) has a `circle_brush` initialization
error on page load: `Cannot access 'circle_brush' before initialization`.
This is a drawdata library bug, not a Panel AnyWidget issue. Despite the error,
the widget renders and is partially functional.

GitHub: https://github.com/koaning/drawdata
Docs:   https://github.com/koaning/drawdata#readme

Required package:
    pip install drawdata

Run with:
    panel serve research/anywidget/examples/ext_drawdata.py
"""

from drawdata import ScatterWidget

import panel as pn

pn.extension()

# Create the drawdata ScatterWidget
scatter_widget = ScatterWidget()

# Wrap it with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(scatter_widget)

# Create Panel controls for bidirectional sync
brushsize_slider = pn.widgets.IntSlider(
    name="Brush Size",
    start=1,
    end=50,
    value=scatter_widget.brushsize,
    width=300
)

# Pane to display the drawn data
data_display = pn.pane.JSON(
    scatter_widget.data if scatter_widget.data else {},
    name="Drawn Data"
)

# Bidirectional sync setup using the *param* API on pane.component.
# pane.component is available immediately — no need to wait for render.
component = anywidget_pane.component

# Panel -> Widget (through component params):
brushsize_slider.param.watch(lambda e: setattr(component, 'brushsize', e.new), "value")

# Widget -> Panel (through component param.watch):
def on_component_change(*events):
    for event in events:
        if event.name == "brushsize":
            brushsize_slider.value = event.new
        elif event.name == "data":
            data_display.object = event.new if event.new else {}

component.param.watch(on_component_change, ["brushsize", "data"])

# Layout
status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
drawdata renders and allows drawing points, but logs a JavaScript error on page load:
<code>Cannot access 'circle_brush' before initialization</code>. This is an upstream
drawdata library bug, not a Panel issue. Despite the error, the widget is functional.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# drawdata -- Draw Scatter Data Points

**drawdata** lets you create scatter plot datasets by drawing directly on a
canvas. This is useful for generating synthetic classification data.

## How to Draw

1. **Pick a class** by clicking one of the colored buttons at the top of the canvas
   (each color represents a different label)
2. **Draw points** by clicking or dragging on the canvas. Each click places
   a point with the selected class label.
3. **Watch the data update** in the "Drawn Data" panel on the right -- it
   shows the x/y coordinates and labels in real time.

**Note:** Due to an upstream bug in drawdata, the Brush Size slider may not
sync changes to the canvas. Drawing and data export still work.
""")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    brushsize_slider,
    width=350
)

data_section = pn.Column(
    pn.pane.Markdown("## Drawn Data (Real-time)"),
    data_display
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Canvas"),
            anywidget_pane,
        ),
        controls,
        data_section,
    ),
).servable()
