"""
navio_jupyter Example -- Interactive Data Explorer
===================================================

This example demonstrates using navio_jupyter's navio widget
(a high-dimensional data explorer) with Panel's AnyWidget pane.

navio renders a compact, interactive visualization of tabular data,
showing all columns side-by-side as mini-bar charts. Users can
brush/filter data in the browser, and the ``selected`` traitlet
reports the selected row indices back to Python.

GitHub: https://github.com/john-googol/navio-jupyter

Key traitlets:
    - data (List): List of dicts representing the tabular data
    - height (Int): Height of the widget in pixels (default: 300)
    - opts (Dict): Configuration options for the visualization
    - selected (List): Currently selected/filtered data rows

Note: The ``data`` trait expects a list of dicts, not a pandas DataFrame.
Convert with ``df.to_dict(orient='records')``.

Required package:
    pip install navio-jupyter

Run with:
    panel serve research/anywidget/examples/ext_navio.py
"""

import pandas as pd

from navio_jupyter import navio

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data and the navio widget
# ---------------------------------------------------------------------------

sample_data = pd.DataFrame({
    "Name": [
        "Alice", "Bob", "Charlie", "Diana", "Eve",
        "Frank", "Grace", "Hank", "Iris", "Jack",
        "Karen", "Leo", "Mona", "Nate", "Olivia",
    ],
    "Age": [25, 30, 35, 28, 32, 45, 22, 38, 29, 41, 33, 27, 36, 31, 24],
    "Salary": [
        55000, 72000, 68000, 61000, 80000,
        95000, 48000, 77000, 59000, 88000,
        71000, 53000, 82000, 64000, 46000,
    ],
    "Experience": [2, 7, 10, 4, 8, 20, 1, 14, 5, 16, 9, 3, 12, 6, 1],
    "Department": [
        "Eng", "Sales", "Eng", "HR", "Sales",
        "Eng", "HR", "Sales", "Eng", "HR",
        "Sales", "Eng", "HR", "Sales", "Eng",
    ],
    "Rating": [4.2, 3.8, 4.5, 4.0, 3.9, 4.7, 3.5, 4.1, 4.3, 3.6, 4.4, 3.7, 4.6, 4.0, 3.3],
})

widget = navio(data=sample_data.to_dict("records"), height=400)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 2. Access the component and set up bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Height slider -- Panel <-> Widget
height_slider = pn.widgets.IntSlider(
    name="Widget Height (px)",
    start=200,
    end=600,
    value=component.height,
    step=50,
    width=300,
)
height_slider.param.watch(
    lambda e: setattr(component, 'height', e.new), ['value']
)
component.param.watch(
    lambda e: setattr(height_slider, 'value', e.new), ['height']
)

# Display selected items (Widget -> Panel)
selected_display = pn.pane.JSON(
    [],
    name="Selected Data",
    depth=3,
    height=200,
)

selected_count = pn.pane.Markdown("**Selected:** 0 rows")


def on_selected_change(event):
    sel = event.new if event.new else []
    selected_display.object = sel
    selected_count.object = f"**Selected:** {len(sel)} rows"


component.param.watch(on_selected_change, ["selected"])

# Data count display
data_count = pn.pane.Markdown(f"**Total rows:** {len(sample_data)}")

# Switch datasets
alt_data = pd.DataFrame({
    "Fruit": ["Apple", "Banana", "Orange", "Grape", "Strawberry", "Blueberry", "Mango", "Kiwi"],
    "Calories": [95, 105, 62, 67, 49, 84, 99, 42],
    "Sugar_g": [19, 14, 12, 16, 7, 15, 23, 6],
    "Fiber_g": [4.4, 3.1, 3.1, 0.9, 3.0, 3.6, 2.6, 2.1],
    "Color": ["red", "yellow", "orange", "purple", "red", "blue", "orange", "green"],
})

DATASETS = {
    "Employees (15 rows)": sample_data,
    "Fruits (8 rows)": alt_data,
}

dataset_selector = pn.widgets.Select(
    name="Dataset",
    options=list(DATASETS.keys()),
    value="Employees (15 rows)",
    width=250,
)


def on_dataset_change(event):
    df = DATASETS[event.new]
    component.data = df.to_dict("records")
    data_count.object = f"**Total rows:** {len(df)}"


dataset_selector.param.watch(on_dataset_change, "value")

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# navio_jupyter -- Interactive Data Explorer

[GitHub](https://github.com/john-googol/navio-jupyter)

**navio** renders a compact, parallel-coordinates-style overview of tabular
data. Each column is displayed as a sorted mini-bar, and you can brush
(click + drag) on any column to filter the dataset.

## How to Test

1. **Brush a column** by clicking and dragging vertically on one of the
   mini-bars to select a range of values.
2. **Watch the selection** update below -- the selected row count and
   data are synced back to Python via the ``selected`` traitlet.
3. **Change the dataset** with the dropdown to load different data.
4. **Adjust height** with the slider to resize the widget.
""", sizing_mode="stretch_width")

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
navio renders linked attribute views for exploring tabular data. The <code>data</code>
and <code>height</code> traits sync from Python to browser. The <code>selected</code>
trait syncs brush selections from browser back to Python.
</p>
</div>
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    dataset_selector,
    height_slider,
    data_count,
    pn.pane.Markdown("### Selected Data"),
    selected_count,
    selected_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Navio Data Explorer"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
