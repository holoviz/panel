"""
Altair JupyterChart Example with Bidirectional Sync
====================================================

This example demonstrates using Altair's JupyterChart widget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

Altair's JupyterChart is built on anywidget.AnyWidget. It loads its
Vega-Lite JavaScript dependencies from a CDN by default, keeping the
ESM payload small. The `spec` traitlet holds the Vega-Lite specification
as a dict, and `_params` / `_vl_selections` sync interactive parameters
and selections back to Python.

Required packages:
    pip install altair vega_datasets

Run with:
    panel serve research/anywidget/examples/ext_altair.py
"""

import altair as alt

from altair import JupyterChart
from vega_datasets import data as vega_data

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create an Altair chart with brush selection for bidirectional sync
# ---------------------------------------------------------------------------

source = vega_data.cars()

# Create an interval selection (brush) to demonstrate bidirectional sync
brush = alt.selection_interval()

# Build the chart with brush selection and conditional color
chart = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x=alt.X("Horsepower:Q"),
        y=alt.Y("Miles_per_Gallon:Q"),
        color=alt.condition(brush, "Origin:N", alt.value("lightgray")),
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .properties(width=500, height=350, title="Cars Dataset — Brush to Select")
    .add_params(brush)
)

# Create the JupyterChart widget
jupyter_chart = JupyterChart(chart)

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(jupyter_chart)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 3. Bidirectional sync: Panel dropdowns -> chart, selections -> Panel
# ---------------------------------------------------------------------------

# Panel -> Chart: rebuild chart on dropdown change
field_options = [
    "Horsepower", "Miles_per_Gallon", "Weight_in_lbs",
    "Displacement", "Acceleration",
]

x_selector = pn.widgets.Select(
    name="X Axis", options=field_options, value="Horsepower", width=200
)
y_selector = pn.widgets.Select(
    name="Y Axis", options=field_options, value="Miles_per_Gallon", width=200
)

def update_chart(*events):
    """Rebuild the chart with new field selections and push to the widget."""
    x = x_selector.value
    y = y_selector.value
    new_chart = (
        alt.Chart(source)
        .mark_circle(size=60)
        .encode(
            x=alt.X(f"{x}:Q", title=x.replace("_", " ")),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ")),
            color=alt.condition(brush, "Origin:N", alt.value("lightgray")),
            tooltip=["Name", "Origin", x, y],
        )
        .properties(width=500, height=350, title="Cars Dataset — Brush to Select")
        .add_params(brush)
    )
    component.spec = new_chart.to_dict()

x_selector.param.watch(update_chart, "value")
y_selector.param.watch(update_chart, "value")

# Chart -> Panel: display selections synced back from the browser
selections_display = pn.pane.JSON(
    {}, name="Vega-Lite Selections", depth=3, height=150,
)
params_display = pn.pane.JSON(
    {}, name="Vega-Lite Params", depth=3, height=150,
)

def on_selections_change(*events):
    for event in events:
        selections_display.object = event.new if event.new else {}

def on_params_change(*events):
    for event in events:
        params_display.object = event.new if event.new else {}

component.param.watch(on_selections_change, ["_vl_selections"])
component.param.watch(on_params_change, ["_params"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

ALTAIR_LOGO = "https://altair-viz.github.io/_static/altair-logo-light.png"

header = pn.pane.Markdown("""
# Altair JupyterChart — Bidirectional Sync Demo

This example renders **Altair's JupyterChart** (an anywidget) natively
in Panel using the `AnyWidget` pane.

**Bidirectional sync:**
- **Panel -> Chart**: Use the dropdowns to change axes. The chart updates
  by pushing a new Vega-Lite spec via `component.spec`.
- **Chart -> Panel**: Brush-select points on the chart. The selection
  coordinates sync back to Python via `component._vl_selections`.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    x_selector,
    y_selector,
    pn.pane.Markdown("### Selections (from chart)"),
    selections_display,
    pn.pane.Markdown("### Params (from chart)"),
    params_display,
    width=350,
)

pn.Column(
    header,
    pn.Row(
        pn.Column(
            pn.Row(
                pn.pane.PNG(ALTAIR_LOGO, height=35, margin=(0, 10, 0, 0)),
                pn.pane.Markdown("### Altair JupyterChart"),
                align="center",
            ),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
