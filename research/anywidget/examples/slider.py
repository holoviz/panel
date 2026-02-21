"""
Anywidget HTML Range Slider Example

Demonstrates an anywidget component with an HTML range slider (<input type="range">)
integrated with Panel's reactive binding. The slider value is displayed in real-time
using a synced Panel IntSlider and a Markdown pane.

Run with: panel serve research/anywidget/examples/slider.py
"""

import anywidget
import traitlets

import panel as pn

pn.extension()


class SliderWidget(anywidget.AnyWidget):
    """A simple HTML range slider widget using anywidget."""

    value = traitlets.Int(50).tag(sync=True)

    _esm = """
    function render({ model, el }) {
      let container = document.createElement("div");
      container.style.padding = "20px";
      container.style.fontFamily = "sans-serif";

      let label = document.createElement("label");
      label.style.display = "block";
      label.style.marginBottom = "10px";
      label.style.fontSize = "16px";

      let slider = document.createElement("input");
      slider.type = "range";
      slider.min = "0";
      slider.max = "100";
      slider.value = model.get("value");
      slider.style.width = "300px";
      slider.style.cursor = "pointer";

      let valueDisplay = document.createElement("span");
      valueDisplay.style.marginLeft = "10px";
      valueDisplay.style.fontWeight = "bold";
      valueDisplay.style.color = "#1f77b4";
      valueDisplay.textContent = slider.value;

      label.textContent = "Select a value: ";
      label.appendChild(valueDisplay);

      container.appendChild(label);
      container.appendChild(slider);

      slider.addEventListener("input", (event) => {
        let newValue = parseInt(event.target.value);
        valueDisplay.textContent = newValue;
        model.set("value", newValue);
        model.save_changes();
      });

      model.on("change:value", () => {
        let newValue = model.get("value");
        slider.value = newValue;
        valueDisplay.textContent = newValue;
      });

      el.appendChild(container);
    }
    export default { render };
    """


# Create slider widget instance and pane
slider_widget = SliderWidget()
pane = pn.pane.AnyWidget(slider_widget)

# pane.component is available immediately — use param API directly
component = pane.component

# Create Panel IntSlider synced bidirectionally with the anywidget
panel_slider = pn.widgets.IntSlider(
    name="Panel IntSlider (Python side)",
    start=0,
    end=100,
    step=1,
    value=slider_widget.value,
)

# Reactive markdown display using pn.bind on the component param
value_display = pn.pane.Markdown(pn.bind(
    lambda v: f"**Current value:** {v}", component.param.value
))

# Bidirectional sync via param API (no widget.observe needed!)
component.param.watch(lambda e: setattr(panel_slider, 'value', e.new), ['value'])
panel_slider.param.watch(lambda e: setattr(component, 'value', e.new), ['value'])

# Layout
header = pn.pane.Markdown("""
# Slider Example — AnyWidget Pane

This example renders an **HTML `<input type="range">`** as an anywidget,
wrapped by Panel's `AnyWidget` pane.  A **Panel IntSlider** and a
**Markdown pane** stay in sync via bidirectional observation.

**Try it:**
1. **Drag the anywidget slider** (top) — the Panel slider and value display update.
2. **Drag the Panel slider** (bottom) — the anywidget slider updates.

**API used:** `pane.component.param.watch(...)` and `pn.bind(func, component.param.value)` —
the component is created eagerly so `param.watch`, `pn.bind`, and `.rx` all work immediately.
""")

pn.Column(
    header,
    pn.pane.Markdown("### Anywidget (browser-side range slider)"),
    pane,
    pn.pane.Markdown("### Panel Widgets (Python-side controls)"),
    panel_slider,
    value_display,
).servable()
