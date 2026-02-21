"""
AnyWidget POC smoke-test script.

Run with:  panel serve examples/anywidget_poc_test.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()

# ---- Define a simple counter anywidget (inline ESM, no deps) ----

class CounterWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let btn = document.createElement("button");
        btn.style.fontSize = "20px";
        btn.style.padding = "10px 24px";
        btn.style.cursor = "pointer";
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


# ---- Create the anywidget and wrap it ----
widget = CounterWidget(value=5)
pane = pn.pane.AnyWidget(widget)

# ---- Bidirectional sync demo ----
slider = pn.widgets.IntSlider(name="Value (Python side)", start=0, end=100, value=5)

def sync_slider_to_widget(event):
    widget.value = event.new

def sync_widget_to_slider(*events):
    for event in events:
        if event.name == 'value':
            slider.value = event.new

slider.param.watch(sync_slider_to_widget, 'value')
if pane.component is not None:
    pane.component.param.watch(sync_widget_to_slider, ['value'])

# ---- Layout ----
pn.Column(
    "# AnyWidget POC",
    "Click the button or drag the slider to verify bidirectional sync.",
    pane,
    slider,
).servable()
