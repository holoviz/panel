"""
AnyWidget Pane POC — Native anywidget rendering in Panel.

This demo proves that Panel can render any anywidget *natively* — no
ipywidgets_bokeh needed. The AnyWidget pane extracts an anywidget's ESM
source and traitlets, builds a dynamic AnyWidgetComponent, and renders it
through Panel's ReactiveESM pipeline with full bidirectional sync.

Run with: panel serve research/anywidget/examples/counter.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


# ---------------------------------------------------------------------------
# 1. Define an anywidget (this is a plain anywidget — NOT a Panel component)
# ---------------------------------------------------------------------------

class CounterWidget(anywidget.AnyWidget):
    """A standard anywidget counter button — pure ESM + traitlets."""

    _esm = """
    function render({ model, el }) {
        let btn = document.createElement("button");
        btn.style.fontSize = "20px";
        btn.style.padding = "10px 24px";
        btn.style.cursor = "pointer";
        btn.style.borderRadius = "6px";
        btn.style.border = "2px solid #2196F3";
        btn.style.backgroundColor = "#e3f2fd";
        btn.style.color = "#1565c0";
        btn.style.fontWeight = "bold";
        btn.innerHTML = `count is ${model.get("value")}`;
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });
        model.on("change:value", () => {
            btn.innerHTML = `count is ${model.get("value")}`;
        });
        el.appendChild(btn);
    }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)


# ---------------------------------------------------------------------------
# 2. Wrap it with the new AnyWidget pane — this is the POC magic
# ---------------------------------------------------------------------------

widget = CounterWidget(value=5)
pane = pn.pane.AnyWidget(widget)   # <-- renders natively, no ipywidgets_bokeh!


# ---------------------------------------------------------------------------
# 3. Wire up a Panel slider for bidirectional sync demo
# ---------------------------------------------------------------------------
# pane.component is available immediately — no need to wait for render.
# This enables standard param patterns: param.watch, pn.bind, .rx

slider = pn.widgets.IntSlider(
    name="Panel IntSlider (Python side)",
    start=0, end=100, value=5,
)

# Bidirectional sync using the *param* API on pane.component:
pane.component.param.watch(lambda e: setattr(slider, 'value', e.new), ['value'])
slider.param.watch(lambda e: setattr(pane.component, 'value', e.new), ['value'])


# ---------------------------------------------------------------------------
# 4. Layout — styled for a clear POC demo
# ---------------------------------------------------------------------------

ANYWIDGET_LOGO = "https://raw.githubusercontent.com/manzt/anywidget/main/docs/public/favicon.svg"
PANEL_LOGO = "https://panel.holoviz.org/_static/logo_horizontal_light_theme.png"

header = pn.pane.Markdown(
    """
# Panel AnyWidget Pane — POC Demo

**What's happening here?** The button below is a standard
[anywidget](https://anywidget.dev) rendered *natively* through Panel's
upcoming `AnyWidget` pane. No `ipywidgets_bokeh` — just Panel's ReactiveESM pipeline.
""",
    sizing_mode="stretch_width",
)

anywidget_section = pn.Column(
    pn.Row(
        pn.pane.SVG(ANYWIDGET_LOGO, height=35, margin=(0, 10, 0, 0)),
        pn.pane.Markdown("### Anywidget (browser-side ESM)"),
        align="center",
    ),
    pn.pane.Markdown(
        "Click the button to increment the counter from the **browser**:"
    ),
    pane,
)

panel_section = pn.Column(
    pn.Row(
        pn.pane.PNG(PANEL_LOGO, height=35, margin=(0, 10, 0, 0)),
        pn.pane.Markdown("### Panel Widget (Python-side)"),
        align="center",
    ),
    pn.pane.Markdown(
        "Drag the slider to change the value from **Python**:"
    ),
    slider,
)

instructions = pn.pane.Markdown(
    """
---
**Test bidirectional sync:**
1. Click the **button** — the slider updates.
2. Drag the **slider** — the button label updates.
3. Both directions prove native traitlet ↔ param sync works!

**API used:** `pane.component.param.watch(...)` — the component is created
eagerly so `param.watch`, `pn.bind`, and `.rx` all work immediately.
""",
    sizing_mode="stretch_width",
)

pn.Column(
    header,
    pn.Row(anywidget_section, pn.Spacer(width=40), panel_section),
    instructions,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
