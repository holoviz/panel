import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

try:
    import textual

    from textual.app import App
    from textual.widgets import Button
except Exception:
    textual = None  # type: ignore
textual_available = pytest.mark.skipif(textual is None, reason="requires textual")

from panel.pane import Textual
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_textual_app(page):
    clicks = []

    def app():
        # Has to be run on the thread
        class ButtonApp(App):

            def compose(self):
                yield Button("Default")

            def on_button_pressed(self, event: Button.Pressed) -> None:
                clicks.append(event)

        app = ButtonApp()
        textual = Textual(app)
        return textual

    serve_component(page, app)

    expect(page.locator(".xterm-screen")).to_have_count(1)

    wait_until(lambda: bool(page.mouse.click(50, 50) or clicks), page)
