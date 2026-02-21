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
    panel serve research/anywidget/examples/altair_example.py
"""

import panel as pn

try:
    import altair as alt

    from altair import JupyterChart
except ImportError as e:
    raise ImportError(
        "This example requires altair >= 5.1. "
        "Please install it with: pip install altair vega_datasets"
    ) from e

try:
    from vega_datasets import data as vega_data
except ImportError as e:
    raise ImportError(
        "This example requires vega_datasets. "
        "Please install it with: pip install vega_datasets"
    ) from e

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create an Altair chart with interactive parameters
# ---------------------------------------------------------------------------

source = vega_data.cars()

# Create a variable parameter for the x-axis field
x_field = alt.param(
    name="x_field",
    value="Horsepower",
)

y_field = alt.param(
    name="y_field",
    value="Miles_per_Gallon",
)

# Build the chart — a simple scatter with color encoding
chart = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x=alt.X("Horsepower:Q", title="Horsepower"),
        y=alt.Y("Miles_per_Gallon:Q", title="Miles per Gallon"),
        color="Origin:N",
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .properties(width=500, height=350, title="Cars Dataset — Altair JupyterChart")
    .interactive()
)

# Create the JupyterChart widget
jupyter_chart = JupyterChart(chart)

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(jupyter_chart)

# ---------------------------------------------------------------------------
# 3. Add Panel controls for bidirectional interaction
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display the current spec as JSON (read-only — useful for debugging)
spec_display = pn.pane.JSON(
    jupyter_chart.spec if jupyter_chart.spec else {},
    name="Vega-Lite Spec",
    depth=2,
    height=200,
)

# Watch for spec changes from the component
def on_spec_change(*events):
    for event in events:
        if event.name == "spec":
            spec_display.object = event.new if event.new else {}

component.param.watch(on_spec_change, ["spec"])

# Create a new chart on dropdown change
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
mark_selector = pn.widgets.Select(
    name="Mark Type",
    options=["circle", "square", "point"],
    value="circle",
    width=200,
)

def update_chart(*events):
    """Rebuild the chart with new field selections and push to the widget."""
    x = x_selector.value
    y = y_selector.value
    mark = mark_selector.value

    mark_method = getattr(alt.Chart(source), f"mark_{mark}")
    new_chart = (
        mark_method(size=60)
        .encode(
            x=alt.X(f"{x}:Q", title=x.replace("_", " ")),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ")),
            color="Origin:N",
            tooltip=["Name", "Origin", x, y],
        )
        .properties(width=500, height=350, title="Cars Dataset — Altair JupyterChart")
        .interactive()
    )
    # Update the spec on the component — this syncs to the browser
    component.spec = new_chart.to_dict()

x_selector.param.watch(update_chart, "value")
y_selector.param.watch(update_chart, "value")
mark_selector.param.watch(update_chart, "value")


# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

ANYWIDGET_LOGO = "https://raw.githubusercontent.com/manzt/anywidget/main/docs/public/favicon.svg"
ALTAIR_LOGO = "https://altair-viz.github.io/_static/altair-logo-light.png"

header = pn.pane.Markdown("""
# Altair JupyterChart — AnyWidget Pane Demo

This example renders **Altair's JupyterChart** (an anywidget) natively
in Panel using the `AnyWidget` pane. The chart is fully interactive —
pan, zoom, and hover tooltips work out of the box.

Use the dropdowns to change the axes and mark type. The chart updates
by pushing a new Vega-Lite spec to the widget via `component.spec`.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    x_selector,
    y_selector,
    mark_selector,
    pn.pane.Markdown("### Vega-Lite Spec (live)"),
    spec_display,
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
