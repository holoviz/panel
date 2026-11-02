from io import BytesIO

import pytest

pytest.importorskip("playwright")

from PIL import Image

from panel.pane import (
    HoloViews, Markdown, Perspective, Vega,
)
from panel.tests.util import hv_available

pytestmark = pytest.mark.ui

VEGA = {
    'data': {'values': [{'x': 'A', 'y': 5}, {'x': 'B', 'y': 3}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'}, 'y': {'type': 'quantitative', 'field': 'y'}},
    'width': 200, 'height': 150,
    '$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
}


def _png(obj):
    buf = BytesIO()
    obj.save(buf, as_png=True, backend='playwright')
    buf.seek(0)
    return Image.open(buf)


def _has_ink(img):
    lo, _ = img.convert('L').getextrema()
    return lo < 200


def test_save_png_playwright_markdown():
    """Markdown exported blank when Panel's wait script did not reach Bokeh 3.10's backends."""
    assert _has_ink(_png(Markdown('# Hello', width=200)))


def test_save_png_playwright_perspective():
    """Perspective renders asynchronously, so the export has to wait for the document to go idle."""
    assert _has_ink(_png(Perspective({'a': [1, 2, 3], 'b': [4, 5, 6]}, width=400, height=200)))


def test_save_png_playwright_vega():
    """A pane whose JS loads from an extension bundle renders before the screenshot."""
    assert _has_ink(_png(Vega(VEGA)))


@hv_available
def test_save_png_playwright_holoviews():
    """A plain Bokeh plot exports through Panel without Selenium."""
    import holoviews as hv

    assert _has_ink(_png(HoloViews(hv.Curve([1, 3, 2]), backend='bokeh', width=300, height=200)))
