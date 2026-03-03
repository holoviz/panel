"""
PGLite Example — PostgreSQL in the Browser (WASM)
===================================================

This example demonstrates using jupyter-anywidget-pglite with Panel's AnyWidget
pane. PGLite runs a full PostgreSQL database in the browser using WebAssembly,
allowing SQL queries without any server infrastructure.

GitHub: https://github.com/nickmcintyre/jupyter-anywidget-pglite

Key traitlets:
    - code_content (Unicode): SQL query to execute
    - response (Dict): Query result from the browser-side PGLite engine
    - headless (Bool): Whether to render headlessly
    - audio (Bool): Whether to enable audio feedback
    - extensions (List): PostgreSQL extensions to load
    - multiexec (Bool): Execute multiple statements
    - multiline (Unicode): Multi-line SQL input

Required package:
    pip install jupyter-anywidget-pglite

Run with:
    panel serve research/anywidget/examples/ext_pglite.py
"""

from jupyter_anywidget_pglite import postgresWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the PGLite widget
# ---------------------------------------------------------------------------

widget = postgresWidget()

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=500, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. SQL query controls
# ---------------------------------------------------------------------------

SAMPLE_QUERIES = {
    "Create Table": """\
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    age INTEGER
);""",
    "Insert Data": """\
INSERT INTO users (name, email, age) VALUES
    ('Alice', 'alice@example.com', 30),
    ('Bob', 'bob@example.com', 25),
    ('Charlie', 'charlie@example.com', 35);""",
    "Select All": "SELECT * FROM users;",
    "Filter Query": "SELECT name, age FROM users WHERE age > 28;",
    "Count Query": "SELECT COUNT(*) as total_users FROM users;",
}

query_select = pn.widgets.Select(
    name="Sample Queries",
    options=list(SAMPLE_QUERIES.keys()),
    value="Create Table",
    width=250,
)

sql_editor = pn.widgets.TextAreaInput(
    name="SQL Query",
    value=SAMPLE_QUERIES["Create Table"],
    height=150,
    sizing_mode="stretch_width",
)

run_button = pn.widgets.Button(name="Run Query", button_type="primary", width=150)


def on_query_select(event):
    sql_editor.value = SAMPLE_QUERIES[event.new]


query_select.param.watch(on_query_select, "value")


def on_run_query(event):
    component.code_content = sql_editor.value


run_button.param.watch(on_run_query, "clicks")

# Sync code_content bidirectionally
sql_editor.param.watch(
    lambda e: setattr(component, 'code_content', e.new), ['value']
)

# Display query results
response_display = pn.pane.JSON(
    pn.bind(lambda r: r if r else {}, component.param.response),
    name="Query Response",
    depth=3,
    height=200,
    sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
PGLite runs a full PostgreSQL database in the browser via WebAssembly. The
<code>code_content</code> trait sends SQL queries, and the <code>response</code>
trait returns results. No server infrastructure needed.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# jupyter-anywidget-pglite — PostgreSQL in the Browser

[GitHub](https://github.com/nickmcintyre/jupyter-anywidget-pglite)

Run SQL queries directly in the browser using PGLite (PostgreSQL compiled to
WebAssembly). Create tables, insert data, and query — all client-side.

## How to Test

1. Click **"Run Query"** with the default CREATE TABLE query.
2. Switch to **"Insert Data"** and run it to populate the table.
3. Switch to **"Select All"** to see the data in the response panel.
4. Try the filter and count queries.
5. Edit the SQL directly in the text area.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Query Controls"),
    query_select,
    sql_editor,
    run_button,
    pn.pane.Markdown("### Query Response"),
    response_display,
    sizing_mode="stretch_width",
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### PGLite Console"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
        sizing_mode="stretch_width",
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
