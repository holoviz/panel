"""
pyobsplot Example — Observable Plot in Panel
=============================================

This example demonstrates using pyobsplot (Observable Plot for Python)
with Panel's AnyWidget pane.

pyobsplot renders Observable Plot charts as anywidgets. The Plot.plot()
method returns an ObsplotWidget whose `spec` traitlet can be updated to
change the chart dynamically.

GitHub: https://github.com/juba/pyobsplot
Docs:   https://juba.github.io/pyobsplot/

Key traitlets:
    - spec (Dict): The Observable Plot specification dictionary

Required packages:
    pip install pyobsplot pandas

Run with:
    panel serve research/anywidget/examples/ext_pyobsplot.py
"""

import random

import pandas as pd  # noqa: F401

from pyobsplot import Plot

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data
# ---------------------------------------------------------------------------

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
    name="Chart Type",
    options={"Dot Plot": "dot", "Bar Chart": "bar", "Box Plot": "boxplot"},
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

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
This example works fully with Panel's AnyWidget pane.
Rendering, spec updates from Panel, and chart type switching all work as expected.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# pyobsplot -- Observable Plot in Panel

[GitHub](https://github.com/juba/pyobsplot) | [Docs](https://juba.github.io/pyobsplot/)

An interactive chart built with [Observable Plot](https://observablehq.com/plot/),
rendered in Panel.

## Try These Controls

- **Chart Type:** Switch between Dot plot (individual points), Bar chart
  (summed by category), and Box plot (distribution per category)
- **Color By:** Color the marks by "category" (A-E) or by "group" (alpha/beta)
- **Show Grid:** Toggle background grid lines on and off

The chart updates instantly when you change any control.
""", sizing_mode="stretch_width")

controls = pn.Row(mark_select, color_select, grid_toggle)

pn.Column(
    status,
    header,
    controls,
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
