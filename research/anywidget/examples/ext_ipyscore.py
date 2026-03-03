"""
ipyscore Example -- Music Score Renderer (VexFlow)
====================================================

This example demonstrates using ipyscore's Widget with Panel's AnyWidget pane.
ipyscore renders music scores in the browser using VexFlow, a JavaScript
music notation rendering library.

GitHub: https://github.com/nickmcintyre/ipyscore

Key traitlets (public):
    - width (Int): Width of the score canvas (default: 500)
    - height (Int): Height of the score canvas (default: 500)

Key traitlets (private, used by the builder API):
    - _notes (Unicode): Note string (e.g. "C4/q, D4/q, E4/q")
    - _draw (Bool): Toggle trigger to render the score
    - _clef (Unicode): Clef type (e.g. "treble", "bass")
    - _time_signature (Unicode): Time signature string (e.g. "4/4")

The widget uses a builder-pattern API:
    score = widget.new_score()
    notes = score.notes("C4/q, D4/q, E4/q, F4/q")
    voice = score.voice(notes)
    system = widget.new_system()
    stave = system.add_stave(voices=[voice])
    stave.add_clef("treble").add_time_signature("4/4")
    widget.draw()

Required package:
    pip install ipyscore

Run with:
    panel serve research/anywidget/examples/ext_ipyscore.py
"""

from ipyscore import Widget as ScoreWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the ScoreWidget and build an initial score
# ---------------------------------------------------------------------------

widget = ScoreWidget(width=700, height=200)

# Build a simple melody: C major scale quarter notes
score = widget.new_score()
notes = score.notes("C4/q, D4/q, E4/q, F4/q")
voice = score.voice(notes)
system = widget.new_system()
stave = system.add_stave(voices=[voice])
stave.add_clef("treble").add_time_signature("4/4")
widget.draw()

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=250)
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Controls for building new scores
# ---------------------------------------------------------------------------

# Predefined melodies
MELODIES = {
    "C Major Scale": "C4/q, D4/q, E4/q, F4/q",
    "G Major Arpeggio": "G4/q, B4/q, D5/q, G5/q",
    "Simple Chord Progression": "C4/q, E4/q, G4/q, C5/q",
    "Descending Scale": "C5/q, B4/q, A4/q, G4/q",
    "Whole Notes": "C4/w",
    "Eighth Notes": "C4/8, D4/8, E4/8, F4/8, G4/8, A4/8, B4/8, C5/8",
    "Mixed Durations": "C4/h, E4/q, G4/q",
}

melody_selector = pn.widgets.Select(
    name="Melody Preset",
    options=list(MELODIES.keys()),
    value="C Major Scale",
    width=250,
)

custom_notes = pn.widgets.TextInput(
    name="Custom Notes (VexFlow format)",
    value="C4/q, D4/q, E4/q, F4/q",
    placeholder="e.g. C4/q, D4/8, E4/8, F4/h",
    width=400,
)

clef_selector = pn.widgets.Select(
    name="Clef",
    options=["treble", "bass", "alto", "tenor"],
    value="treble",
    width=150,
)

time_sig_selector = pn.widgets.Select(
    name="Time Signature",
    options=["4/4", "3/4", "6/8", "2/4"],
    value="4/4",
    width=150,
)

width_slider = pn.widgets.IntSlider(
    name="Score Width",
    start=400,
    end=1000,
    value=700,
    step=50,
    width=250,
)

height_slider = pn.widgets.IntSlider(
    name="Score Height",
    start=100,
    end=500,
    value=200,
    step=25,
    width=250,
)


def render_score(event=None):
    """Rebuild and render the score with current settings."""
    # Update widget dimensions
    component.width = width_slider.value
    component.height = height_slider.value

    # Build new score using the builder API
    s = widget.new_score()
    n = s.notes(custom_notes.value)
    v = s.voice(n)
    sys = widget.new_system()
    stv = sys.add_stave(voices=[v])
    stv.add_clef(clef_selector.value).add_time_signature(time_sig_selector.value)
    widget.draw()


def on_melody_change(event):
    custom_notes.value = MELODIES[event.new]
    render_score()


melody_selector.param.watch(on_melody_change, "value")

render_button = pn.widgets.Button(
    name="Render Score", button_type="primary", width=200
)
render_button.on_click(render_score)

# Also render on clef/time sig changes
clef_selector.param.watch(render_score, "value")
time_sig_selector.param.watch(render_score, "value")
width_slider.param.watch(render_score, "value")
height_slider.param.watch(render_score, "value")

# Display current notes trait (Widget -> Panel)
notes_display = pn.pane.Markdown(
    pn.bind(
        lambda n: f"**Current _notes trait:** `{n}`" if n else "**Current _notes trait:** (empty)",
        component.param._notes,
    ),
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
ipyscore renders music notation using VexFlow in the browser. Score construction
via the Python builder API works correctly. The <code>width</code>, <code>height</code>,
and internal traits (<code>_notes</code>, <code>_clef</code>, <code>_time_signature</code>)
sync as expected.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# ipyscore -- Music Score Renderer

[GitHub](https://github.com/nickmcintyre/ipyscore)

Render music notation interactively in the browser using VexFlow.

## How to Test

1. **Select a melody preset** from the dropdown to load predefined notes.
2. **Edit notes** in the "Custom Notes" field using VexFlow format
   (e.g., ``C4/q`` = C4 quarter note, ``D4/h`` = D4 half note,
   ``E4/w`` = whole note, ``F4/8`` = eighth note).
3. **Click "Render Score"** to update the display with custom notes.
4. **Change the clef** (treble, bass, alto, tenor) or **time signature**.
5. **Adjust dimensions** with the width/height sliders.

## VexFlow Note Format

| Duration | Symbol | Example |
|----------|--------|---------|
| Whole    | /w     | C4/w    |
| Half     | /h     | D4/h    |
| Quarter  | /q     | E4/q    |
| Eighth   | /8     | F4/8    |
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("### Melody"),
    melody_selector,
    custom_notes,
    render_button,
    pn.pane.Markdown("### Score Settings"),
    pn.Row(clef_selector, time_sig_selector),
    pn.Row(width_slider, height_slider),
    pn.pane.Markdown("### Sync"),
    notes_display,
    width=450,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Music Score"),
            anywidget_pane,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
