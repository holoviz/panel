import pytest

from panel import FloatPanel, Row, Spacer
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

def test_float_panel_closed_status(page):
    float_panel = FloatPanel(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
    )

    serve_component(page, float_panel)

    page.locator('.jsPanel-btn-close').click()

    wait_until(lambda: float_panel.status == 'closed', page)

def test_float_panel_status_set_on_init(page):
    float_panel = FloatPanel(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        status='minimized'
    )

    serve_component(page, float_panel)

    float_container = page.locator('#jsPanel-replacement-container')
    wait_until(lambda: (
        float_container.bounding_box()['y'] + float_container.bounding_box()['height']
    ) == page.viewport_size['height'], page)

def test_float_panel_resize(page):
    float_panel = FloatPanel(
        Row(
            Spacer(styles=dict(background='red'), css_classes=['red'], height=200, sizing_mode='stretch_width'),
            Spacer(styles=dict(background='green'), css_classes=['green'], height=200, sizing_mode='stretch_width'),
            Spacer(styles=dict(background='blue'), css_classes=['blue'], height=200, sizing_mode='stretch_width'),
        )
    )

    serve_component(page, float_panel)

    resize_handle = page.locator('.jsPanel-resizeit-se')

    resize_handle.drag_to(resize_handle, target_position={'x': 510, 'y': 300}, force=True)

    wait_until(lambda: int(page.locator('.red').bounding_box()['width']) == 200, page)
    wait_until(lambda: int(page.locator('.green').bounding_box()['width']) == 200, page)
    wait_until(lambda: int(page.locator('.blue').bounding_box()['width']) == 200, page)


@pytest.mark.parametrize('contained', [True, False])
def test_float_panel_auto_size_fits_content(page, contained):
    float_panel = FloatPanel(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        contained=contained,
        )

    serve_component(page, float_panel)

    content = page.locator('.jsPanel-content')

    wait_until(lambda: content.bounding_box()['height'] >= 600, page)
    wait_until(lambda: content.bounding_box()['width'] >= 200, page)

    if not contained:
        normal = content.bounding_box()['height']
        float_panel.status = 'maximized'
        wait_until(lambda: content.bounding_box()['height'] != normal, page)
        float_panel.status = 'normalized'
        wait_until(lambda: content.bounding_box()['height'] == normal, page)


def test_float_panel_stretch_both_fills_content(page):
    float_panel = FloatPanel(
        Spacer(styles=dict(background='red'), css_classes=['stretch'], sizing_mode='stretch_both'),
        width=400, height=300, contained=False,
    )

    serve_component(page, float_panel)

    content = page.locator('.jsPanel-content')
    child = page.locator('.stretch')
    wait_until(lambda: content.bounding_box()['height'] > 200, page)
    wait_until(lambda: child.bounding_box()['height'] >= content.bounding_box()['height'] - 20, page)
    assert child.bounding_box()['width'] >= content.bounding_box()['width'] - 40


@pytest.mark.parametrize('panel_size', ['400 300', {'width': 400, 'height': 300}])
def test_float_panel_config_panel_size_respected(page, panel_size):
    float_panel = FloatPanel(
        'short', contained=False, config={'panelSize': panel_size},
    )

    serve_component(page, float_panel)

    panel = page.locator('.jsPanel')
    wait_until(lambda: int(panel.bounding_box()['height']) == 300, page)
    assert int(panel.bounding_box()['width']) == 400


def test_float_panel_plain_sizes_to_content(page):
    float_panel = FloatPanel('short', contained=False)

    serve_component(page, float_panel)

    panel = page.locator('.jsPanel')
    wait_until(lambda: panel.bounding_box()['height'] < 150, page)
