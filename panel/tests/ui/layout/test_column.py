import pytest

from panel import Column, Spacer
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

def test_column_scroll(page, port):
    col = Column(
        Spacer(styles=dict(background='red'), width=200, height=200),
        Spacer(styles=dict(background='green'), width=200, height=200),
        Spacer(styles=dict(background='blue'), width=200, height=200),
        scroll=True, height=420
    )

    serve_component(page, port, col)

    bbox = page.locator(".bk-Column").bounding_box()

    assert bbox['width'] in (200, 215) # Ignore if browser hides empty scrollbar
    assert bbox['height'] == 420
