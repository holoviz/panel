"""
Mosaic Widget Example with Bidirectional Sync
==============================================

This example demonstrates using the mosaic-widget MosaicWidget
with Panel's AnyWidget pane and bidirectional sync of interactive
parameters back to Panel.

Mosaic is a framework for linking interactive views to databases.
The MosaicWidget is built on anywidget.AnyWidget and uses DuckDB
(either in-process Python or compiled to WASM in the browser) to
process SQL queries that drive interactive visualizations.

The widget accepts a Vega-Lite-like specification (as a dict) and
optional data (as Pandas/Polars DataFrames). The `params` traitlet
syncs interactive filter/selection parameters back to Python.

GitHub: https://github.com/uwdata/mosaic
Docs:   https://uwdata.github.io/mosaic/

Required packages:
    pip install mosaic-widget pandas

Run with:
    panel serve research/anywidget/examples/ext_mosaic.py
"""

import numpy as np
import pandas as pd

from mosaic_widget import MosaicWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data
# ---------------------------------------------------------------------------

np.random.seed(42)
n = 200
df = pd.DataFrame({
    "x": np.random.randn(n),
    "y": np.random.randn(n),
    "category": np.random.choice(["A", "B", "C"], n),
    "value": np.random.uniform(0, 100, n),
})

# ---------------------------------------------------------------------------
# 2. Create Mosaic specifications
# ---------------------------------------------------------------------------
# The scatter spec includes a named "brush" selection declared in the
# "params" block. The "intervalXY" interactor lets users drag a rectangle
# on the plot; "highlight" dims unselected points. Each time the brush
# changes, Mosaic syncs the selection state to the widget's `params`
# traitlet, which Panel then picks up automatically.

scatter_spec = {
    "params": {
        "brush": {"select": "intersect"},
    },
    "plot": [
        {
            "mark": "dot",
            "data": {"from": "sample_data"},
            "x": "x",
            "y": "y",
            "fill": "category",
            "r": 5,
        },
        {"select": "intervalXY", "as": "$brush"},
        {"select": "highlight", "by": "$brush"},
    ],
    "width": 500,
    "height": 400,
}

bar_spec = {
    "plot": [
        {
            "mark": "barY",
            "data": {"from": "sample_data"},
            "x": "category",
            "y": {"avg": "value"},
            "fill": "category",
        },
    ],
    "width": 500,
    "height": 400,
}

# ---------------------------------------------------------------------------
# 3. Create the MosaicWidget and wrap with Panel
# ---------------------------------------------------------------------------

mosaic_widget = MosaicWidget(
    spec=scatter_spec,
    data={"sample_data": df},
)

anywidget_pane = pn.pane.AnyWidget(mosaic_widget, height=500, width=500, styles={"border": "1px solid #ccc", "border-radius": "4px"})

# ---------------------------------------------------------------------------
# 4. Wire up Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display interactive params synced back from the widget
params_display = pn.pane.JSON(
    mosaic_widget.params if mosaic_widget.params else {},
    name="Mosaic Params",
    depth=3,
    height=300,
)

def on_params_change(*events):
    for event in events:
        if event.name == "params":
            params_display.object = event.new if event.new else {}

component.param.watch(on_params_change, ["params"])

# Button to update the spec from Python
def update_to_bar_chart(event):
    """Switch the visualization to a bar chart (value by category)."""
    component.spec = bar_spec

def update_to_scatter(event):
    """Switch the visualization back to the scatter plot."""
    component.spec = scatter_spec

scatter_btn = pn.widgets.Button(name="Scatter Plot", button_type="primary", width=150)
bar_btn = pn.widgets.Button(name="Bar Chart", button_type="warning", width=150)

scatter_btn.on_click(update_to_scatter)
bar_btn.on_click(update_to_bar_chart)

# ---------------------------------------------------------------------------
# 5. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
This example works fully with Panel's AnyWidget pane.
Rendering, interactive brush selections, spec switching (scatter &harr; bar),
DuckDB-backed queries, and param sync all work as expected.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# Mosaic Widget -- Interactive Scatter & Bar Chart

[Mosaic](https://uwdata.github.io/mosaic/) turns visualization specs into
SQL queries that run against an in-browser DuckDB database.

## How to Interact

1. **Brush-select points** -- Click and drag on the scatter plot to draw a
   selection rectangle. Selected points stay bright; the rest dim out.
   Watch the **Selection State** panel update with the brush coordinates.
2. **Clear the selection** -- Click on an empty area of the plot.
3. **Switch to Bar Chart** -- Click the button to push a different spec
   from Python. The bar chart shows average value per category.
4. **Switch back to Scatter** -- Click to return to the interactive scatter.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Chart Type"),
    pn.Row(scatter_btn, bar_btn),
    pn.pane.Markdown("### Selection State"),
    pn.pane.Markdown(
        "_Drag a rectangle on the scatter plot to see brush "
        "coordinates appear here in real time._"
    ),
    params_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Mosaic Visualization"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
