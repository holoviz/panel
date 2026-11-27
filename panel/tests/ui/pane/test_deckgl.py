import io
import json

import numpy as np
import pytest

pytest.importorskip("playwright")

from PIL import Image

import panel as pn

from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def _require_webgl2(page):
    # Linux CI runs headless Chromium without a GPU, where neither deck.gl
    # nor the MapLibre basemap can create a WebGL context.
    if not page.evaluate("() => !!document.createElement('canvas').getContext('webgl2')"):
        pytest.skip('WebGL2 is not available in this browser')


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
    _require_webgl2(page)

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
      const map = find(Object.values(Bokeh.index))?._map
      if (map == null) { return null }
      const {lng, lat} = map.getCenter()
      return [lng, lat, map.getZoom()]
    }""")


# Stands in for a deck.gl that has not initialized its WebGL device yet,
# which is when it first reports a view state change.
_NO_VIEW_STATE_CHANGE = """
const interval = setInterval(() => {
  const proto = window.deck?.DeckGL?.prototype
  if (proto == null) { return }
  clearInterval(interval)
  const handler = proto._onViewStateChange
  proto._onViewStateChange = function (params) {
    const props = this.props
    this.props = {...props, onViewStateChange: () => null}
    try { return handler.call(this, params) } finally { this.props = props }
  }
}, 0)
"""


_CARTO_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'


def _stub_basemap_style(page):
    # The tests only check the camera, so the CARTO style and its tiles are
    # not fetched; the URL still has to name CARTO for the pane to use MapLibre.
    page.route(_CARTO_STYLE, lambda route: route.fulfill(
        content_type='application/json',
        body=json.dumps({'version': 8, 'sources': {}, 'layers': []}),
    ))


def _basemap_spec(longitude, latitude, zoom):
    return {
        'initialViewState': {'longitude': longitude, 'latitude': latitude, 'zoom': zoom},
        'mapStyle': _CARTO_STYLE,
        'layers': [{
            '@@type': 'ScatterplotLayer', 'data': [{'p': [longitude, latitude]}],
            'getPosition': '@@=p', 'getRadius': 1000
        }]
    }


def test_deckgl_basemap_starts_at_initial_view_state(page):
    page.add_init_script(_NO_VIEW_STATE_CHANGE)
    _stub_basemap_style(page)
    pane = pn.pane.DeckGL(_basemap_spec(-100, 40, 3), height=400, width=600)

    serve_component(page, pane)
    _require_webgl2(page)

    wait_until(lambda: _basemap_center(page) == pytest.approx([-100, 40, 3]), page)


def test_deckgl_basemap_follows_initial_view_state_update(page):
    _stub_basemap_style(page)
    pane = pn.pane.DeckGL(_basemap_spec(-100, 40, 3), height=400, width=600)

    serve_component(page, pane)
    _require_webgl2(page)

    wait_until(lambda: _basemap_center(page) == pytest.approx([-100, 40, 3]), page)

    pane.object = _basemap_spec(-120, 37, 6)

    wait_until(lambda: _basemap_center(page) == pytest.approx([-120, 37, 6]), page)
