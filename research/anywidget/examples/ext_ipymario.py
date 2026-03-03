"""
ipymario Example — Custom Message Demo
=======================================

This example demonstrates using ipymario with Panel's AnyWidget pane,
including triggering the Mario animation from Python via custom messages
(``widget.send()``) and bidirectional sync for gain/duration/size.

How it works
------------
ipymario's ESM listens for ``model.on("msg:custom", ...)`` messages.
Sending ``{"type": "click"}`` from Python triggers the canvas click
handler which plays the chime sound and bounce animation.

The ``animate`` traitlet is just a boolean flag that controls whether the
bounce animation plays on click — it is NOT a trigger. Setting it to True
doesn't cause animation; a click event is required.

Browser-side clicks (clicking the Mario box directly) play the animation
but do NOT notify Python — ipymario's ESM doesn't call ``model.set()``
or ``model.send()`` on click, so the server-side counter can only track
programmatic plays via the Play button.

GitHub: https://github.com/LordPachimari/ipymario

Required package:
    pip install ipymario

Run with:
    panel serve research/anywidget/examples/ext_ipymario.py
"""

from ipymario import Widget

import panel as pn

pn.extension()

# Create the ipymario Widget
mario_widget = Widget(size=200)

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(mario_widget, width=400, height=400)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# Server-side counter: track programmatic plays
# ---------------------------------------------------------------------------

play_count = pn.widgets.IntInput(name="Play Count", value=0, disabled=True, width=100)
gain_slider = pn.widgets.FloatSlider(
    name="Volume", start=0.0, end=1.0, value=0.1, step=0.05, width=250
)
duration_slider = pn.widgets.FloatSlider(
    name="Duration", start=0.01, end=2.0, value=1.0, step=0.01, width=250
)
size_slider = pn.widgets.IntSlider(
    name="Block Size", start=50, end=500, value=200, step=25, width=250
)

# Sync gain/duration/size bidirectionally
def on_gain_change(event):
    component.gain = event.new

def on_duration_change(event):
    component.duration = event.new

def on_size_change(event):
    component.size = event.new

gain_slider.param.watch(on_gain_change, "value")
duration_slider.param.watch(on_duration_change, "value")
size_slider.param.watch(on_size_change, "value")

# Play button — sends custom message to trigger the ESM click handler
def play_mario(event):
    # ipymario's ESM listens for msg:custom with {"type": "click"}
    # which triggers canvas.click() → chime + bounce animation.
    mario_widget.send({"type": "click"})
    play_count.value += 1

play_button = pn.widgets.Button(
    name="Play Mario!", button_type="success", width=200
)
play_button.on_click(play_mario)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# ipymario -- Interactive Mario Sound Box

[GitHub](https://github.com/LordPachimari/ipymario)

Click the Mario "?" block to hear a coin chime and see a bounce animation!

## Two Ways to Play

| Action | What happens |
|--------|-------------|
| **Click the Mario block** directly | Plays the chime and animation in your browser. The Play Count stays the same because the server is not notified. |
| **Click the green "Play Mario!" button** | Sends a command from the server to the browser to play the chime. The Play Count increments because the server initiated it. |

## Adjust the Settings

- **Volume:** How loud the coin chime plays (0 = silent, 1 = full volume)
- **Duration:** How long the chime sound rings (in seconds)
- **Mario Size:** The pixel size of the Mario block (50--500)

Changes to these sliders take effect on the next play.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    play_button,
    pn.pane.Markdown("### Play Counter"),
    play_count,
    pn.pane.Markdown("### Settings"),
    gain_slider,
    duration_slider,
    size_slider,
    width=350,
)

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
The Mario "?" block renders and responds to clicks (plays coin chime + bounce animation).
<code>gain</code>, <code>duration</code>, and <code>size</code> traits sync from Python to browser.
Custom messages (<code>widget.send({"type": "click"})</code>) trigger animation from Python.
<br><br>
<strong>Caveat:</strong> The canvas may appear invisible in headless Chromium (no GPU).
Browser-side clicks do NOT notify Python (ipymario's ESM doesn't call <code>model.set()</code> on click).
</p>
</div>
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Mario Widget"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=900,
).servable()
