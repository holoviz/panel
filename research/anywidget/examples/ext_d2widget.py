"""
d2-widget Example with Bidirectional Sync
==========================================

This example demonstrates using the d2-widget library's Widget
with Panel's AnyWidget pane and bidirectional sync between the widget
and Panel controls.

D2 is a modern diagram scripting language that turns text into diagrams.
The d2-widget package provides an anywidget wrapper that compiles and
renders D2 diagrams entirely in the browser using WASM.

GitHub: https://github.com/peter-gy/d2-widget
D2 Language: https://d2lang.com
D2 Playground: https://play.d2lang.com

Required package:
    pip install d2-widget

Run with:
    panel serve research/anywidget/examples/ext_d2widget.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the D2 diagram renders (shows a flowchart)
    3. Edit the D2 code in the TextAreaInput on the right and press Enter
       or click away -- the diagram should re-render
    4. Try the preset buttons for different diagram styles
    5. Check that _svg output appears in the Synced Traits section
    6. Check the browser console for errors (F12)

Trait Name Collisions: NONE
    The d2-widget user-facing traits (diagram, options, _svg) do not
    collide with any Bokeh reserved model property names.
"""

from d2_widget import Widget as D2Widget

import panel as pn

pn.extension(sizing_mode="stretch_width")

# --- Sample D2 diagrams ---

SAMPLE_BASIC = """\
direction: right

Panel: {
  shape: rectangle
  style.fill: "#4FC3F7"
  style.font-color: "#fff"
}

AnyWidget: {
  shape: rectangle
  style.fill: "#81C784"
  style.font-color: "#fff"
}

D2: {
  shape: rectangle
  style.fill: "#FFB74D"
  style.font-color: "#fff"
}

Panel -> AnyWidget: wraps
AnyWidget -> D2: renders
""".strip()

SAMPLE_FLOWCHART = """\
direction: down

start: Start {shape: oval}
input: User Input
process: Process Data
decision: Valid? {shape: diamond}
output: Display Result
error: Show Error
end: End {shape: oval}

start -> input
input -> process
process -> decision
decision -> output: yes
decision -> error: no
error -> input: retry
output -> end
""".strip()

SAMPLE_SEQUENCE = """\
shape: sequence_diagram

Browser: {
  shape: person
}
Panel Server
Bokeh Model
AnyWidget Adapter
D2 WASM Compiler

Browser -> Panel Server: HTTP request
Panel Server -> Bokeh Model: Create model
Bokeh Model -> AnyWidget Adapter: Initialize
AnyWidget Adapter -> D2 WASM Compiler: Compile diagram
D2 WASM Compiler -> AnyWidget Adapter: SVG output
AnyWidget Adapter -> Browser: Render SVG
""".strip()

SAMPLE_CLASS = """\
direction: right

Viewable: {
  shape: class
  render()
  servable()
}

Reactive: {
  shape: class
  param
  _process_events()
}

ReactiveESM: {
  shape: class
  _esm: str
  _render_esm()
}

AnyWidgetComponent: {
  shape: class
  _anywidget_trait_values: dict
  _protocol_adapter()
}

Viewable -> Reactive
Reactive -> ReactiveESM
ReactiveESM -> AnyWidgetComponent
""".strip()

PRESETS = {
    "Basic (Panel + AnyWidget + D2)": SAMPLE_BASIC,
    "Flowchart": SAMPLE_FLOWCHART,
    "Sequence Diagram": SAMPLE_SEQUENCE,
    "Class Diagram (Panel hierarchy)": SAMPLE_CLASS,
}

# --- Create the D2 widget ---

d2_widget = D2Widget(diagram=SAMPLE_BASIC)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(d2_widget, height=500)

# Access the component for param-based sync
component = anywidget_pane.component

# --- Panel controls ---

diagram_input = pn.widgets.TextAreaInput(
    name="D2 Diagram Code",
    value=SAMPLE_BASIC,
    height=300,
    width=400,
)

preset_select = pn.widgets.Select(
    name="Preset Diagrams",
    options=list(PRESETS.keys()),
    value="Basic (Panel + AnyWidget + D2)",
    width=400,
)

# --- Synced traits display ---

trait_display = pn.pane.JSON(
    {
        "diagram": d2_widget.diagram[:100] + "..." if len(d2_widget.diagram) > 100 else d2_widget.diagram,
        "options": d2_widget.options,
        "_svg": "(rendered after load)" if not d2_widget._svg else d2_widget._svg[:100] + "...",
    },
    name="Synced Traits",
    depth=2,
    width=400,
)

# --- Bidirectional sync ---

# When user selects a preset, update the text area and the widget
def on_preset_change(event):
    new_diagram = PRESETS.get(event.new, SAMPLE_BASIC)
    diagram_input.value = new_diagram
    component.diagram = new_diagram

preset_select.param.watch(on_preset_change, "value")

# When user edits the text area, update the widget
def on_diagram_edit(event):
    component.diagram = event.new

diagram_input.param.watch(on_diagram_edit, "value")

# When the component diagram or _svg changes, update the trait display
def on_component_change(*events):
    for event in events:
        if event.name == "diagram":
            diagram_input.value = event.new
    # Update trait display
    trait_display.object = {
        "diagram": component.diagram[:100] + "..." if len(component.diagram) > 100 else component.diagram,
        "options": getattr(component, 'options', {}),
        "_svg": component._svg[:100] + "..." if component._svg else "(not yet rendered)",
    }

component.param.watch(on_component_change, ["diagram", "_svg"])

# --- Layout ---

status_banner = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
D2 diagrams render correctly via WASM compilation in the browser.
Bidirectional sync of the <code>diagram</code> trait works.
The <code>_svg</code> output trait is synced back to Python.
No trait name collisions with Bokeh reserved names.
</p>
</div>
""")

header = pn.pane.Markdown("""
# d2-widget -- D2 Diagram Language

**[D2](https://d2lang.com)** is a modern diagram scripting language that turns
text into diagrams. The **d2-widget** anywidget package compiles D2 code to SVG
entirely in the browser using a WASM build of the D2 compiler.

## How to Use

1. **Edit the D2 code** in the text area on the right, then click away or
   press Tab to update the diagram.
2. **Choose a preset** from the dropdown to load example diagrams.
3. **Watch the SVG output** in the Synced Traits section below the controls.

Learn D2 syntax at [d2lang.com/tour](https://d2lang.com/tour/intro/).
""")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    preset_select,
    diagram_input,
    pn.pane.Markdown("## Synced Traits"),
    trait_display,
    width=450,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Diagram"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
).servable()
