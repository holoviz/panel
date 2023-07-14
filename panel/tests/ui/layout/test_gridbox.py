import time

import pytest

from panel import Column, GridBox, Spacer
from panel.io.server import serve

pytestmark = pytest.mark.ui

def test_gridbox(page, port):
    grid = GridBox(
        *(Spacer(width=50, height=50) for i in range(12)),
        ncols=4
    )

    serve(grid, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()

    assert bbox['width'] == 200
    assert bbox['height'] == 150

    grid.ncols = 6

    time.sleep(0.1)

    bbox = page.locator(".bk-GridBox").bounding_box()

    assert bbox['width'] == 300
    assert bbox['height'] == 100


def test_gridbox_unequal(page, port):
    grid = GridBox(
        Spacer(width=50, height=10),
        Spacer(width=40, height=10),
        Spacer(width=60, height=20),
        Spacer(width=20, height=10),
        Spacer(width=20, height=30),
        ncols=4
    )

    serve(grid, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 170
    assert bbox['height'] == 50
    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['width'] == 50
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 50
    assert bbox2['width'] == 40
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 90
    assert bbox3['width'] == 60
    bbox4 = children.nth(3).bounding_box()
    assert bbox4['x'] == 150
    assert bbox4['width'] == 20
    bbox5 = children.nth(4).bounding_box()
    assert bbox5['x'] == 0
    assert bbox5['y'] == 20
    assert bbox5['width'] == 20
    assert bbox5['height'] == 30

    grid.ncols = 5

    time.sleep(0.1)

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 190
    assert bbox['height'] == 30
    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['width'] == 50
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 50
    assert bbox2['width'] == 40
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 90
    assert bbox3['width'] == 60
    bbox4 = children.nth(3).bounding_box()
    assert bbox4['x'] == 150
    assert bbox4['width'] == 20
    bbox5 = children.nth(4).bounding_box()
    assert bbox5['x'] == 170
    assert bbox5['y'] == 0
    assert bbox5['width'] == 20
    assert bbox5['height'] == 30


def test_gridbox_stretch_width(page, port):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_width', height=50),
        Spacer(sizing_mode='stretch_width', height=50),
        Spacer(sizing_mode='stretch_width', height=50),
        ncols=2, sizing_mode='stretch_width'
    ), width=800)

    serve(grid, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 800
    assert bbox['height'] == 100

    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['width'] == 400
    assert bbox1['height'] == 50
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 400
    assert bbox2['width'] == 400
    assert bbox2['height'] == 50
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 0
    assert bbox3['width'] == 400
    assert bbox3['height'] == 50


def test_gridbox_stretch_height(page, port):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_height', width=50),
        Spacer(sizing_mode='stretch_height', width=50),
        Spacer(sizing_mode='stretch_height', width=50),
        ncols=2, sizing_mode='stretch_height'
    ), height=800)

    serve(grid, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 100
    assert bbox['height'] == 800

    bbox1 = children.nth(0).bounding_box()
    assert bbox1['y'] == 0
    assert bbox1['height'] == 400
    assert bbox1['width'] == 50
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 50
    assert bbox2['y'] == 0
    assert bbox2['height'] == 400
    assert bbox2['width'] == 50
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 0
    assert bbox3['y'] == 400
    assert bbox3['height'] == 400
    assert bbox3['width'] == 50

def test_gridbox_stretch_both(page, port):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_both'),
        Spacer(sizing_mode='stretch_both'),
        Spacer(sizing_mode='stretch_both'),
        ncols=2, sizing_mode='stretch_both'
    ), height=800, width=600)

    serve(grid, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    bbox = page.locator(".bk-GridBox").bounding_box()
    children = page.locator(".bk-GridBox div")

    assert bbox['width'] == 600
    assert bbox['height'] == 800

    bbox1 = children.nth(0).bounding_box()
    assert bbox1['x'] == 0
    assert bbox1['y'] == 0
    assert bbox1['height'] == 400
    assert bbox1['width'] == 300
    bbox2 = children.nth(1).bounding_box()
    assert bbox2['x'] == 300
    assert bbox2['y'] == 0
    assert bbox2['height'] == 400
    assert bbox2['width'] == 300
    bbox3 = children.nth(2).bounding_box()
    assert bbox3['x'] == 0
    assert bbox3['y'] == 400
    assert bbox3['height'] == 400
    assert bbox3['width'] == 300
