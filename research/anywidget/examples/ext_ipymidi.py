"""
ipymidi Example -- Web MIDI Interface
=====================================

This example demonstrates using ipymidi's MIDIInterface with Panel's
AnyWidget pane. ipymidi provides access to the Web MIDI API, allowing
detection of connected MIDI devices and monitoring of MIDI events
(note on/off, control change, etc.) directly in the browser.

Note: MIDIInterface sets ``_view_name = None`` (headless widget), so it
does not render any visible DOM element. The AnyWidget pane still syncs
all traitlets. The ``enabled`` trait becomes True after the browser
grants MIDI access (requires user interaction with a security prompt).
Since there is no visual widget, interaction happens entirely through
the Panel controls and status displays.

GitHub: https://github.com/nickmcintyre/ipymidi

Key traitlets:
    - enabled (Bool, read-only): Whether MIDI access has been granted
    - _inputs (List, read-only): List of detected MIDI input devices

Required package:
    pip install ipymidi

Run with:
    panel serve research/anywidget/examples/ext_ipymidi.py
"""

from ipymidi import get_interface

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the MIDIInterface widget (singleton)
# ---------------------------------------------------------------------------

midi_interface = get_interface()

# Wrap with Panel's AnyWidget pane.
# Note: ipymidi sets _view_name=None so no visible element is rendered.
anywidget_pane = pn.pane.AnyWidget(midi_interface, height=50)

# ---------------------------------------------------------------------------
# 2. Access the component and set up bidirectional sync
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# Display for the 'enabled' trait (read-only from Python side).
# This updates reactively whenever the browser grants MIDI access.
enabled_display = pn.pane.Markdown(
    pn.bind(
        lambda enabled: (
            "**MIDI Enabled:** "
            "<span style='color: green; font-weight: bold;'>Yes -- access granted</span>"
            if enabled else
            "**MIDI Enabled:** "
            "<span style='color: red; font-weight: bold;'>No -- click the button below</span>"
        ),
        component.param.enabled,
    ),
    sizing_mode="stretch_width",
)

# Button to request MIDI access. This calls midi_interface.enable() which
# sends a command to the browser JS to request Web MIDI API access.
# The browser will show a security prompt; once granted, enabled -> True.
enable_button = pn.widgets.Button(
    name="Request MIDI Access",
    button_type="primary",
    width=250,
)


def on_enable_click(event):
    midi_interface.enable()


enable_button.on_click(on_enable_click)

def _format_inputs(iface):
    """Format MIDI input device information for display."""
    if not iface.enabled:
        return "**MIDI Inputs:** *(enable MIDI first)*"
    try:
        inputs = iface._inputs
    except Exception:
        inputs = []
    if not inputs:
        return (
            "**MIDI Inputs:** No devices detected. "
            "Connect a MIDI device and re-enable."
        )
    lines = ["**MIDI Inputs:**\n"]
    for i, inp in enumerate(inputs):
        if isinstance(inp, dict):
            name = inp.get("name", "Unknown")
            manufacturer = inp.get("manufacturer", "Unknown")
            lines.append(
                f"- **{i + 1}.** {name} (manufacturer: {manufacturer})"
            )
        else:
            lines.append(f"- **{i + 1}.** {inp}")
    return "\n".join(lines)


# Display info about detected MIDI inputs.
# _inputs is a read-only list of dicts describing connected MIDI devices.
inputs_display = pn.pane.Markdown(
    pn.bind(
        lambda enabled: _format_inputs(midi_interface),
        component.param.enabled,
    ),
    sizing_mode="stretch_width",
)


# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# ipymidi -- Web MIDI Interface

[GitHub](https://github.com/nickmcintyre/ipymidi)

Access MIDI devices from Python via the Web MIDI API. ipymidi wraps the
browser's Web MIDI API as an anywidget, letting you detect inputs, receive
MIDI messages (note on, note off, control change), and react to them in
Python.

## How to Test

1. **Click "Request MIDI Access"** below -- the browser will show a
   security prompt asking for permission to access MIDI devices.
2. **Grant access** -- the "MIDI Enabled" indicator should turn green.
3. **Connect a MIDI device** (keyboard, controller, etc.) -- it should
   appear in the MIDI Inputs list below.

## Architecture Note

MIDIInterface is a **headless** anywidget (``_view_name = None``). It does
not render any visible HTML element. Instead, it runs JavaScript in the
background to interact with the Web MIDI API and syncs state back to Python
via traitlets. Panel's AnyWidget pane handles the trait sync even though
there is nothing visual to display.

The ``enabled`` trait is **read-only** from the Python side -- it can only
become True when the browser grants MIDI access after ``enable()`` is called.

## Requirements

- A browser that supports the Web MIDI API (Chrome, Edge, Opera)
- Firefox requires the ``dom.webmidi.enabled`` flag
- Physical MIDI device connected via USB or Bluetooth
- HTTPS or localhost (Web MIDI requires a secure context)
""", sizing_mode="stretch_width")

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
This is a <strong>headless</strong> widget -- no visible element is rendered in the browser.
Trait sync works (the <code>enabled</code> flag updates when MIDI access is granted), but
MIDI event callbacks (<code>noteon</code>, <code>noteoff</code>) require the full Jupyter
kernel message protocol and do not fire in a pure Panel serve context. Use this example
to verify that the headless anywidget pattern and trait sync work correctly.
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### MIDI Controls"),
    enable_button,
    enabled_display,
    pn.pane.Markdown("---"),
    inputs_display,
    pn.pane.Markdown("### AnyWidget Pane (headless -- no visible element)"),
    anywidget_pane,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
