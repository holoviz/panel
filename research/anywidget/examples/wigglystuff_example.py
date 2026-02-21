"""
wigglystuff Example — One-Way Sync Limitation
==============================================

This example demonstrates using the wigglystuff library's tangle-style
inline sliders with Panel's AnyWidget pane.

KNOWN LIMITATION: The TangleSlider ESM does not implement a
`model.on("change:amount", ...)` handler, so external changes from Python
cannot update the TangleSlider display. Only TangleSlider -> Panel direction works.

Required package:
    pip install wigglystuff

Run with:
    panel serve research/anywidget/examples/wigglystuff_example.py
"""

import panel as pn

try:
    from wigglystuff import TangleSlider
except ImportError as e:
    raise ImportError(
        "This example requires wigglystuff. "
        "Please install it with: pip install wigglystuff"
    ) from e

pn.extension()

# Create the wigglystuff TangleSlider widget with reasonable defaults
tangle_widget = TangleSlider(
    min_value=0,
    max_value=100,
    amount=50,
    step=1,
    prefix="",
    suffix=""
)

# Wrap it with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(tangle_widget)

# Access the component immediately — no need to wait for render
component = anywidget_pane.component

# Create a Panel FloatSlider synced bidirectionally with the TangleSlider
panel_slider = pn.widgets.FloatSlider(
    name="Panel Slider (synced)",
    start=0,
    end=100,
    step=1,
    value=50
)

# Display current amount using pn.bind on the component's param
amount_display = pn.pane.Markdown(pn.bind(
    lambda amount: f"**Current amount:** {amount:.1f}",
    component.param.amount
))

# TangleSlider -> Panel: use param.watch on pane.component
component.param.watch(lambda e: setattr(panel_slider, 'value', e.new), ['amount'])

# Panel -> TangleSlider: watch slider changes (note: limited by TangleSlider ESM)
panel_slider.param.watch(lambda e: setattr(component, 'amount', e.new), ['value'])

# Layout
header = pn.pane.Markdown("""
# wigglystuff Example — Third-Party AnyWidget in Panel

This example renders **wigglystuff's TangleSlider** widget (a third-party anywidget)
natively in Panel using the `AnyWidget` pane. No `ipywidgets_bokeh` needed!
""")

explanation = pn.pane.Markdown("""
### How it works

**TangleSlider** is a Bret Victor-style draggable inline number. Click and drag on the number
to change its value.

### Sync Direction

| Direction | Works? | Why |
|-----------|--------|-----|
| TangleSlider -> Panel | Yes | `component.param.watch()` picks up traitlet changes |
| Panel -> TangleSlider | **No** | TangleSlider ESM has no `model.on("change:amount", ...)` handler |

This is a **TangleSlider library limitation**, not a Panel issue. The ESM reads `amount` once
at render time but never listens for external updates. The traitlet IS updated from Python,
but the browser-side display doesn't refresh.

**Try it:** Drag the TangleSlider — the Panel slider and amount display update.
Dragging the Panel slider updates the traitlet (shown in amount display) but not the TangleSlider visual.

**API used:** `pane.component.param.watch(...)` and `pn.bind(func, component.param.amount)` —
the component is created eagerly so `param.watch`, `pn.bind`, and `.rx` all work immediately.
""")

pn.Column(
    header,
    explanation,
    pn.pane.Markdown("### TangleSlider (rendered via AnyWidget pane)"),
    pn.Row(pn.Spacer(width=200), anywidget_pane),
    amount_display,
    pn.pane.Markdown("### Synced Panel Slider"),
    panel_slider,
).servable()
