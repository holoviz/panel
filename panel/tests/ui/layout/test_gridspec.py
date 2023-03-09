import time

import pytest

from panel import Column, GridSpec, Spacer
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_gridspec(page, port):
    gspec = GridSpec(width=800, height=600, margin=0)

    gspec[:,   0  ] = Spacer(styles=dict(background='red'))
    gspec[0,   1:3] = Spacer(styles=dict(background='green'))
    gspec[1,   2:4] = Spacer(styles=dict(background='orange'))
    gspec[2,   1:4] = Spacer(styles=dict(background='blue'))
    gspec[0:1, 3:4] = Spacer(styles=dict(background='purple'))

    serve(gspec, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 800
    assert bbox['height'] == 600
    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['width'] == 200
    assert bbox1['height'] == 600
    assert children.nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 0, 0)'
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 200
    assert bbox2['y'] == 0
    assert bbox2['width'] == 400
    assert bbox2['height'] == 200
    assert children.nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 128, 0)'
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 400
    assert bbox3['y'] == 200
    assert bbox3['width'] == 400
    assert bbox3['height'] == 200
    assert children.nth(2).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 165, 0)'
    bbox4 = children.nth(3).bounding_box()
    assert bbox4['x'] == 200
    assert bbox4['y'] == 400
    assert bbox4['width'] == 600
    assert bbox4['height'] == 200
    assert children.nth(3).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 0, 255)'
    bbox5 = children.nth(4).bounding_box()
    assert bbox5['x'] == 600
    assert bbox5['y'] == 0
    assert bbox5['width'] == 200
    assert bbox5['height'] == 200
    assert children.nth(4).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(128, 0, 128)'

    gspec[1, 1] = Spacer(styles=dict(background='black'))

    time.sleep(0.2)

    children = page.locator(".bk-GridBox > div")
    bbox6 = children.nth(5).bounding_box()
    assert children.nth(5).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 0, 0)'
    assert bbox6['x'] == 200
    assert bbox6['y'] == 200
    assert bbox6['width'] == 200
    assert bbox6['height'] == 200


def test_gridspec_stretch(page, port):
    gspec = GridSpec(sizing_mode='stretch_both')
    col = Column(gspec, width=800, height=600)

    gspec[:,   0  ] = Spacer(styles=dict(background='red'))
    gspec[0,   1:3] = Spacer(styles=dict(background='green'))
    gspec[1,   2:4] = Spacer(styles=dict(background='orange'))
    gspec[2,   1:4] = Spacer(styles=dict(background='blue'))
    gspec[0:1, 3:4] = Spacer(styles=dict(background='purple'))

    serve(col, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox > div")

    assert bbox['width'] == 800
    assert bbox['height'] == 600
    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['width'] == 200
    assert bbox1['height'] == 600
    assert children.nth(0).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 0, 0)'
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 200
    assert bbox2['y'] == 0
    assert bbox2['width'] == 400
    assert bbox2['height'] == 200
    assert children.nth(1).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 128, 0)'
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 400
    assert bbox3['y'] == 200
    assert bbox3['width'] == 400
    assert bbox3['height'] == 200
    assert children.nth(2).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(255, 165, 0)'
    bbox4 = children.nth(3).bounding_box()
    assert bbox4['x'] == 200
    assert bbox4['y'] == 400
    assert bbox4['width'] == 600
    assert bbox4['height'] == 200
    assert children.nth(3).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 0, 255)'
    bbox5 = children.nth(4).bounding_box()
    assert bbox5['x'] == 600
    assert bbox5['y'] == 0
    assert bbox5['width'] == 200
    assert bbox5['height'] == 200
    assert children.nth(4).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(128, 0, 128)'

    gspec[1, 1] = Spacer(styles=dict(background='black'))

    time.sleep(0.25)

    children = page.locator(".bk-GridBox > div")
    bbox6 = children.nth(5).bounding_box()
    assert children.nth(5).evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 0, 0)'
    assert bbox6['x'] == 200
    assert bbox6['y'] == 200
    assert bbox6['width'] == 200
    assert bbox6['height'] == 200
