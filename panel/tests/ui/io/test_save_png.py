from io import BytesIO

import pytest

pytest.importorskip("playwright")

from PIL import Image

from panel.pane import Markdown, Vega
from panel.tests.util import hv_available

pytestmark = pytest.mark.ui

VEGA = {
    'data': {'values': [{'x': 'A', 'y': 5}, {'x': 'B', 'y': 3}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'}, 'y': {'type': 'quantitative', 'field': 'y'}},
    'width': 200, 'height': 150,
    '$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
}


def _png(obj, **kwargs):
    buf = BytesIO()
    obj.save(buf, as_png=True, backend='playwright', **kwargs)
    buf.seek(0)
    return Image.open(buf)


def _has_ink(img):
    lo, _ = img.convert('L').getextrema()
    return lo < 200


def test_save_png_playwright_markdown():
    assert _has_ink(_png(Markdown('# Hello', width=200)))


def test_save_png_playwright_vega():
    assert _has_ink(_png(Vega(VEGA)))


@hv_available
def test_save_png_playwright_holoviews():
    import holoviews as hv

    from panel.pane import HoloViews
    assert _has_ink(_png(HoloViews(hv.Curve([1, 3, 2]), backend='bokeh', width=300, height=200)))
