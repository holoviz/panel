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

n_classes_slider = pn.widgets.IntSlider(
    name="Number of Classes",
    start=2,
    end=10,
    value=scatter_widget.n_classes,
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
n_classes_slider.param.watch(lambda e: setattr(component, 'n_classes', e.new), "value")

# Widget -> Panel (through component param.watch):
def on_component_change(*events):
    for event in events:
        if event.name == "brushsize":
            brushsize_slider.value = event.new
        elif event.name == "n_classes":
            n_classes_slider.value = event.new
        elif event.name == "data":
            data_display.object = event.new if event.new else {}

component.param.watch(on_component_change, ["brushsize", "n_classes", "data"])

# Layout
header = pn.pane.Markdown("""
# drawdata Example — Bidirectional Sync with Panel

This example renders **drawdata's ScatterWidget** (a third-party anywidget)
natively in Panel using the `AnyWidget` pane with full bidirectional synchronization.

## Known Issue

drawdata's bundled ESM (487KB) has a `circle_brush` initialization error on page load.
You'll see `Uncaught ReferenceError: Cannot access 'circle_brush' before initialization`
in the browser console. This is a **drawdata library bug**, not a Panel issue.

This error **breaks bidirectional sync** — the widget partially renders but the
Panel sliders (Brush Size, Number of Classes) may not update the widget because
the initialization error prevents the `model.on("change:brushsize", ...)` handlers
from being fully connected. Data sync (Widget -> Panel) may also be affected.

## How It Works

**Drawing Canvas:** Use your mouse to draw scatter data points by clicking and dragging in the canvas area.

**Bidirectional Controls:**
- **Brush Size:** Adjust the brush size using the slider (1-50 pixels). Changes sync both ways between the slider and the widget.
- **Number of Classes:** Set the number of data classes using the slider (2-10). Changes sync both ways.

**Data Display:** The drawn data is displayed in real-time as you draw. The JSON view shows:
- `x`: x-coordinates of drawn points
- `y`: y-coordinates of drawn points
- `label`: class labels for each point

## Testing Bidirectional Sync

1. **Widget -> Panel:** Draw points in the canvas. The data display updates automatically.
2. **Panel -> Widget:** Adjust the sliders. The widget's internal state updates.
3. **Widget -> Panel (controls):** If you can directly change widget values (e.g., via console), the Panel sliders reflect the changes.
""")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    brushsize_slider,
    n_classes_slider,
    width=350
)

data_section = pn.Column(
    pn.pane.Markdown("## Drawn Data (Real-time)"),
    data_display
)

pn.Column(
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
