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

Note on _params vs _vl_selections:
- `_vl_selections` tracks Vega-Lite **selections** (interval / point)
- `_params` tracks Vega-Lite **named parameters** created with `alt.param()`
  Both only sync if the chart spec includes the corresponding declarations.

GitHub: https://github.com/vega/altair
Docs:   https://altair-viz.github.io/

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
# 1. Create an Altair chart with brush selection AND a named param
# ---------------------------------------------------------------------------

source = vega_data.cars()

# Create an interval selection (brush) — syncs to _vl_selections
brush = alt.selection_interval()

# Create a named parameter (slider) — syncs to _params
cutoff = alt.param(name="cutoff", value=100, bind=alt.binding_range(min=0, max=300, step=1))

# Build the chart with brush selection, cutoff param, and conditional encoding
chart = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x=alt.X("Horsepower:Q"),
        y=alt.Y("Miles_per_Gallon:Q"),
        color=alt.condition(brush, "Origin:N", alt.value("lightgray")),
        opacity=alt.condition(alt.datum.Horsepower > cutoff, alt.value(1.0), alt.value(0.2)),
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .properties(width=500, height=350, title="Cars Dataset — Brush & Filter")
    .add_params(brush, cutoff)
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
            opacity=alt.condition(alt.datum[x] > cutoff, alt.value(1.0), alt.value(0.2)),
            tooltip=["Name", "Origin", x, y],
        )
        .properties(width=500, height=350, title="Cars Dataset — Brush & Filter")
        .add_params(brush, cutoff)
    )
    component.spec = new_chart.to_dict()

x_selector.param.watch(update_chart, "value")
y_selector.param.watch(update_chart, "value")

# Chart -> Panel: display selections and params synced back from the browser
selections_display = pn.pane.JSON(
    {}, name="Vega-Lite Selections", depth=4, height=150,
)
params_display = pn.pane.JSON(
    {}, name="Vega-Lite Params", depth=4, height=150,
)

# Show filtered data from brush selection
selection_table = pn.pane.DataFrame(
    source.head(0), name="Selected Points", height=200, sizing_mode="stretch_width",
)
selection_count = pn.pane.Markdown("**Selected:** 0 points")

def on_selections_change(*events):
    for event in events:
        sel = event.new if event.new else {}
        selections_display.object = sel
        # Filter source data by brush selection bounds
        if sel:
            # Extract the first selection's bounds (interval selection)
            for _, sel_data in sel.items():
                sel_data = sel_data.get("value")
                if not sel_data:
                    continue
                filtered = source
                if "Horsepower" in sel_data:
                    hp_range = sel_data["Horsepower"]
                    filtered = filtered[
                        (filtered["Horsepower"] >= hp_range[0])
                        & (filtered["Horsepower"] <= hp_range[1])
                    ]
                if "Miles_per_Gallon" in sel_data:
                    mpg_range = sel_data["Miles_per_Gallon"]
                    filtered = filtered[
                        (filtered["Miles_per_Gallon"] >= mpg_range[0])
                        & (filtered["Miles_per_Gallon"] <= mpg_range[1])
                    ]
                selection_table.object = filtered.reset_index(drop=True)
                selection_count.object = f"**Selected:** {len(filtered)} points"
                break  # use the first selection
        else:
            selection_table.object = source.head(0)
            selection_count.object = "**Selected:** 0 points"

def on_params_change(*events):
    for event in events:
        params_display.object = event.new if event.new else {}

component.param.watch(on_selections_change, ["_vl_selections"])
component.param.watch(on_params_change, ["_params"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

ALTAIR_LOGO = "https://altair-viz.github.io/_static/altair-logo-light.png"

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
This example works fully with Panel's AnyWidget pane.
Rendering, bidirectional sync (Panel &harr; Vega-Lite selections &amp; params), and interaction all work as expected.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# Altair Interactive Scatter Plot

[GitHub](https://github.com/vega/altair) | [Docs](https://altair-viz.github.io/)

Explore the **Cars dataset** with an interactive Altair chart rendered in Panel.

## How to Use

1. **Brush-select points:** Click and drag on the chart to draw a selection
   rectangle. Selected points turn colored; unselected points turn gray.
   The data table below updates to show only the selected rows.
2. **Drag the cutoff slider:** Look for the small slider labeled "cutoff"
   directly above the chart. Drag it to set a Horsepower threshold --
   points below the cutoff become semi-transparent.
3. **Change axes:** Use the X Axis and Y Axis dropdowns on the right to
   plot different car attributes (e.g., Weight vs. Acceleration).
   The chart rebuilds instantly.

The raw selection coordinates and slider value are shown in the sidebar.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Axis Controls"),
    x_selector,
    y_selector,
    pn.Column(
        pn.pane.Markdown("### Selection Bounds"),
        pn.pane.Markdown("_Coordinates of your brush rectangle:_"),
        selections_display,
    ),
    pn.Column(
        pn.pane.Markdown("### Cutoff Value"),
        pn.pane.Markdown("_Current value of the in-chart slider:_"),
        params_display,
    ),
    width=350,
)

pn.Column(
    status,
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
    pn.pane.Markdown("### Selected Data (brush-select points on the chart)"),
    selection_table,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
