"""
ipyclipboard Example -- Browser Clipboard Access
==================================================

This example demonstrates using ipyclipboard's Clipboard widget
with Panel's AnyWidget pane. The widget provides browser clipboard
read access via the Clipboard API.

GitHub: https://github.com/nickmcintyre/ipyclipboard

Key traitlets:
    - value (Unicode): The current clipboard text content (synced from browser)

The widget renders a "Paste" button in the browser. When clicked, it reads
the clipboard content and syncs the text to the `value` traitlet. Note that
clipboard access requires user interaction and browser permission.

Required package:
    pip install ipyclipboard

Run with:
    panel serve research/anywidget/examples/ext_ipyclipboard.py
"""

from ipyclipboard import Clipboard

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Clipboard widget
# ---------------------------------------------------------------------------

widget = Clipboard()

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=100)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Display synced clipboard content
# ---------------------------------------------------------------------------

# Show the clipboard value synced from the browser
clipboard_display = pn.pane.Markdown(
    pn.bind(
        lambda val: f"**Clipboard content:**\n```\n{val or '(empty -- click Paste in the widget above)'}\n```",
        component.param.value,
    ),
    sizing_mode="stretch_width",
)

# Character count
char_count = pn.pane.Markdown(
    pn.bind(
        lambda val: f"**Character count:** {len(val)}" if val else "**Character count:** 0",
        component.param.value,
    ),
    sizing_mode="stretch_width",
)

# History of pastes
paste_history = pn.widgets.TextAreaInput(
    name="Paste History",
    value="",
    height=150,
    disabled=True,
    sizing_mode="stretch_width",
)

paste_count = pn.widgets.IntInput(name="Paste Count", value=0, disabled=True, width=100)


def on_value_change(event):
    if event.new:
        paste_count.value += 1
        prefix = paste_history.value
        separator = "\n---\n" if prefix else ""
        paste_history.value = f"{prefix}{separator}[{paste_count.value}] {event.new}"


component.param.watch(on_value_change, ["value"])

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
The Clipboard widget renders a "Paste" button. Clicking it reads the browser
clipboard and syncs the text to the <code>value</code> traitlet. The value syncs
correctly to Panel.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipyclipboard -- Browser Clipboard Reader

[GitHub](https://github.com/nickmcintyre/ipyclipboard)

Access the browser clipboard from Python via the Clipboard API.

## How to Test

1. **Copy some text** to your clipboard (Ctrl+C / Cmd+C).
2. **Click the "Paste" button** rendered by the widget above.
3. Your browser may ask for clipboard permission -- grant it.
4. The **Clipboard content** display below should show your pasted text.
5. Each paste is logged in the **Paste History** area.

**Note:** Clipboard access requires HTTPS or localhost and a user gesture
(clicking the button). It will not work in some restricted browser contexts.
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### Clipboard Widget"),
    anywidget_pane,
    pn.pane.Markdown("### Synced Output"),
    clipboard_display,
    char_count,
    paste_count,
    pn.pane.Markdown("### Paste History"),
    paste_history,
    sizing_mode="stretch_width",
    max_width=800,
).servable()
