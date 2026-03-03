"""
Playwright test for the multi_trait anywidget example.

Tests:
    1. Widget renders (displays initial state for all trait types)
    2. No unexpected console errors
    3. Python -> Browser sync (change Int, Unicode, Bool traits from Python)
    4. List and Dict traits sync from Python
"""
import anywidget
import pytest
import traitlets

import panel as pn

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# --- Widget definition (same as research/anywidget/examples/multi_trait.py) ---

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
      container.className = "multi-trait-container";
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
          { name: "Count (Int)", value: model.get("count"), cls: "trait-count" },
          { name: "Label (Unicode)", value: model.get("label") || "(empty)", cls: "trait-label" },
          { name: "Enabled (Bool)", value: model.get("enabled") ? "True" : "False", cls: "trait-enabled" },
          { name: "Items (List)", value: JSON.stringify(model.get("items") || []), cls: "trait-items" },
          { name: "Config (Dict)", value: JSON.stringify(model.get("config") || {}), cls: "trait-config" }
        ];

        sections.forEach(function(section) {
          let sectionDiv = document.createElement("div");
          sectionDiv.className = section.cls;
          sectionDiv.style.marginBottom = "12px";
          sectionDiv.style.padding = "10px";
          sectionDiv.style.backgroundColor = "white";
          sectionDiv.style.borderRadius = "4px";
          sectionDiv.style.border = "1px solid #ddd";

          let label = document.createElement("strong");
          label.textContent = section.name + ": ";

          let value = document.createElement("span");
          value.className = "trait-value";
          value.textContent = String(section.value);
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


def test_multi_trait_renders(page):
    """Widget renders and shows initial state for all traits."""
    widget = MultiTraitWidget(count=0, label="", enabled=True, items=[], config={})
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator("div.multi-trait-container")
    expect(container).to_be_visible()

    # Verify initial values displayed
    count_section = page.locator("div.trait-count .trait-value")
    expect(count_section).to_contain_text("0")

    label_section = page.locator("div.trait-label .trait-value")
    expect(label_section).to_contain_text("(empty)")

    enabled_section = page.locator("div.trait-enabled .trait-value")
    expect(enabled_section).to_contain_text("True")

    items_section = page.locator("div.trait-items .trait-value")
    expect(items_section).to_contain_text("[]")

    config_section = page.locator("div.trait-config .trait-value")
    expect(config_section).to_contain_text("{}")

    assert_no_console_errors(msgs)


def test_multi_trait_int_sync(page):
    """Changing count from Python updates the display (Python -> browser)."""
    widget = MultiTraitWidget(count=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    count_section = page.locator("div.trait-count .trait-value")
    expect(count_section).to_contain_text("0")

    pane.component.count = 42

    expect(count_section).to_contain_text("42")
    assert widget.count == 42

    assert_no_console_errors(msgs)


def test_multi_trait_unicode_sync(page):
    """Changing label from Python updates the display (Python -> browser)."""
    widget = MultiTraitWidget(label="")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    label_section = page.locator("div.trait-label .trait-value")
    expect(label_section).to_contain_text("(empty)")

    pane.component.label = "Hello World"

    expect(label_section).to_contain_text("Hello World")
    assert widget.label == "Hello World"

    assert_no_console_errors(msgs)


def test_multi_trait_bool_sync(page):
    """Changing enabled from Python updates the display (Python -> browser)."""
    widget = MultiTraitWidget(enabled=True)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    enabled_section = page.locator("div.trait-enabled .trait-value")
    expect(enabled_section).to_contain_text("True")

    pane.component.enabled = False

    expect(enabled_section).to_contain_text("False")
    assert widget.enabled is False

    assert_no_console_errors(msgs)


def test_multi_trait_list_sync(page):
    """Changing items from Python updates the display (Python -> browser)."""
    widget = MultiTraitWidget(items=[])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    items_section = page.locator("div.trait-items .trait-value")
    expect(items_section).to_contain_text("[]")

    pane.component.items = ["apple", "banana"]

    expect(items_section).to_contain_text('["apple","banana"]')
    assert widget.items == ["apple", "banana"]

    assert_no_console_errors(msgs)


def test_multi_trait_dict_sync(page):
    """Changing config from Python updates the display (Python -> browser)."""
    widget = MultiTraitWidget(config={})
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    config_section = page.locator("div.trait-config .trait-value")
    expect(config_section).to_contain_text("{}")

    pane.component.config = {"key": "value"}

    expect(config_section).to_contain_text('{"key":"value"}')
    assert widget.config == {"key": "value"}

    assert_no_console_errors(msgs)
