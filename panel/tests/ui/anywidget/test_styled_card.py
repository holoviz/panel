"""
Playwright test for the styled_card anywidget example.

Tests:
    1. Widget renders (card appears with initial title and content)
    2. No unexpected console errors
    3. CSS styling is applied (card has correct class)
    4. Python -> Browser sync (change title/content from Python, card updates)
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


# --- Widget definition (same as research/anywidget/examples/styled_card.py) ---

class StyledCardWidget(anywidget.AnyWidget):
    """A card widget with CSS styling and customizable title and content."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "styled-card";

        let heading = document.createElement("h3");
        heading.textContent = model.get("title");

        let paragraph = document.createElement("p");
        paragraph.textContent = model.get("content");

        container.appendChild(heading);
        container.appendChild(paragraph);
        el.appendChild(container);

        model.on("change:title", () => {
            heading.textContent = model.get("title");
        });

        model.on("change:content", () => {
            paragraph.textContent = model.get("content");
        });
    }
    export default { render };
    """

    _css = """
    .styled-card {
        border: 2px solid #2196F3;
        border-radius: 8px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        max-width: 400px;
    }

    .styled-card h3 {
        margin: 0 0 12px 0;
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
    }

    .styled-card p {
        margin: 0;
        font-size: 16px;
        line-height: 1.5;
        color: rgba(255, 255, 255, 0.95);
    }
    """

    title = traitlets.Unicode("Hello Panel").tag(sync=True)
    content = traitlets.Unicode("AnyWidget + Panel").tag(sync=True)


def test_styled_card_renders(page):
    """Widget renders with initial title and content."""
    widget = StyledCardWidget(title="Hello Panel", content="AnyWidget + Panel")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    card = page.locator("div.styled-card")
    expect(card).to_be_visible()

    heading = card.locator("h3")
    expect(heading).to_contain_text("Hello Panel")

    paragraph = card.locator("p")
    expect(paragraph).to_contain_text("AnyWidget + Panel")

    assert_no_console_errors(msgs)


def test_styled_card_css_applied(page):
    """CSS styling is applied to the card."""
    widget = StyledCardWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    card = page.locator("div.styled-card")
    expect(card).to_be_visible()

    # Verify the card has some CSS styling applied (border-radius from CSS)
    border_radius = card.evaluate("el => getComputedStyle(el).borderRadius")
    assert border_radius == "8px"

    assert_no_console_errors(msgs)


def test_styled_card_python_to_browser_title(page):
    """Changing title from Python updates the card heading (Python -> browser)."""
    widget = StyledCardWidget(title="Initial Title", content="Initial Content")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    heading = page.locator("div.styled-card h3")
    expect(heading).to_contain_text("Initial Title")

    pane.component.title = "Updated Title"

    expect(heading).to_contain_text("Updated Title")
    assert widget.title == "Updated Title"

    assert_no_console_errors(msgs)


def test_styled_card_python_to_browser_content(page):
    """Changing content from Python updates the card paragraph (Python -> browser)."""
    widget = StyledCardWidget(title="Title", content="Original Content")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    paragraph = page.locator("div.styled-card p")
    expect(paragraph).to_contain_text("Original Content")

    pane.component.content = "New Content"

    expect(paragraph).to_contain_text("New Content")
    assert widget.content == "New Content"

    assert_no_console_errors(msgs)
