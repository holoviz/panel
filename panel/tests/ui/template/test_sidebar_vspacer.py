import pytest

try:
    from playwright.sync_api import expect
    pytestmark = [pytest.mark.ui, pytest.mark.internet]
except ImportError:
    pytestmark = [pytest.mark.skip('playwright not available')]

from panel.layout import Column, Spacer, VSpacer
from panel.template import (
    BootstrapTemplate, FastGridTemplate, FastListTemplate, ReactTemplate,
    VanillaTemplate,
)
from panel.tests.util import serve_component
from panel.widgets import Button

TEMPLATES = [
    BootstrapTemplate, FastGridTemplate, FastListTemplate, ReactTemplate,
    VanillaTemplate,
]


def _sidebar_scroll(page):
    return page.locator('#sidebar').evaluate(
        'el => ({scroll: el.scrollHeight, client: el.clientHeight})'
    )


def _assert_bottom_pinned(page):
    expect(page.locator('.bottom-btn')).to_be_visible()
    sidebar = page.locator('#sidebar').bounding_box()
    top = page.locator('.top-btn').bounding_box()
    bottom = page.locator('.bottom-btn').bounding_box()
    sidebar_bottom = sidebar['y'] + sidebar['height']
    bottom_edge = bottom['y'] + bottom['height']
    # A wrapping flex container would move the trailing item into a second column
    assert bottom['x'] == pytest.approx(top['x'], abs=1)
    assert bottom['y'] > top['y'] + top['height']
    assert bottom_edge <= sidebar_bottom
    assert sidebar_bottom - bottom_edge < 50
    assert bottom_edge <= page.viewport_size['height']
    metrics = _sidebar_scroll(page)
    assert metrics['scroll'] <= metrics['client']


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_vspacer_fills_height(page, template):
    top = Button(label='Top', css_classes=['top-btn'])
    bottom = Button(label='Bottom', css_classes=['bottom-btn'])
    tmpl = template()
    tmpl.sidebar.append(Column(top, VSpacer(), bottom, sizing_mode='stretch_height'))

    serve_component(page, tmpl)

    _assert_bottom_pinned(page)


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_vspacer_between_items(page, template):
    tmpl = template()
    tmpl.sidebar.extend([
        Button(label='Top', css_classes=['top-btn']),
        VSpacer(),
        Button(label='Bottom', css_classes=['bottom-btn']),
    ])

    serve_component(page, tmpl)

    _assert_bottom_pinned(page)


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_stretch_height_item_between_items(page, template):
    tmpl = template()
    tmpl.sidebar.extend([
        Button(label='Top', css_classes=['top-btn']),
        Column(Button(label='Middle', css_classes=['middle-btn']), sizing_mode='stretch_height'),
        Button(label='Bottom', css_classes=['bottom-btn']),
    ])

    serve_component(page, tmpl)

    _assert_bottom_pinned(page)
    top = page.locator('.top-btn').bounding_box()
    middle = page.locator('.middle-btn').bounding_box()
    assert middle['x'] == pytest.approx(top['x'], abs=1)
    assert middle['y'] > top['y']


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_scrolls_when_content_is_tall(page, template):
    tmpl = template()
    tmpl.sidebar.append(Column(
        Button(label='Top', css_classes=['top-btn']),
        VSpacer(),
        Button(label='Bottom', css_classes=['bottom-btn']),
        height=3000,
    ))

    serve_component(page, tmpl)

    expect(page.locator('.top-btn')).to_be_visible()
    metrics = page.locator('#sidebar').evaluate(
        'el => ({scroll: el.scrollHeight, client: el.clientHeight})'
    )
    assert metrics['scroll'] > metrics['client']
    page.locator('#sidebar').evaluate('el => { el.scrollTop = el.scrollHeight }')
    sidebar = page.locator('#sidebar').bounding_box()
    bottom = page.locator('.bottom-btn').bounding_box()
    assert bottom['y'] + bottom['height'] <= sidebar['y'] + sidebar['height']


def test_fast_list_template_sidebar_vspacer_collapse_and_expand(page):
    tmpl = FastListTemplate()
    tmpl.sidebar.append(Column(
        Button(label='Top'), VSpacer(), Button(label='Bottom', css_classes=['bottom-btn']),
        sizing_mode='stretch_height',
    ))

    serve_component(page, tmpl)

    sidebar = page.locator('#sidebar')
    expect(page.locator('.bottom-btn')).to_be_visible()
    page.locator('#sidebar-button').click()
    expect(sidebar).to_have_class('sidenav hidden')
    expect(sidebar).to_have_css('width', '0px')
    page.locator('#sidebar-button').click()
    expect(sidebar).not_to_have_class('sidenav hidden')
    expect(page.locator('.bottom-btn')).to_be_visible()
    sidebar_box = sidebar.bounding_box()
    bottom_box = page.locator('.bottom-btn').bounding_box()
    assert sidebar_box['y'] + sidebar_box['height'] - (bottom_box['y'] + bottom_box['height']) < 50


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_scrolls_when_items_are_tall(page, template):
    tmpl = template()
    tmpl.sidebar.extend([
        Button(label='Top', css_classes=['top-btn']),
        Spacer(height=3000),
        Button(label='Bottom', css_classes=['bottom-btn']),
    ])

    serve_component(page, tmpl)

    expect(page.locator('.top-btn')).to_be_visible()
    metrics = _sidebar_scroll(page)
    assert metrics['scroll'] > metrics['client']
    page.locator('#sidebar').evaluate('el => { el.scrollTop = el.scrollHeight }')
    sidebar = page.locator('#sidebar').bounding_box()
    top = page.locator('.top-btn').bounding_box()
    bottom = page.locator('.bottom-btn').bounding_box()
    assert bottom['x'] == pytest.approx(top['x'], abs=1)
    assert bottom['y'] >= sidebar['y']
    assert bottom['y'] + bottom['height'] <= sidebar['y'] + sidebar['height'] + 1
