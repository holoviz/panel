"""
Anywidget Multiple Traitlets Example

Demonstrates an anywidget component with multiple traitlet types (Int, Unicode, Bool, List, Dict)
integrated with Panel's reactive binding. Each traitlet is synced bidirectionally with corresponding
Panel widgets (IntSlider, TextInput, Checkbox), and JSON display for complex types.

Run with: panel serve research/anywidget/examples/multi_trait.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


class MultiTraitWidget(anywidget.AnyWidget):
    """An anywidget demonstrating multiple traitlet types with bidirectional sync."""

    count = traitlets.Int(0).tag(sync=True)
    label = traitlets.Unicode("").tag(sync=True)
    enabled = traitlets.Bool(True).tag(sync=True)
    items = traitlets.List(default_value=[]).tag(sync=True)
    config = traitlets.Dict(default_value={}).tag(sync=True)

    _esm = """
    function render({ model, el }) {
      let container = document.createElement("div");
      container.style.padding = "20px";
      container.style.fontFamily = "sans-serif";
      container.style.backgroundColor = "#f5f5f5";
      container.style.borderRadius = "8px";

      function updateDisplay() {
        container.innerHTML = "";

        let title = document.createElement("h2");
        title.textContent = "Widget State";
        title.style.marginTop = "0";
        container.appendChild(title);

        let sections = [
          { name: "Count (Int)", value: model.get("count") },
          { name: "Label (Unicode)", value: model.get("label") || "(empty)" },
          { name: "Enabled (Bool)", value: model.get("enabled") ? "True" : "False" },
          { name: "Items (List)", value: JSON.stringify(model.get("items") || []) },
          { name: "Config (Dict)", value: JSON.stringify(model.get("config") || {}) }
        ];

        sections.forEach(function(section) {
          let sectionDiv = document.createElement("div");
          sectionDiv.style.marginBottom = "12px";
          sectionDiv.style.padding = "10px";
          sectionDiv.style.backgroundColor = "white";
          sectionDiv.style.borderRadius = "4px";
          sectionDiv.style.border = "1px solid #ddd";

          let label = document.createElement("strong");
          label.textContent = section.name + ": ";
          label.style.color = "#333";

          let value = document.createElement("span");
          value.textContent = String(section.value);
          value.style.color = "#666";
          value.style.fontFamily = "monospace";

          sectionDiv.appendChild(label);
          sectionDiv.appendChild(value);
          container.appendChild(sectionDiv);
        });
      }

      updateDisplay();

      model.on("change:count", updateDisplay);
      model.on("change:label", updateDisplay);
      model.on("change:enabled", updateDisplay);
      model.on("change:items", updateDisplay);
      model.on("change:config", updateDisplay);

      el.appendChild(container);
    }
    export default { render };
    """


# Create the anywidget instance and pane
widget = MultiTraitWidget()
pane = pn.pane.AnyWidget(widget)

# pane.component is available immediately — use param API
component = pane.component

# Create Panel widgets synced to the traitlets
count_slider = pn.widgets.IntSlider(name="Count", start=0, end=100, value=0)
label_input = pn.widgets.TextInput(name="Label", value="")
enabled_checkbox = pn.widgets.Checkbox(name="Enabled", value=True)

# Items (List) controls
items_input = pn.widgets.TextInput(name="Add item", placeholder="Type item", value="")
items_add_button = pn.widgets.Button(name="Add Item", button_type="success")
items_clear_button = pn.widgets.Button(name="Clear Items", button_type="warning")
items_display = pn.pane.Markdown(pn.bind(
    lambda items: f"**Items:** `{items}`", component.param.items
))

# Config (Dict) controls
config_key_input = pn.widgets.TextInput(name="Key", placeholder="Enter key", value="")
config_value_input = pn.widgets.TextInput(name="Value", placeholder="Enter value", value="")
config_add_button = pn.widgets.Button(name="Add to Config", button_type="success")
config_clear_button = pn.widgets.Button(name="Clear Config", button_type="warning")
config_display = pn.pane.Markdown(pn.bind(
    lambda config: f"**Config:** `{config}`", component.param.config
))

# Bidirectional sync via param API
component.param.watch(lambda e: setattr(count_slider, 'value', e.new), ['count'])
count_slider.param.watch(lambda e: setattr(component, 'count', e.new), ['value'])

component.param.watch(lambda e: setattr(label_input, 'value', e.new), ['label'])
label_input.param.watch(lambda e: setattr(component, 'label', e.new), ['value'])

component.param.watch(lambda e: setattr(enabled_checkbox, 'value', e.new), ['enabled'])
enabled_checkbox.param.watch(lambda e: setattr(component, 'enabled', e.new), ['value'])

# Items (List) control callbacks
def add_item(event):
    if items_input.value:
        component.items = list(component.items) + [items_input.value]
        items_input.value = ""

def clear_items(event):
    component.items = []

items_add_button.on_click(add_item)
items_clear_button.on_click(clear_items)

# Config (Dict) control callbacks
def add_config_item(event):
    if config_key_input.value and config_value_input.value:
        component.config = {**component.config, config_key_input.value: config_value_input.value}
        config_key_input.value = ""
        config_value_input.value = ""

def clear_config(event):
    component.config = {}

config_add_button.on_click(add_config_item)
config_clear_button.on_click(clear_config)

# Layout
header = pn.pane.Markdown("""
# Multi-Trait Example — AnyWidget Pane

This example demonstrates **all common traitlet types** synced between an
anywidget and Panel: `Int`, `Unicode`, `Bool`, `List`, and `Dict`.

The left panel is the **anywidget** (rendered via ESM) showing live state.
The right panel contains **Panel widgets** wired via `pane.component.param.watch()`.

**Try it:** Change any control on the right — the anywidget display updates.
The Items and Config values are read-only here but sync from the browser side.
""")

pn.Column(
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Anywidget (browser-side state display)"),
            pn.panel(pane, width=500),
        ),
        pn.Column(
            pn.pane.Markdown("### Panel Widgets (Python-side controls)"),
            count_slider,
            label_input,
            enabled_checkbox,
            pn.pane.Markdown("---"),
            pn.pane.Markdown("### Items (List)"),
            pn.Row(items_input, items_add_button),
            items_clear_button,
            items_display,
            pn.pane.Markdown("---"),
            pn.pane.Markdown("### Config (Dict)"),
            pn.Row(config_key_input, config_value_input),
            pn.Row(config_add_button, config_clear_button),
            config_display,
            width=300,
        ),
    ),
).servable()
