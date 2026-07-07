import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout import Overlay
from panel.pane import HTML
from panel.tests.util import serve_component, wait_until
from panel.widgets import Button

pytestmark = pytest.mark.ui

TOL = 3  # pixel tolerance for bounding-box comparisons


def _box(css_class, **kwargs):
    return HTML(
        f'<div style="width:100%;height:100%"></div>',
        css_classes=[css_class], width=40, height=20, margin=0, **kwargs
    )


def _container_box(page):
    # The Overlay's own root element -- the reference frame every
    # panel is anchored against.
    return page.locator('.overlay').bounding_box()


def test_overlay_named_anchor_positions(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(
        ('top-left', _box('tl')),
        ('top-center', _box('tc')),
        ('top-right', _box('tr')),
        ('center-left', _box('cl')),
        ('center', _box('cc')),
        ('center-right', _box('cr')),
        ('bottom-left', _box('bl')),
        ('bottom-center', _box('bc')),
        ('bottom-right', _box('br')),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    expect(page.locator('.overlay-panel')).to_have_count(9)

    container = _container_box(page)

    tl = page.locator('.tl').bounding_box()
    assert abs(tl['x'] - container['x']) < TOL
    assert abs(tl['y'] - container['y']) < TOL

    tr = page.locator('.tr').bounding_box()
    assert abs((tr['x'] + tr['width']) - (container['x'] + container['width'])) < TOL
    assert abs(tr['y'] - container['y']) < TOL

    bl = page.locator('.bl').bounding_box()
    assert abs(bl['x'] - container['x']) < TOL
    assert abs((bl['y'] + bl['height']) - (container['y'] + container['height'])) < TOL

    br = page.locator('.br').bounding_box()
    assert abs((br['x'] + br['width']) - (container['x'] + container['width'])) < TOL
    assert abs((br['y'] + br['height']) - (container['y'] + container['height'])) < TOL

    tc = page.locator('.tc').bounding_box()
    assert abs((tc['x'] + tc['width'] / 2) - (container['x'] + container['width'] / 2)) < TOL
    assert abs(tc['y'] - container['y']) < TOL

    bc = page.locator('.bc').bounding_box()
    assert abs((bc['x'] + bc['width'] / 2) - (container['x'] + container['width'] / 2)) < TOL
    assert abs((bc['y'] + bc['height']) - (container['y'] + container['height'])) < TOL

    cl = page.locator('.cl').bounding_box()
    assert abs(cl['x'] - container['x']) < TOL
    assert abs((cl['y'] + cl['height'] / 2) - (container['y'] + container['height'] / 2)) < TOL

    cr = page.locator('.cr').bounding_box()
    assert abs((cr['x'] + cr['width']) - (container['x'] + container['width'])) < TOL
    assert abs((cr['y'] + cr['height'] / 2) - (container['y'] + container['height'] / 2)) < TOL

    cc = page.locator('.cc').bounding_box()
    assert abs((cc['x'] + cc['width'] / 2) - (container['x'] + container['width'] / 2)) < TOL
    assert abs((cc['y'] + cc['height'] / 2) - (container['y'] + container['height'] / 2)) < TOL


def test_overlay_pixel_coordinate_position(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(
        ((24, 80), _box('coord')),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    container = _container_box(page)
    box = page.locator('.coord').bounding_box()

    assert abs(box['x'] - (container['x'] + 24)) < TOL
    assert abs(box['y'] - (container['y'] + 80)) < TOL


def test_overlay_percentage_coordinate_position(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(
        (("25%", "75%"), _box('pct')),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    container = _container_box(page)
    box = page.locator('.pct').bounding_box()

    assert abs(box['x'] - (container['x'] + container['width'] * 0.25)) < TOL
    assert abs(box['y'] - (container['y'] + container['height'] * 0.75)) < TOL


def test_overlay_panels_do_not_cover_base(page):
    # There is no full-size covering layer -- each panel is only as
    # big as its own footprint -- so the base stays interactive
    # everywhere else (see spec 7).
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(
        ('top-left', _box('tl')),
        ('bottom-right', _box('br')),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    container = _container_box(page)
    for cls in ('tl', 'br'):
        box = page.locator(f'.{cls}').bounding_box()
        assert box['width'] < container['width'] / 2
        assert box['height'] < container['height'] / 2


def test_overlay_base_receives_clicks_outside_panels(page):
    clicks = []
    base = Button(name='Base', sizing_mode='stretch_both')
    base.on_click(lambda e: clicks.append(e))

    overlay = Overlay(
        ('top-left', _box('tl')),
        ('bottom-right', _box('br')),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    container = _container_box(page)
    # Dead center of a 400x300 box is well clear of both 40x20 corner panels.
    page.mouse.click(container['x'] + container['width'] / 2, container['y'] + container['height'] / 2)

    wait_until(lambda: len(clicks) == 1, page)


def test_overlay_margin_insets_panel_from_anchor(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(
        ('top-left', _box('inset', margin=30)),
        base=base, width=400, height=300,
    )
    serve_component(page, overlay)

    container = _container_box(page)
    box = page.locator('.inset').bounding_box()

    # Roughly inset by the margin -- generous tolerance since the
    # exact box-model arithmetic (collapsing, wrapper sizing) isn't
    # being pinned down here, only that margin clearly pushes the
    # panel content away from the flush corner.
    assert 10 < (box['x'] - container['x']) < 50
    assert 10 < (box['y'] - container['y']) < 50


def test_overlay_no_objects_renders_base_only(page):
    base = HTML('<div class="base-only" style="width:100%;height:100%"></div>')
    overlay = Overlay(base=base, width=400, height=300)
    serve_component(page, overlay)

    expect(page.locator('.overlay-panel')).to_have_count(0)
    expect(page.locator('.base-only')).to_have_count(1)


def test_overlay_reactive_anchor_change(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    panel = _box('moving')
    overlay = Overlay(('top-left', panel), base=base, width=400, height=300)
    serve_component(page, overlay)

    container = _container_box(page)
    overlay[0] = ('bottom-right', panel)

    def _moved():
        box = page.locator('.moving').bounding_box()
        return abs((box['x'] + box['width']) - (container['x'] + container['width'])) < TOL

    wait_until(_moved, page)


def test_overlay_reactive_base_swap(page):
    base1 = HTML('<div class="base1" style="width:100%;height:100%"></div>')
    base2 = HTML('<div class="base2" style="width:100%;height:100%"></div>')
    overlay = Overlay(base=base1, width=400, height=300)
    serve_component(page, overlay)

    expect(page.locator('.base1')).to_have_count(1)
    expect(page.locator('.base2')).to_have_count(0)

    overlay.base = base2

    wait_until(lambda: page.locator('.base2').count() == 1, page)
    expect(page.locator('.base1')).to_have_count(0)


def test_overlay_reactive_append(page):
    base = HTML('<div style="width:100%;height:100%"></div>')
    overlay = Overlay(('top-left', _box('tl')), base=base, width=400, height=300)
    serve_component(page, overlay)

    expect(page.locator('.overlay-panel')).to_have_count(1)

    overlay.append(('bottom-right', _box('br')))

    wait_until(lambda: page.locator('.overlay-panel').count() == 2, page)
