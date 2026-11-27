import numpy as np
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Column, Spacer
from panel.layout.gridstack import GridStack
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

# (x, y, width, height, background) of each child; None skips the check
LAYOUT = [
    (0, None, 200, 600, 'rgb(255, 0, 0)'),
    (200, 0, 400, 200, 'rgb(0, 128, 0)'),
    (400, 200, 400, 200, 'rgb(255, 165, 0)'),
    (200, 400, 600, 200, 'rgb(0, 0, 255)'),
    (600, 0, 200, 200, 'rgb(128, 0, 128)'),
]

ADDED = (200, 200, 200, 200, 'rgb(0, 0, 0)')


def _populate(gspec):
    gspec[:,   0  ] = Spacer(styles=dict(background='red'))
    gspec[0,   1:3] = Spacer(styles=dict(background='green'))
    gspec[1,   2:4] = Spacer(styles=dict(background='orange'))
    gspec[2,   1:4] = Spacer(styles=dict(background='blue'))
    gspec[0:1, 3:4] = Spacer(styles=dict(background='purple'))


def _assert_layout(page, layout):
    # GridStack positions its items after they render, so a single read
    # can catch them before they reach their cells.
    grid = page.locator(".grid-stack").bounding_box()
    assert grid is not None
    assert np.isclose(grid['width'], 800, atol=0.3)
    assert np.isclose(grid['height'], 600, atol=0.3)
    # Keyed by color since GridStack may reorder its items in the DOM
    boxes = dict(page.locator(".grid-stack > div > div > div").evaluate_all("""(els) => els.map((el) => {
        const r = el.getBoundingClientRect()
        return [getComputedStyle(el).backgroundColor, [r.x, r.y, r.width, r.height]]
    })"""))
    assert len(boxes) == len(layout)
    for x, y, width, height, background in layout:
        bx, by, bwidth, bheight = boxes[background]
        assert np.isclose(bx, x, atol=0.3)
        if y is not None:
            assert np.isclose(by, y, atol=0.3)
        assert np.isclose(bwidth, width, atol=0.3)
        assert np.isclose(bheight, height, atol=0.3)


def _check_gridstack(page, gspec):
    children = page.locator(".grid-stack > div > div > div")
    expect(children).to_have_count(5)
    wait_until(lambda: _assert_layout(page, LAYOUT), page)

    gspec[1, 1] = Spacer(styles=dict(background='black'))

    expect(children).to_have_count(6)
    wait_until(lambda: _assert_layout(page, [*LAYOUT, ADDED]), page)


def test_gridstack(page):
    gspec = GridStack(width=800, height=600, margin=0)
    _populate(gspec)

    serve_component(page, gspec)

    _check_gridstack(page, gspec)


def test_gridstack_stretch(page):
    gspec = GridStack(sizing_mode='stretch_both')
    column = Column(gspec, max_width=800, max_height=600)
    _populate(gspec)

    serve_component(page, column)

    _check_gridstack(page, gspec)
