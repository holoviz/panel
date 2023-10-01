import pytest

pytestmark = pytest.mark.ui

from panel.tests.util import serve_component, wait_until
from panel.widgets import Button


def test_button_click(page):
    button = Button(name='Click')

    events = []
    def cb(event):
        events.append(event)
    button.on_click(cb)

    serve_component(page, button)

    page.click('.bk-btn')

    wait_until(lambda: len(events) == 1, page)
