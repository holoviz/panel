"""
ipymario Example — Server Communication Demo
==============================================

This example demonstrates the ipymario library rendered natively in Panel
with bidirectional sync. A Panel button triggers the Mario animation, and
a counter tracks interactions on the server side.

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
# Server-side counter: track animation triggers
# ---------------------------------------------------------------------------

play_count = pn.widgets.IntInput(name="Play Count", value=0, disabled=True, width=100)
gain_slider = pn.widgets.FloatSlider(
    name="Volume (gain)", start=0.0, end=1.0, value=0.5, step=0.05, width=250
)
duration_slider = pn.widgets.FloatSlider(
    name="Duration", start=0.01, end=0.5, value=0.1, step=0.01, width=250
)
size_slider = pn.widgets.IntSlider(
    name="Mario Size", start=50, end=500, value=200, step=25, width=250
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

# Play button — triggers animation and increments counter
def play_mario(event):
    component.animate = True
    play_count.value += 1

play_button = pn.widgets.Button(
    name="Play Mario!", button_type="success", width=200
)
play_button.on_click(play_mario)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# ipymario — Server Communication Demo

This example renders **ipymario** (an anywidget) natively in Panel with
bidirectional sync between the widget and Panel controls.

## How It Works

- **Play Button:** Triggers the Mario animation via `component.animate = True`
  and increments a server-side counter
- **Volume / Duration / Size:** Panel sliders sync to the widget traitlets
  (`gain`, `duration`, `size`)

## Server Communication

The play counter demonstrates server-side state tracking. Each click:
1. Sets `component.animate = True` (syncs to browser, triggers animation)
2. Increments the Python counter (server-side state)
""")

controls = pn.Column(
    pn.pane.Markdown("### Controls"),
    play_button,
    pn.pane.Markdown("### Server Counter"),
    play_count,
    pn.pane.Markdown("### Widget Settings"),
    gain_slider,
    duration_slider,
    size_slider,
    width=350,
)

pn.Column(
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
