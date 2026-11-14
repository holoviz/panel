import pytest

try:
    from playwright.sync_api import expect
    pytestmark = [pytest.mark.ui, pytest.mark.internet]
except ImportError:
    pytestmark = [pytest.mark.skip('playwright not available')]

from panel.layout import Column, VSpacer
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


@pytest.mark.parametrize('template', TEMPLATES)
def test_template_sidebar_vspacer_fills_height(page, template):
    top = Button(label='Top', css_classes=['top-btn'])
    bottom = Button(label='Bottom', css_classes=['bottom-btn'])
    tmpl = template()
    tmpl.sidebar.append(Column(top, VSpacer(), bottom, sizing_mode='stretch_height'))

    serve_component(page, tmpl)

    expect(page.locator('.bottom-btn')).to_be_visible()
    sidebar = page.locator('#sidebar').bounding_box()
    bottom_box = page.locator('.bottom-btn').bounding_box()
    sidebar_bottom = sidebar['y'] + sidebar['height']
    assert sidebar_bottom - (bottom_box['y'] + bottom_box['height']) < 50


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
