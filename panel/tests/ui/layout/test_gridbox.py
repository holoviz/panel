import pytest

from panel import Column, GridBox, Spacer
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

def test_gridbox(page):
    grid = GridBox(
        *(Spacer(width=50, height=50) for i in range(12)),
        ncols=4
    )

    serve_component(page, grid)

    wait_until(lambda: page.locator(".bk-GridBox").bounding_box() == {'width': 200, 'height': 150, 'x': 0, 'y': 0}, page)

    grid.ncols = 6

    wait_until(lambda: page.locator(".bk-GridBox").bounding_box() == {'width': 300, 'height': 100, 'x': 0, 'y': 0}, page)


def test_gridbox_unequal(page):
    grid = GridBox(
        Spacer(width=50, height=10),
        Spacer(width=40, height=10),
        Spacer(width=60, height=20),
        Spacer(width=20, height=10),
        Spacer(width=20, height=30),
        ncols=4
    )

    serve_component(page, grid)

    wait_until(lambda: page.locator(".bk-GridBox").bounding_box() == {'width': 170, 'height': 50, 'x': 0, 'y': 0}, page)

    children = page.locator(".bk-GridBox div")
    wait_until(lambda: children.nth(0).bounding_box() == {'x': 0, 'y': 0, 'width': 50, 'height': 10}, page)
    wait_until(lambda: children.nth(1).bounding_box() == {'x': 50, 'y': 0, 'width': 40, 'height': 10}, page)
    wait_until(lambda: children.nth(2).bounding_box() == {'x': 90, 'y': 0, 'width': 60, 'height': 20}, page)
    wait_until(lambda: children.nth(3).bounding_box() == {'x': 150, 'y': 0, 'width': 20, 'height': 10}, page)
    wait_until(lambda: children.nth(4).bounding_box() == {'x': 0, 'y': 20, 'width': 20, 'height': 30}, page)

    grid.ncols = 5

    wait_until(lambda: page.locator(".bk-GridBox").bounding_box() == {'width': 190, 'height': 30, 'x': 0, 'y': 0}, page)
    wait_until(lambda: children.nth(0).bounding_box() == {'x': 0, 'y': 0, 'width': 50, 'height': 10}, page)
    wait_until(lambda: children.nth(1).bounding_box() == {'x': 50, 'y': 0, 'width': 40, 'height': 10}, page)
    wait_until(lambda: children.nth(2).bounding_box() == {'x': 90, 'y': 0, 'width': 60, 'height': 20}, page)
    wait_until(lambda: children.nth(3).bounding_box() == {'x': 150, 'y': 0, 'width': 20, 'height': 10}, page)
    wait_until(lambda: children.nth(4).bounding_box() == {'x': 170, 'y': 0, 'width': 20, 'height': 30}, page)


def test_gridbox_stretch_width(page):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_width', height=50),
        Spacer(sizing_mode='stretch_width', height=50),
        Spacer(sizing_mode='stretch_width', height=50),
        ncols=2, sizing_mode='stretch_width'
    ), width=800)

    serve_component(page, grid)

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


def test_gridbox_stretch_height(page):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_height', width=50),
        Spacer(sizing_mode='stretch_height', width=50),
        Spacer(sizing_mode='stretch_height', width=50),
        ncols=2, sizing_mode='stretch_height'
    ), height=800)

    serve_component(page, grid)

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

def test_gridbox_stretch_both(page):
    grid = Column(GridBox(
        Spacer(sizing_mode='stretch_both'),
        Spacer(sizing_mode='stretch_both'),
        Spacer(sizing_mode='stretch_both'),
        ncols=2, sizing_mode='stretch_both'
    ), height=800, width=600)

    serve_component(page, grid)

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
