import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import Markdown
from panel.template import EditableTemplate
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_editable_template_no_console_errors(page):
    tmpl = EditableTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    msgs, _ = serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    assert [msg for msg in msgs if msg.type == 'error'] == []


def test_editable_template_order(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    items = page.locator(".muuri-grid-item")
    md1_bbox = items.nth(0).bounding_box()
    md2_bbox = items.nth(1).bounding_box()
    assert md2_bbox['y'] < md1_bbox['y']


def test_editable_template_reset_order(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    items = page.locator(".muuri-grid-item")
    md1_bbox = items.nth(0).bounding_box()
    md2_bbox = items.nth(1).bounding_box()
    assert md2_bbox['y'] < md1_bbox['y']

    page.locator('#grid-reset').click(force=True)

    wait_until(lambda: items.nth(1).bounding_box()['y'] > items.nth(0).bounding_box()['y'], page)
    wait_until(lambda: list(tmpl.layout) == [id(md1), id(md2)], page)


def test_editable_template_size(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    items = page.locator(".muuri-grid-item")
    md2_bbox = items.nth(1).bounding_box()
    assert md2_bbox['height'] == 60


def test_editable_template_reset_size(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    items = page.locator(".muuri-grid-item")
    md1_bbox = items.nth(0).bounding_box()
    md2_bbox = items.nth(1).bounding_box()
    assert md2_bbox['y'] < md1_bbox['y']

    page.locator('#grid-reset').click()

    wait_until(lambda: items.nth(1).bounding_box()['width'] > (md2_bbox['width'] * 2), page)
    wait_until(lambda: tmpl.layout[id(md2)]['width'] == 100, page)


def test_editable_template_visible(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50, 'visible': False}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_item = page.locator(".muuri-grid-item").nth(1)

    page.wait_for_timeout(200)

    expect(md2_item).to_have_class('muuri-grid-item muuri-item-hidden muuri-item')


def test_editable_template_reset_visible(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 50, 'visible': False}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_item = page.locator(".muuri-grid-item").nth(1)

    page.wait_for_timeout(200)

    expect(md2_item).to_have_class('muuri-grid-item muuri-item-hidden muuri-item')

    page.locator('#grid-reset').click()

    md2_item = page.locator(".muuri-grid-item").nth(1)
    expect(md2_item).to_have_class('muuri-grid-item muuri-item-shown muuri-item')
    wait_until(lambda: tmpl.layout[id(md2)]['visible'], page)


def test_editable_template_delete_item(page):
    tmpl = EditableTemplate()
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    page.wait_for_timeout(200)

    page.locator(".muuri-handle.delete").nth(1).click()

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('visible') == False, page)


def test_editable_template_undo_delete_item(page):
    tmpl = EditableTemplate()
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    page.locator(".muuri-handle.delete").nth(1).click()

    page.wait_for_timeout(200)

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('visible') == False, page)

    page.locator('#grid-undo').click()

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('visible') == True, page)


def test_editable_template_drag_item(page):
    tmpl = EditableTemplate()
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_handle = page.locator(".muuri-handle.drag").nth(1)

    page.wait_for_timeout(200)

    md2_handle.drag_to(md2_handle, target_position={'x': 0, 'y': -50}, force=True)

    wait_until(lambda: list(tmpl.layout) == [id(md2), id(md1)], page)

def test_editable_template_undo_drag_item(page):
    tmpl = EditableTemplate()
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_handle = page.locator(".muuri-handle.drag").nth(1)

    page.wait_for_timeout(200)

    md2_handle.drag_to(md2_handle, target_position={'x': 0, 'y': -50}, force=True)

    wait_until(lambda: list(tmpl.layout) == [id(md2), id(md1)], page)

    page.locator('#grid-undo').click()

    wait_until(lambda: list(tmpl.layout) == [id(md1), id(md2)], page)

def test_editable_template_resize_item(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 80}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_handle = page.locator(".muuri-handle.resize").nth(1)

    page.wait_for_timeout(200)

    md2_handle.hover()
    md2_handle.drag_to(md2_handle, target_position={'x': -50, 'y': -30}, force=True)

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('width') < 45, page)

def test_editable_template_undo_resize_item(page):
    md1 = Markdown('1')
    md2 = Markdown('2')

    tmpl = EditableTemplate(layout={id(md2): {'width': 50, 'height': 80}})

    tmpl.main[:] = [md1, md2]

    serve_component(page, tmpl)

    md2_handle = page.locator(".muuri-handle.resize").nth(1)

    page.wait_for_timeout(200)

    md2_handle.hover()
    md2_handle.drag_to(md2_handle, target_position={'x': -50, 'y': -30}, force=True)

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('width') < 45, page)

    page.locator('#grid-undo').click()

    wait_until(lambda: tmpl.layout.get(id(md2), {}).get('width') == 50, page)
