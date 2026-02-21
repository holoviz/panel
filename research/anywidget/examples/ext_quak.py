"""
quak Example — Scalable Data Profiler
======================================

This example demonstrates using quak's Widget (a scalable data profiler
for tables) with Panel's AnyWidget pane.

quak provides an interactive data profiler built on DuckDB and Mosaic.
Users can mouse over column summaries, cross-filter, sort, and slice rows.
Interactions are captured as executable SQL queries.

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

header = pn.pane.Markdown("""
# quak Data Profiler — Panel AnyWidget Example

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
    header,
    pn.pane.Markdown("### Interactive Data Profiler"),
    anywidget_pane,
    pn.pane.Markdown("### Current SQL Query"),
    sql_display,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
