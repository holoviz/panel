"""
Playwright test for the theme toggle anywidget example.

Tests:
    1. Widget renders (toggle switch and content area appear)
    2. No unexpected console errors
    3. Browser -> Python sync (click toggle, dark mode changes in Python)
    4. Python -> Browser sync (change dark from Python, theme class updates)
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


# --- Widget definition (same as research/anywidget/examples/toggle_theme.py) ---

class ThemeToggleWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "theme-container";

        let switchContainer = document.createElement("div");
        switchContainer.className = "switch-container";

        let switchLabel = document.createElement("label");
        switchLabel.className = "switch";

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = model.get("dark") || false;

        let slider = document.createElement("span");
        slider.className = "slider";

        checkbox.addEventListener("change", () => {
            model.set("dark", checkbox.checked);
            model.save_changes();
            updateTheme();
        });

        switchLabel.appendChild(checkbox);
        switchLabel.appendChild(slider);
        switchContainer.appendChild(switchLabel);

        let switchText = document.createElement("span");
        switchText.className = "switch-text";
        switchText.textContent = "Dark Mode";
        switchContainer.appendChild(switchText);

        container.appendChild(switchContainer);

        let contentArea = document.createElement("div");
        contentArea.className = "content-area";
        contentArea.innerHTML = `
            <h2>Theme Content</h2>
            <p>Toggle the switch to switch themes.</p>
        `;
        container.appendChild(contentArea);

        function updateTheme() {
            let isDark = model.get("dark") || false;
            if (isDark) {
                container.classList.remove("theme-light");
                container.classList.add("theme-dark");
            } else {
                container.classList.remove("theme-dark");
                container.classList.add("theme-light");
            }
        }

        model.on("change:dark", () => {
            checkbox.checked = model.get("dark") || false;
            updateTheme();
        });

        updateTheme();
        el.appendChild(container);
    }
    export default { render };
    """

    _css = """
    .theme-container { padding: 20px; border-radius: 8px; transition: background-color 0.3s; }
    .theme-light { background-color: #f5f5f5; color: #333; }
    .theme-dark { background-color: #333; color: #f5f5f5; }
    .switch-container { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
    .switch { position: relative; display: inline-block; width: 50px; height: 28px; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
              background-color: #ccc; border-radius: 28px; transition: 0.4s; }
    .slider:before { position: absolute; content: ""; height: 22px; width: 22px;
                     left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: 0.4s; }
    input:checked + .slider { background-color: #2196F3; }
    input:checked + .slider:before { transform: translateX(22px); }
    .content-area { padding: 16px; border-radius: 6px; border: 2px solid currentColor; }
    """

    dark = traitlets.Bool(False).tag(sync=True)


def test_toggle_theme_renders(page):
    """Widget renders and shows light theme by default."""
    widget = ThemeToggleWidget(dark=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator(".theme-container")
    expect(container).to_be_visible()
    expect(container).to_have_class("theme-container theme-light")

    content = page.locator(".content-area h2")
    expect(content).to_contain_text("Theme Content")

    assert_no_console_errors(msgs)


def test_toggle_theme_click_toggles_dark(page):
    """Clicking the toggle switch enables dark mode (browser -> Python sync)."""
    widget = ThemeToggleWidget(dark=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator(".theme-container")
    expect(container).to_have_class("theme-container theme-light")

    # Click the slider (the visible part of the toggle switch)
    slider = page.locator(".slider")
    slider.click()

    # Wait for Python-side value to update
    wait_until(lambda: widget.dark is True, page)
    assert pane.component.dark is True

    # Verify the DOM has the dark class
    expect(container).to_have_class("theme-container theme-dark")

    assert_no_console_errors(msgs)


def test_toggle_theme_python_to_browser(page):
    """Changing dark from Python updates the theme class (Python -> browser sync)."""
    widget = ThemeToggleWidget(dark=False)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    container = page.locator(".theme-container")
    expect(container).to_have_class("theme-container theme-light")

    # Change from Python side
    pane.component.dark = True

    expect(container).to_have_class("theme-container theme-dark")
    assert widget.dark is True

    # Toggle back
    pane.component.dark = False
    expect(container).to_have_class("theme-container theme-light")

    assert_no_console_errors(msgs)
