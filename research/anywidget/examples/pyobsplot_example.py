"""
pyobsplot Example — Observable Plot in Panel
=============================================

This example demonstrates using pyobsplot (Observable Plot for Python)
with Panel's AnyWidget pane.

pyobsplot renders Observable Plot charts as anywidgets. The Plot.plot()
method returns an ObsplotWidget whose `spec` traitlet can be updated to
change the chart dynamically.

Key traitlets:
    - spec (Dict): The Observable Plot specification dictionary

Required packages:
    pip install pyobsplot pandas

Run with:
    panel serve research/anywidget/examples/pyobsplot_example.py
"""

import panel as pn

try:
    from pyobsplot import Plot
except ImportError as e:
    raise ImportError(
        "This example requires pyobsplot. "
        "Please install it with: pip install pyobsplot"
    ) from e

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "This example requires pandas. "
        "Please install it with: pip install pandas"
    ) from e

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data
# ---------------------------------------------------------------------------

import random

random.seed(42)

data = pd.DataFrame({
    "category": ["A", "B", "C", "D", "E"] * 10,
    "value": [random.gauss(50, 15) for _ in range(50)],
    "group": (["alpha"] * 5 + ["beta"] * 5) * 5,
})

# ---------------------------------------------------------------------------
# 2. Create an Observable Plot widget
# ---------------------------------------------------------------------------


def make_spec(mark_type="dot", color_col="category", show_grid=True):
    """Build an Observable Plot spec dictionary."""
    marks = []
    if mark_type == "dot":
        marks.append(
            Plot.dot(data, {"x": "category", "y": "value", "fill": color_col})
        )
    elif mark_type == "bar":
        marks.append(
            Plot.barY(data, Plot.groupX({"y": "sum"}, {"x": "category", "y": "value", "fill": color_col}))
        )
    elif mark_type == "boxplot":
        marks.append(
            Plot.boxY(data, {"x": "category", "y": "value", "fill": color_col})
        )
    return {
        "grid": show_grid,
        "color": {"legend": True},
        "marks": marks,
    }


# Create the initial plot widget (returns ObsplotWidget)
plot_widget = Plot.plot(make_spec())

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(plot_widget)

# ---------------------------------------------------------------------------
# 3. Panel controls to update the plot spec
# ---------------------------------------------------------------------------

mark_select = pn.widgets.Select(
    name="Mark Type",
    options=["dot", "bar", "boxplot"],
    value="dot",
    width=200,
)

color_select = pn.widgets.Select(
    name="Color By",
    options=["category", "group"],
    value="category",
    width=200,
)

grid_toggle = pn.widgets.Toggle(
    name="Show Grid",
    value=True,
    width=200,
)


def update_plot(*events):
    """Update the plot spec when any control changes."""
    new_spec = make_spec(
        mark_type=mark_select.value,
        color_col=color_select.value,
        show_grid=grid_toggle.value,
    )
    anywidget_pane.component.spec = new_spec


mark_select.param.watch(update_plot, "value")
color_select.param.watch(update_plot, "value")
grid_toggle.param.watch(update_plot, "value")

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# pyobsplot — Observable Plot in Panel

**pyobsplot** brings [Observable Plot](https://observablehq.com/@observablehq/plot)
to Python. This example renders an Observable Plot chart natively in Panel
using the `AnyWidget` pane.

## How It Works

`Plot.plot(spec)` returns an `ObsplotWidget` (an anywidget) with a `spec`
traitlet. Panel wraps it with `pn.pane.AnyWidget()` and the chart updates
reactively when `pane.component.spec` is reassigned.

## Controls

Use the controls below to change the chart type, color mapping, and grid.
""", sizing_mode="stretch_width")

controls = pn.Row(mark_select, color_select, grid_toggle)

pn.Column(
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
