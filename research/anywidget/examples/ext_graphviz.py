"""
jupyter-anywidget-graphviz Example -- Graphviz DOT Renderer
============================================================

This example demonstrates using jupyter-anywidget-graphviz's graphvizWidget
with Panel's AnyWidget pane. The widget renders Graphviz DOT source as SVG
in the browser using a WASM-compiled Graphviz engine.

GitHub: https://github.com/nickmcintyre/jupyter-anywidget-graphviz

Key traitlets:
    - code_content (Unicode): The DOT source string to render
    - svg (Unicode): The rendered SVG output (read-only, synced from browser)
    - response (Dict): Status dict (e.g. {'status': 'initialising'})
    - headless (Bool): Whether to render headlessly
    - audio (Bool): Whether to enable audio feedback

Note: The package also exports a `Widget` class, but that is just a simple
counter button demo. The actual Graphviz renderer is `graphvizWidget`.

Required package:
    pip install jupyter-anywidget-graphviz

Run with:
    panel serve research/anywidget/examples/ext_graphviz.py
"""

from jupyter_anywidget_graphviz import graphvizWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the graphvizWidget with an initial DOT source
# ---------------------------------------------------------------------------

DEFAULT_DOT = """\
digraph G {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fillcolor="#e8f4fd", fontname="Helvetica"];
    edge [color="#666666"];

    A [label="Start", fillcolor="#d4edda"];
    B [label="Process"];
    C [label="Decision", shape=diamond, fillcolor="#fff3cd"];
    D [label="Output"];
    E [label="End", fillcolor="#f8d7da"];

    A -> B -> C;
    C -> D [label="yes"];
    C -> E [label="no"];
    D -> E;
}
"""

widget = graphvizWidget(code_content=DEFAULT_DOT)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=500)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Bidirectional sync: Panel controls <-> widget traits
# ---------------------------------------------------------------------------

# Panel TextAreaInput for editing the DOT source
dot_editor = pn.widgets.TextAreaInput(
    name="DOT Source",
    value=DEFAULT_DOT,
    height=250,
    sizing_mode="stretch_width",
)

# Panel -> Widget: update code_content when editor changes
dot_editor.param.watch(
    lambda e: setattr(component, 'code_content', e.new), ['value']
)

# Widget -> Panel: update editor when code_content changes from widget
component.param.watch(
    lambda e: setattr(dot_editor, 'value', e.new), ['code_content']
)

# Display the rendered SVG source (read-only, synced from browser)
svg_display = pn.pane.Markdown(
    pn.bind(
        lambda svg: f"**SVG output length:** {len(svg)} chars" if svg else "**SVG:** (not yet rendered)",
        component.param.svg,
    ),
    sizing_mode="stretch_width",
)

# Display widget response/status
status_display = pn.pane.JSON(
    pn.bind(lambda r: r if r else {}, component.param.response),
    name="Widget Status",
    depth=2,
    height=80,
)

# Preset graph selector
PRESETS = {
    "Flowchart": DEFAULT_DOT,
    "Binary Tree": """\
digraph BTree {
    node [shape=circle, style=filled, fillcolor="#e8f4fd"];
    1 -> 2; 1 -> 3;
    2 -> 4; 2 -> 5;
    3 -> 6; 3 -> 7;
}
""",
    "State Machine": """\
digraph FSM {
    rankdir=LR;
    node [shape=doublecircle]; S0 S3;
    node [shape=circle];
    S0 -> S1 [label="a"];
    S1 -> S2 [label="b"];
    S2 -> S3 [label="a"];
    S3 -> S1 [label="b"];
    S1 -> S1 [label="a"];
}
""",
    "Simple Pipeline": """\
digraph Pipeline {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fillcolor="#dfe6e9"];
    Ingest -> Transform -> Validate -> Load -> Report;
}
""",
}

preset_selector = pn.widgets.Select(
    name="Preset Graphs",
    options=list(PRESETS.keys()),
    value="Flowchart",
    width=200,
)


def on_preset_change(event):
    dot_editor.value = PRESETS[event.new]


preset_selector.param.watch(on_preset_change, "value")

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
The Graphviz widget renders DOT source as SVG in the browser via WASM.
The <code>code_content</code> trait syncs bidirectionally with Panel controls.
The <code>svg</code> trait provides the rendered SVG output.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# jupyter-anywidget-graphviz -- DOT Graph Renderer

[GitHub](https://github.com/nickmcintyre/jupyter-anywidget-graphviz)

Render Graphviz DOT graphs interactively in the browser using a WASM-compiled
Graphviz engine.

## How to Test

1. **Select a preset graph** from the dropdown to load a predefined DOT source.
2. **Edit the DOT source** in the text area -- the graph should re-render.
3. The **SVG output length** updates when the widget finishes rendering.
4. The **Widget Status** shows the current rendering state.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    preset_selector,
    pn.pane.Markdown("### DOT Source Editor"),
    dot_editor,
    pn.pane.Markdown("### Sync Status"),
    svg_display,
    status_display,
    width=400,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Rendered Graph"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
