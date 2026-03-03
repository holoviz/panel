"""
widget-code-input Example -- Interactive Code Editor
=====================================================

This example demonstrates using widget-code-input's WidgetCodeInput
(a CodeMirror-based code editor) with Panel's AnyWidget pane.

WidgetCodeInput provides an interactive Python function editor with syntax
highlighting and live editing. Users type code in the editor and the
function_body trait syncs back to Python.

GitHub: https://github.com/odea-project/widget-code-input

Key traitlets:
    - function_name (Unicode): Name of the function being edited
    - function_parameters (Unicode): Parameter string (e.g., "x, y")
    - function_body (Unicode): The code body typed by the user
    - code_theme (Unicode): Editor theme (e.g., "basicLight", "basicDark")
    - docstring (Any): Function docstring
    - name (Unicode): COLLIDES with Panel's name param -> renamed to w_name

Required package:
    pip install widget-code-input

Run with:
    panel serve research/anywidget/examples/ext_codeinput.py
"""

from widget_code_input import WidgetCodeInput

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the WidgetCodeInput widget
# ---------------------------------------------------------------------------

widget = WidgetCodeInput(
    function_name="my_function",
    function_parameters="x, y",
)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=300)

# ---------------------------------------------------------------------------
# 2. Access the component and set up bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Panel TextInput to change function_name from Python
name_input = pn.widgets.TextInput(
    name="Function Name (Panel)",
    value=component.function_name,
    width=300,
)

# Panel -> Widget: update function_name when Panel input changes
name_input.param.watch(
    lambda e: setattr(component, 'function_name', e.new), ['value']
)

# Widget -> Panel: update Panel input when widget changes function_name
component.param.watch(
    lambda e: setattr(name_input, 'value', e.new), ['function_name']
)

# Display for function_body (read from the component)
body_display = pn.pane.Markdown(
    pn.bind(
        lambda body: f"**Current function_body:**\n```python\n{body or '(empty)'}\n```",
        component.param.function_body
    ),
    sizing_mode="stretch_width",
)

# Display for the renamed 'name' trait (w_name)
w_name_display = pn.pane.Markdown(
    pn.bind(
        lambda wn: f"**w_name (renamed from 'name'):** `{wn}`",
        component.param.w_name
    ),
    sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# widget-code-input -- Panel AnyWidget Example

**widget-code-input** provides an interactive CodeMirror-based Python
function editor. It syncs the function name, parameters, body, and
docstring as traitlets.

## How to Test

1. **Type code** in the editor below -- the `function_body` display
   should update in real time.
2. **Change the function name** using the Panel TextInput -- the editor
   header should update to show the new function name.
3. The `name` traitlet collides with Panel's built-in `name` param,
   so it is renamed to `w_name` on the component.

## Trait Collision Note

The `name` traitlet from WidgetCodeInput collides with Panel's `name`
parameter. Panel automatically renames it to `w_name`. Access it via
`pane.component.w_name` or check `pane.component._trait_name_map`.
""", sizing_mode="stretch_width")

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
CodeMirror editor renders correctly with syntax highlighting. The <code>function_body</code>
trait syncs from browser to Python in real time. The <code>name</code> trait collides with
Panel's built-in <code>name</code> param and is renamed to <code>w_name</code>.
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### Code Editor"),
    anywidget_pane,
    pn.pane.Markdown("### Controls & Sync"),
    name_input,
    body_display,
    w_name_display,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
