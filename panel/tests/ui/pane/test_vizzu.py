import pytest

pytest.importorskip("playwright")

import numpy as np

from playwright.sync_api import expect

from panel.models.vizzu import VIZZU_VERSION
from panel.pane import Vizzu
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

DATA = {
    'Name': ['Alice', 'Bob', 'Ted', 'Patrick', 'Jason', 'Teresa', 'John'],
    'Weight': 50+np.random.randint(0, 10, 7)*10
}

CONFIG = {'geometry': 'rectangle', 'x': 'Name', 'y': 'Weight', 'title': 'Weight by person'}

def test_vizzu_no_console_errors(page):
    vizzu = Vizzu(
        DATA, config=CONFIG, duration=400, height=400, sizing_mode='stretch_width', tooltip=True
    )

    msgs, _ = serve_component(page, vizzu)

    expect(page.locator('canvas')).to_have_count(1)

    bbox = page.locator('canvas').bounding_box()

    assert bbox['width'] > 0
    assert bbox['height'] == 400
    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_vizzu_click(page):
    vizzu = Vizzu(
        DATA, config=CONFIG, duration=400, height=400, sizing_mode='stretch_width', tooltip=True
    )

    clicks = []

    vizzu.on_click(clicks.append)

    msgs, _ = serve_component(page, vizzu)

    expect(page.locator('canvas')).to_have_count(1)

    bbox = page.locator('canvas').bounding_box()

    page.mouse.click(bbox['width']//2, bbox['height']-100)

    wait_until(lambda: len(clicks) == 1, page)

    assert clicks[0]['categories'] == {'Name': 'Patrick'}

def test_can_import_version():
    assert VIZZU_VERSION
