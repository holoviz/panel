import io

import numpy as np
import pytest

pytest.importorskip("playwright")

from PIL import Image

import panel as pn

from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def _red_pixels(page):
    png = page.locator('.deckgl').screenshot()
    img = np.array(Image.open(io.BytesIO(png)).convert('RGB')).astype(int)
    return (img[..., 0] > 200) & (img[..., 1] < 60) & (img[..., 2] < 60)


def test_deckgl_path_layer_equal_length_paths_issue_3953(page):
    records = [
        {'coordinates': [[6.0 + 0.1 * i, 46.0], [6.0 + 0.1 * i, 46.05], [6.05 + 0.1 * i, 46.05]]}
        for i in range(4)
    ]
    spec = {
        'initialViewState': {'latitude': 46.03, 'longitude': 6.2, 'zoom': 11},
        'mapStyle': None,
        'layers': [{
            '@@type': 'PathLayer', 'data': records, 'getPath': '@@=coordinates',
            'getColor': [255, 0, 0], 'getWidth': 20, 'widthMinPixels': 4
        }]
    }
    pane = pn.pane.DeckGL(spec, height=500, width=800)

    serve_component(page, pane)

    wait_until(lambda: _red_pixels(page).any(), page)
    red = _red_pixels(page)
    # Each path turns a right angle; flattened coordinates draw only diagonals
    assert red.sum(axis=1).max() > 100
    assert red.sum(axis=0).max() > 150
