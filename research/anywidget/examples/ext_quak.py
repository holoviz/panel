"""
quak Example — Scalable Data Profiler
======================================

This example demonstrates using quak's Widget (a scalable data profiler
for tables) with Panel's AnyWidget pane.

quak provides an interactive data profiler built on DuckDB and Mosaic.
Users can mouse over column summaries, cross-filter, sort, and slice rows.
Interactions are captured as executable SQL queries.

GitHub: https://github.com/manzt/quak
Docs:   https://github.com/manzt/quak#readme

Key traitlets:
    - _table_name (Unicode): Internal table name in DuckDB
    - _columns (List[Unicode]): Column names from the data
    - sql (Unicode): The current SQL query reflecting user interactions

Required packages:
    pip install quak pandas

Run with:
    panel serve research/anywidget/examples/ext_quak.py
"""

import pandas as pd
import quak

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample data
# ---------------------------------------------------------------------------

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"],
    "age": [25, 32, 28, 45, 30, 38, 22, 50],
    "salary": [50000, 72000, 61000, 95000, 68000, 83000, 45000, 110000],
    "department": ["Eng", "Sales", "Eng", "Mgmt", "Sales", "Eng", "Sales", "Mgmt"],
    "rating": [4.2, 3.8, 4.5, 4.0, 3.5, 4.8, 3.9, 4.1],
})

# ---------------------------------------------------------------------------
# 2. Create the quak Widget and wrap with AnyWidget pane
# ---------------------------------------------------------------------------

widget = quak.Widget(df)
anywidget_pane = pn.pane.AnyWidget(widget, height=500)

# ---------------------------------------------------------------------------
# 3. Display the SQL query reactively
# ---------------------------------------------------------------------------

component = anywidget_pane.component

sql_display = pn.pane.Markdown(
    f"```sql\n{widget.sql or 'SELECT * FROM df'}\n```",
    sizing_mode="stretch_width",
)

def on_sql_change(*events):
    for event in events:
        if event.name == "sql":
            sql_display.object = f"```sql\n{event.new or 'SELECT * FROM df'}\n```"

component.param.watch(on_sql_change, ["sql"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
The quak data profiler renders correctly with Panel's AnyWidget pane.
DuckDB-WASM loads in-browser and the interactive table/column profiler works.
The <code>sql</code> trait syncs from browser to Python, reflecting user interactions
as executable SQL queries.
<br><br>
<strong>Note:</strong> quak uses DuckDB-WASM which requires <code>SharedArrayBuffer</code>.
This is only available when the page is served with
<code>Cross-Origin-Opener-Policy: same-origin</code> and
<code>Cross-Origin-Embedder-Policy: require-corp</code> headers.
GitHub Codespaces sets these headers automatically.
For standalone <code>panel serve</code>, you need to add these headers
via a custom Tornado <code>OutputTransform</code> — see the
<a href="https://panel.holoviz.org/reference/panes/AnyWidget.html">AnyWidget reference guide</a>.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# quak Data Profiler — Panel AnyWidget Example

[GitHub](https://github.com/manzt/quak) | [Docs](https://github.com/manzt/quak#readme)

**quak** is a scalable data profiler built on DuckDB and Mosaic. It renders
tabular data as an interactive profiler where you can:

- **Mouse over** column headers to see distributions
- **Click columns** to sort
- **Cross-filter** by selecting ranges in column summaries
- **Slice rows** by scrolling through the table

All interactions are captured as SQL queries shown below.

## How It Works

The quak widget is wrapped with `pn.pane.AnyWidget()` and rendered natively
in Panel. The `sql` traitlet is watched via `pane.component.param.watch()`
to reactively display the current query.
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### Interactive Data Profiler"),
    anywidget_pane,
    pn.pane.Markdown("### Current SQL Query"),
    sql_display,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
