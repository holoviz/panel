import pytest

from panel import Row, Spacer
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

def test_row_scroll(page):
    row = Row(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, width=420
    )

    serve_component(page, row)

    row_el = page.locator(".bk-Row")
    bbox = row_el.bounding_box()

    assert bbox['width'] == 420
    assert bbox['height'] in (200, 215) # Ignore if browser hides empty scrollbar

    assert 'scrollable-horizontal' in row_el.get_attribute('class')
