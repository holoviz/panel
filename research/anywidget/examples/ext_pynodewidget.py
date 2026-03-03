"""
pynodewidget Example -- Interactive Node Graph Editor
=====================================================

This example demonstrates using pynodewidget (a ReactFlow wrapper) with
Panel's AnyWidget pane and bidirectional sync. Users can visually build
data-processing workflows by dragging nodes from the sidebar, connecting
them with edges, and editing field values inside each node.

pynodewidget provides a GridBuilder API for defining node types with
headers, input/output handles, text fields, number fields, select
dropdowns, and boolean toggles -- all without writing any JavaScript.

GitHub: https://github.com/HenningScheufler/pynodewidget
Docs:   https://henningscheufler.github.io/pynodewidget/

Required package:
    pip install pynodewidget

Run with:
    panel serve research/anywidget/examples/ext_pynodewidget.py

Trait name collisions
---------------------
    height (Unicode '600px') -> renamed to w_height on the Panel component
        because Panel's height param is an int (pixels). Use
        component.w_height to read/write the widget's CSS height string.
"""

from pynodewidget import GridBuilder, NodeFlowWidget
from pynodewidget.models import (
    BaseHandle,
    BoolField,
    HeaderComponent,
    LabeledHandle,
    NumberField,
    SelectField,
    TextField,
)

import panel as pn

pn.extension()

# =====================================================================
# Create the NodeFlowWidget and register three node types
# =====================================================================

flow_widget = NodeFlowWidget(height="650px")

# --- Node Type 1: Data Source ----------------------------------------
grid_input = (
    GridBuilder.preset("simple_node")
    .slot("header", [
        HeaderComponent(
            id="header", label="Data Source", icon="", bgColor="#10b981"
        ),
    ])
    .slot("center", [
        TextField(id="source_name", value="DataSet-001"),
        SelectField(
            id="source_type",
            value="csv",
            options=["csv", "json", "parquet", "xlsx"],
        ),
        NumberField(id="sample_size", value=1000, min=100, max=10000),
    ])
    .slot("output", [
        BaseHandle(id="data_out", handle_type="output", label="Data"),
        BaseHandle(id="meta_out", handle_type="output", label="Meta"),
    ])
    .gap("8px")
    .build()
)
flow_widget.add_node_type(
    type_name="input_node", label="Input Node", icon="", grid_layout=grid_input
)

# --- Node Type 2: Processor -----------------------------------------
grid_proc = (
    GridBuilder.preset("three_column")
    .slot("header", [
        HeaderComponent(
            id="header", label="Processor", icon="", bgColor="#3b82f6"
        ),
    ])
    .slot("left", [
        LabeledHandle(id="data_in", handle_type="input", label="Input"),
        LabeledHandle(id="config_in", handle_type="input", label="Config"),
    ])
    .slot("center", [
        SelectField(
            id="method",
            value="standard",
            options=["standard", "advanced", "custom"],
        ),
        NumberField(id="threshold", value=50, min=0, max=100),
        BoolField(id="enable_cache", value=True),
    ])
    .slot("right", [
        LabeledHandle(id="result_out", handle_type="output", label="Result"),
        LabeledHandle(id="logs_out", handle_type="output", label="Logs"),
    ])
    .build()
)
flow_widget.add_node_type(
    type_name="processing_node",
    label="Processing Node",
    icon="",
    grid_layout=grid_proc,
)

# --- Node Type 3: Export Sink ----------------------------------------
grid_output = (
    GridBuilder.preset("simple_node")
    .slot("header", [
        HeaderComponent(
            id="header", label="Export", icon="", bgColor="#ef4444"
        ),
    ])
    .slot("input", [
        BaseHandle(id="data_in", handle_type="input", label="Data"),
    ])
    .slot("center", [
        TextField(id="output_path", value="/output/results.csv"),
        SelectField(
            id="format",
            value="csv",
            options=["csv", "json", "parquet", "xlsx"],
        ),
        BoolField(id="compress", value=False),
    ])
    .gap("8px")
    .build()
)
flow_widget.add_node_type(
    type_name="output_node", label="Output Node", icon="", grid_layout=grid_output
)

# =====================================================================
# Wrap with Panel's AnyWidget pane
# =====================================================================

anywidget_pane = pn.pane.AnyWidget(flow_widget, sizing_mode="stretch_width", height=700)
component = anywidget_pane.component

# =====================================================================
# Panel controls for bidirectional sync
# =====================================================================

fit_view_toggle = pn.widgets.Checkbox(name="Fit View", value=flow_widget.fit_view)

# Displays for synced trait values
edges_display = pn.pane.JSON({}, name="Edges", depth=2, width=400, height=200)
nodes_display = pn.pane.JSON({}, name="Nodes", depth=2, width=400, height=200)
node_values_display = pn.pane.JSON({}, name="Node Values", depth=3, width=400, height=200)
viewport_display = pn.pane.JSON(
    flow_widget.viewport, name="Viewport", depth=1, width=400, height=80
)

# Panel -> Widget sync
fit_view_toggle.param.watch(
    lambda e: setattr(component, "fit_view", e.new), "value"
)

# Widget -> Panel sync
def on_component_change(*events):
    for event in events:
        if event.name == "edges":
            edges_display.object = event.new if event.new else {}
        elif event.name == "nodes":
            nodes_display.object = event.new if event.new else {}
        elif event.name == "node_values":
            node_values_display.object = dict(event.new) if event.new else {}
        elif event.name == "viewport":
            viewport_display.object = event.new if event.new else {}
        elif event.name == "fit_view":
            fit_view_toggle.value = event.new

component.param.watch(
    on_component_change,
    ["edges", "nodes", "node_values", "viewport", "fit_view"],
)

# =====================================================================
# Layout
# =====================================================================

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 14px; margin: 8px 0 0 0;">
<strong>Upstream issue:</strong> pynodewidget's bundled ESM triggers a
React error #185 (<code>ReactDOM.render is no longer supported in React 18</code>)
inside Panel's rendering context. The canvas mounts but React nodes may fail
to render. This is a pynodewidget bundling issue, not a Panel bug.
<br/><br/>
<strong>Trait collision:</strong> <code>height</code> (Unicode, e.g. "600px") is renamed to
<code>w_height</code> on the Panel component because it conflicts with Panel's
<code>height</code> param (int, pixels).
</p>
</div>
""")

header = pn.pane.Markdown("""
# pynodewidget -- Interactive Node Graph Editor

[GitHub](https://github.com/HenningScheufler/pynodewidget) |
[Docs](https://henningscheufler.github.io/pynodewidget/)

Build data-processing pipelines visually using ReactFlow nodes.

## How to Use

1. **Add nodes** -- right-click on the canvas or drag from the sidebar
   (the sidebar appears on the left of the ReactFlow canvas).
2. **Connect nodes** -- drag from an output handle (right side of a node)
   to an input handle (left side of another node).
3. **Edit fields** -- click inside a node to change text, numbers, or
   select dropdowns.
4. **Watch sync** -- the Edges, Nodes, and Node Values panels on the right
   update in real time as you interact with the graph.

Three node types are pre-registered: **Input Node** (green), **Processing
Node** (blue), and **Output Node** (red).
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    fit_view_toggle,
    pn.pane.Markdown("### Viewport"),
    viewport_display,
    pn.pane.Markdown("### Edges (real-time)"),
    edges_display,
    pn.pane.Markdown("### Node Values (real-time)"),
    node_values_display,
    width=420,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Node Graph Canvas"),
            anywidget_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1400,
).servable()
