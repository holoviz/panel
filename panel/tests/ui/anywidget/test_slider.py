"""
Playwright test for the slider anywidget example.

Tests:
    1. Widget renders (slider appears with initial value)
    2. No unexpected console errors
    3. Browser -> Python sync (drag slider, value updates in Python)
    4. Python -> Browser sync (change value from Python, display updates)
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


# --- Widget definition (same as research/anywidget/examples/slider.py) ---

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
      slider.className = "aw-slider";

      let valueDisplay = document.createElement("span");
      valueDisplay.className = "aw-value-display";
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


def test_slider_renders(page):
    """Widget renders and shows the initial value."""
    widget = SliderWidget(value=50)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    slider = page.locator("input.aw-slider")
    expect(slider).to_be_visible()

    value_display = page.locator("span.aw-value-display")
    expect(value_display).to_contain_text("50")

    assert_no_console_errors(msgs)


def test_slider_browser_to_python(page):
    """Moving the slider updates the Python-side value (browser -> Python sync)."""
    widget = SliderWidget(value=50)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    slider = page.locator("input.aw-slider")

    # Use fill to set the slider value (Playwright supports this on range inputs)
    slider.fill("75")

    # Wait for Python-side value to update
    wait_until(lambda: widget.value == 75, page)
    assert pane.component.value == 75

    value_display = page.locator("span.aw-value-display")
    expect(value_display).to_contain_text("75")

    assert_no_console_errors(msgs)


def test_slider_python_to_browser(page):
    """Changing value from Python updates the slider and display (Python -> browser)."""
    widget = SliderWidget(value=50)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    value_display = page.locator("span.aw-value-display")
    expect(value_display).to_contain_text("50")

    # Change from Python side via the component
    pane.component.value = 25

    expect(value_display).to_contain_text("25")
    assert widget.value == 25

    # Verify the slider input value updated too
    slider = page.locator("input.aw-slider")
    expect(slider).to_have_value("25")

    assert_no_console_errors(msgs)
