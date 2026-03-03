"""
moutils Example -- Copy to Clipboard Widget
=============================================

This example demonstrates using moutils' CopyToClipboard widget
with Panel's AnyWidget pane. The widget renders a button that copies
specified text to the browser clipboard.

GitHub: https://github.com/martinohanlon/moutils

Key traitlets:
    - text (Unicode): The text content to be copied to clipboard
    - button_text (Unicode): Label displayed on the copy button
    - success (Bool): Whether the last copy operation succeeded
    - success_text (Unicode): Text shown after a successful copy

Required package:
    pip install moutils

Run with:
    panel serve research/anywidget/examples/ext_moutils.py
"""

from moutils import CopyToClipboard

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the CopyToClipboard widget
# ---------------------------------------------------------------------------

widget = CopyToClipboard(
    text="Hello from Panel + AnyWidget!",
    button_text="Copy to Clipboard",
)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=80)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Bidirectional sync: Panel controls <-> widget traits
# ---------------------------------------------------------------------------

# Text to copy
text_input = pn.widgets.TextAreaInput(
    name="Text to Copy",
    value=component.text,
    height=100,
    sizing_mode="stretch_width",
)

# Button label
button_text_input = pn.widgets.TextInput(
    name="Button Label",
    value=component.button_text or "Copy to Clipboard",
    width=300,
)

# Panel -> Widget sync
text_input.param.watch(
    lambda e: setattr(component, 'text', e.new), ['value']
)
button_text_input.param.watch(
    lambda e: setattr(component, 'button_text', e.new), ['value']
)

# Widget -> Panel sync
component.param.watch(
    lambda e: setattr(text_input, 'value', e.new), ['text']
)
component.param.watch(
    lambda e: setattr(button_text_input, 'value', e.new), ['button_text']
)

# Display success status
success_display = pn.pane.Markdown(
    pn.bind(
        lambda s: "**Copy status:** Copied successfully!" if s else "**Copy status:** Waiting...",
        component.param.success,
    ),
    sizing_mode="stretch_width",
)

# Copy counter
copy_count = pn.widgets.IntInput(name="Copy Count", value=0, disabled=True, width=100)


def on_success_change(event):
    if event.new:
        copy_count.value += 1


component.param.watch(on_success_change, ["success"])

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
The CopyToClipboard widget renders a button that copies text to the browser clipboard.
The <code>text</code>, <code>button_text</code>, and <code>success</code> traits all sync
correctly with Panel.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# moutils -- Copy to Clipboard

[GitHub](https://github.com/martinohanlon/moutils)

A simple widget that copies text to the browser clipboard on button click.

## How to Test

1. **Edit the text** in the "Text to Copy" field below.
2. **Click the "Copy to Clipboard" button** rendered by the widget.
3. Your browser may ask for clipboard permission -- grant it.
4. **Paste** (Ctrl+V / Cmd+V) somewhere to verify the text was copied.
5. The **Copy status** and **Copy Count** should update on each copy.
6. Change the **Button Label** to customize the button text.
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### Copy Widget"),
    anywidget_pane,
    pn.pane.Markdown("### Controls"),
    text_input,
    button_text_input,
    pn.pane.Markdown("### Status"),
    success_display,
    copy_count,
    sizing_mode="stretch_width",
    max_width=800,
).servable()
