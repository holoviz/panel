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
# 2. Create a Mosaic specification
# ---------------------------------------------------------------------------
# This spec creates an interactive scatter plot with cross-filtering.
# Mosaic specs are Vega-Lite-like dicts that Mosaic compiles to SQL.

spec = {
    "plot": [
        {
            "mark": "dot",
            "data": {"from": "sample_data"},
            "x": "x",
            "y": "y",
            "fill": "category",
            "r": 5,
        }
    ],
    "width": 500,
    "height": 400,
}

# ---------------------------------------------------------------------------
# 3. Create the MosaicWidget and wrap with Panel
# ---------------------------------------------------------------------------

mosaic_widget = MosaicWidget(
    spec=spec,
    data={"sample_data": df},
)

anywidget_pane = pn.pane.AnyWidget(mosaic_widget)

# ---------------------------------------------------------------------------
# 4. Wire up Panel controls for bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display interactive params synced back from the widget
params_display = pn.pane.JSON(
    mosaic_widget.params if mosaic_widget.params else {},
    name="Mosaic Params",
    depth=3,
    height=200,
)

def on_params_change(*events):
    for event in events:
        if event.name == "params":
            params_display.object = event.new if event.new else {}

component.param.watch(on_params_change, ["params"])

# Button to update the spec from Python
def update_to_bar_chart(event):
    """Switch the visualization to a bar chart."""
    bar_spec = {
        "plot": [
            {
                "mark": "barY",
                "data": {"from": "sample_data"},
                "x": "category",
                "y": {"aggregate": "count"},
                "fill": "category",
            }
        ],
        "width": 500,
        "height": 400,
    }
    component.spec = bar_spec

def update_to_scatter(event):
    """Switch the visualization back to the scatter plot."""
    component.spec = spec

scatter_btn = pn.widgets.Button(name="Scatter Plot", button_type="primary", width=150)
bar_btn = pn.widgets.Button(name="Bar Chart", button_type="warning", width=150)

scatter_btn.on_click(update_to_scatter)
bar_btn.on_click(update_to_bar_chart)

# ---------------------------------------------------------------------------
# 5. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# Mosaic Widget — AnyWidget Pane Demo

This example renders **Mosaic's MosaicWidget** (an anywidget backed by DuckDB)
natively in Panel using the `AnyWidget` pane.

Mosaic compiles interactive visualization specifications into SQL queries
that run against DuckDB. Interactive parameters (selections, filters) are
synced back to Python via the `params` traitlet.

**Switch views** using the buttons to push a new spec to the widget from Python.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Switch Visualization"),
    pn.Row(scatter_btn, bar_btn),
    pn.pane.Markdown("### Interactive Params (synced from widget)"),
    params_display,
    width=350,
)

pn.Column(
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
