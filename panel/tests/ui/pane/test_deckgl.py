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

    if not page.evaluate("() => !!document.createElement('canvas').getContext('webgl2')"):
        pytest.skip('WebGL2 is not available in this browser')

    wait_until(lambda: _red_pixels(page).any(), page, timeout=15000)
    red = _red_pixels(page)
    # Each path turns a right angle; flattened coordinates draw only diagonals
    assert red.sum(axis=1).max() > 100
    assert red.sum(axis=0).max() > 150


def _basemap_center(page):
    return page.evaluate("""() => {
      const find = (views) => {
        for (const view of views) {
          if (view.deckGL) { return view }
          const child = find(view.child_views ?? [])
          if (child) { return child }
        }
      }
      const map = find(Object.values(Bokeh.index))._map
      const {lng, lat} = map.getCenter()
      return [lng, lat, map.getZoom()]
    }""")


def test_deckgl_basemap_follows_initial_view_state_update(page):
    def spec(longitude, latitude, zoom):
        return {
            'initialViewState': {'longitude': longitude, 'latitude': latitude, 'zoom': zoom},
            'mapStyle': 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            'layers': [{
                '@@type': 'ScatterplotLayer', 'data': [{'p': [longitude, latitude]}],
                'getPosition': '@@=p', 'getRadius': 1000
            }]
        }
    pane = pn.pane.DeckGL(spec(-100, 40, 3), height=400, width=600)

    serve_component(page, pane)

    wait_until(lambda: _basemap_center(page) == pytest.approx([-100, 40, 3]), page)

    pane.object = spec(-120, 37, 6)

    wait_until(lambda: _basemap_center(page) == pytest.approx([-120, 37, 6]), page)
