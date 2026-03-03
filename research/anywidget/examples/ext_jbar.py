"""
jbar Example -- Interactive Bar Charts
=======================================

This example demonstrates using the jbar library's BarChart widget
with Panel's AnyWidget pane.

jbar provides interactive D3.js-powered bar charts that support
clicking on bars to select them. Data is provided as CSV via the
`data` trait, with `x` specifying the category column and `selection`
tracking the selected bar index.

KNOWN ISSUE: jbar's ESM uses `d3.select("#my_dataviz")` (a document-level
CSS selector query) to locate its container div. Panel renders AnyWidget
components inside a Shadow DOM, and `document.querySelector()` CANNOT
penetrate shadow DOM boundaries. As a result, D3 returns an empty selection
and the SVG bar chart is never created. The widget element is present in the
DOM, but the bars are invisible.

This is a fundamental incompatibility between D3 widgets that use
document-level ID selectors and Shadow DOM encapsulation. Widgets that
use the `el` reference directly (rather than querying by ID) work fine.

GitHub: https://github.com/jsbroks/jbar
PyPI:   https://pypi.org/project/jbar/

Key traitlets:
    - data (Unicode): CSV string of the data
    - x (Unicode): Column name for the x-axis categories
    - exclude (List): Column names to exclude from the chart
    - selection (Int): Index of the currently selected bar (0-based)

NOTE: No trait name collisions with Panel's Layoutable/Bokeh reserved names.

Required package:
    pip install jbar

Run with:
    panel serve research/anywidget/examples/ext_jbar.py --port 6116
"""

from io import StringIO

import pandas as pd

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data and BarChart widget
# ---------------------------------------------------------------------------

# Sample data: fruit sales by quarter
df = pd.DataFrame({
    "Fruit": ["Apples", "Bananas", "Cherries", "Dates", "Elderberries"],
    "Q1": [120, 85, 45, 30, 15],
    "Q2": [95, 110, 60, 40, 25],
    "Q3": [140, 75, 55, 35, 20],
    "Q4": [80, 100, 70, 50, 30],
})

# jbar requires CSV data
csv_output = StringIO()
df.to_csv(csv_output, index=False)
csv_data = csv_output.getvalue()

from jbar import BarChart

widget = BarChart()
widget.data = csv_data
widget.x = "Fruit"
widget.exclude = []
widget.selection = 0

anywidget_pane = pn.pane.AnyWidget(widget, width=700, height=550)

# ---------------------------------------------------------------------------
# 2. Panel controls (trait sync still works even though chart is invisible)
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Selection display -- shows which bar is selected
selection_display = pn.pane.Markdown(pn.bind(
    lambda s: f"**Selected bar index:** {s}",
    component.param.selection,
))

# Panel control to change the selection
selection_spinner = pn.widgets.IntInput(
    name="Selection Index (Panel -> Widget)",
    value=0,
    start=0,
    end=len(df) - 1,
    step=1,
    width=200,
)

# Panel -> Widget
selection_spinner.param.watch(
    lambda e: setattr(component, "selection", e.new), "value"
)

# Widget -> Panel
def on_selection_change(*events):
    for event in events:
        if event.name == "selection":
            selection_spinner.value = event.new

component.param.watch(on_selection_change, ["selection"])

# Show current data as a table
data_table = pn.pane.DataFrame(df, name="Source Data", width=500)

# Display current x and data info
x_display = pn.pane.Markdown(pn.bind(
    lambda x, d: (
        f"**X column:** `{x}` | "
        f"**Data size:** {len(d):,} chars CSV"
    ),
    component.param.x,
    component.param.data,
))

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 15px; margin: 8px 0 0 0;">
<strong>Root cause:</strong> jbar's ESM uses <code>d3.select("#my_dataviz")</code>,
a document-level CSS selector query, to locate its container div. Panel renders
AnyWidget components inside a <strong>Shadow DOM</strong>, and
<code>document.querySelector()</code> cannot penetrate shadow DOM boundaries.
D3 returns an empty selection, so the SVG bar chart is never created.
<br><br>
<strong>This is NOT a Panel bug</strong> &mdash; it is a fundamental incompatibility
between D3 widgets that use document-level ID selectors and Shadow DOM encapsulation.
Widgets that use the <code>el</code> reference directly (e.g. <code>d3.select(el)</code>
or <code>el.querySelector()</code>) work fine in Panel.
<br><br>
<strong>Trait sync still works:</strong> The <code>data</code>, <code>x</code>,
<code>exclude</code>, and <code>selection</code> params are created and synced
correctly; only the visual D3 rendering fails.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# jbar -- Interactive Bar Charts

**jbar** provides D3.js-powered interactive bar charts. Click on bars to
select them; the selection index syncs back to Python.

## Why It Does Not Render

jbar's JavaScript code creates a `<div id="my_dataviz">` inside the
AnyWidget container element (`el`), then uses `d3.select("#my_dataviz")`
to locate it and append the SVG chart. This D3 call translates to
`document.querySelector("#my_dataviz")`, which searches the **main document**
tree only.

Panel renders AnyWidget components inside a **Shadow DOM** for style
encapsulation. Elements inside a shadow root are invisible to
`document.querySelector()`, so D3's selection is empty and no SVG is created.

### Potential Fixes (upstream)

The jbar library could fix this by using the `el` reference directly:
```javascript
// Instead of:
d3.select("#" + this.parent.id).append("svg")
// Use:
d3.select(this.parent).append("svg")
```

### Workaround

Currently, Panel's AnyWidget does not support `use_shadow_dom=False` as a
constructor parameter for the dynamically-created component class. If
shadow-DOM-free rendering were supported, D3's document-level queries
would work.

## Trait Name Collisions

**None.** jbar's traits (`data`, `x`, `exclude`, `selection`) do not
collide with Panel's Layoutable or Bokeh reserved parameter names.

## Component Params (synced correctly)

The following params are available on `pane.component`:
- `data` (str): CSV data string
- `x` (str): X-axis category column name
- `exclude` (list): Columns to exclude
- `selection` (int): Selected bar index

## Testing Instructions

1. Run: `panel serve research/anywidget/examples/ext_jbar.py --port 6116`
2. Observe the blank chart area (expected -- the D3 rendering fails)
3. Verify the trait info display updates correctly
4. Note that the underlying trait sync machinery works; only the D3
   rendering is broken due to Shadow DOM incompatibility
""", sizing_mode="stretch_width")

trait_info = pn.Column(
    pn.pane.Markdown("### Trait Sync (working despite no chart)"),
    selection_display,
    selection_spinner,
    x_display,
    pn.pane.Markdown("---"),
    pn.pane.Markdown("### Source Data"),
    data_table,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Bar Chart Area (blank due to Shadow DOM issue)"),
            anywidget_pane,
            width=750,
        ),
        trait_info,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
