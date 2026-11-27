import io
import json

import numpy as np
import pytest

pytest.importorskip("playwright")

from PIL import Image
from playwright.sync_api import expect

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


_WEBGL_UNAVAILABLE = "This browser can't draw this map: WebGL is unavailable"

_SCATTER_SPEC = {
    'initialViewState': {'latitude': 46.03, 'longitude': 6.2, 'zoom': 11},
    'mapStyle': _CARTO_STYLE,
    'layers': [{
        '@@type': 'ScatterplotLayer', 'data': [{'p': [6.2, 46.03]}],
        'getPosition': '@@=p', 'getFillColor': [255, 0, 0], 'getRadius': 500
    }]
}


def _watch_errors(page):
    errors = []
    page.on('console', lambda msg: msg.type == 'error' and errors.append(msg.text))
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    return errors


def _assert_unavailable_message(page, errors):
    message = page.locator('.deckgl-unavailable')
    expect(message).to_have_text(_WEBGL_UNAVAILABLE)
    expect(message).to_have_attribute('role', 'status')
    assert page.locator('.deckgl canvas').count() == 0
    assert not errors


def test_deckgl_without_webgl_shows_message(browser_type, browser_type_launch_args):
    if browser_type.name != 'chromium':
        pytest.skip('Only Chromium can be launched with WebGL disabled')
    args = [*browser_type_launch_args.get('args', []), '--disable-webgl', '--disable-gpu']
    browser = browser_type.launch(**{**browser_type_launch_args, 'args': args})
    try:
        page = browser.new_page()
        _stub_basemap_style(page)
        errors = _watch_errors(page)
        pane = pn.pane.DeckGL(_SCATTER_SPEC, height=400, width=600)
        serve_component(page, pane)
        assert not page.evaluate("() => !!document.createElement('canvas').getContext('webgl2')")
        _assert_unavailable_message(page, errors)

        pane.object = dict(_SCATTER_SPEC, initialViewState={'latitude': 47, 'longitude': 7, 'zoom': 9})
        page.wait_for_timeout(500)
        _assert_unavailable_message(page, errors)
        assert page.locator('.deckgl-unavailable').count() == 1
    finally:
        browser.close()


# The pane's WebGL2 probe gets a context, every later request none, as on a
# browser whose GPU process refuses contexts after the first.
_BROKEN_WEBGL = """
const getContext = HTMLCanvasElement.prototype.getContext
HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
  if (String(kind).startsWith('webgl')) {
    return new Error().stack.includes('webgl2_available') ? {getExtension: () => null} : null
  }
  return getContext.call(this, kind, ...args)
}
"""

@pytest.mark.parametrize('map_style', [None, _CARTO_STYLE], ids=['no-basemap', 'carto'])
def test_deckgl_device_failure_shows_message(page, map_style):
    page.add_init_script(_BROKEN_WEBGL)
    _stub_basemap_style(page)
    errors = _watch_errors(page)
    pane = pn.pane.DeckGL(dict(_SCATTER_SPEC, mapStyle=map_style), height=400, width=600)
    serve_component(page, pane)
    _assert_unavailable_message(page, errors)

    pane.object = dict(pane.object, initialViewState={'latitude': 47, 'longitude': 7, 'zoom': 9})
    page.wait_for_timeout(500)
    _assert_unavailable_message(page, errors)


_COUNT_CONTEXTS = """
window._webglContexts = []
const getContext = HTMLCanvasElement.prototype.getContext
HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
  const context = getContext.call(this, kind, ...args)
  if (String(kind).startsWith('webgl') && context != null && !window._webglContexts.includes(context)) {
    window._webglContexts.push(context)
  }
  return context
}
"""

_LIVE_CONTEXTS = "() => window._webglContexts.filter((gl) => !gl.isContextLost()).length"


def test_deckgl_rerender_releases_webgl_contexts(page):
    page.add_init_script(_COUNT_CONTEXTS)
    _stub_basemap_style(page)
    pane = pn.pane.DeckGL(_SCATTER_SPEC, height=400, width=600)
    serve_component(page, pane)
    _require_webgl2(page)
    expect(page.locator('.deckgl canvas')).to_have_count(2)
    page.wait_for_timeout(500)
    live = page.evaluate(_LIVE_CONTEXTS)

    for i in range(20):
        # Each re-render creates a new deck.gl canvas and MapLibre basemap
        with page.expect_request_finished(lambda request: request.url == _CARTO_STYLE):
            pane.tooltips = {'text': f'{i}'}
    page.wait_for_timeout(500)
    expect(page.locator('.deckgl canvas')).to_have_count(2)
    assert page.evaluate("() => window._webglContexts.length") >= live + 40
    assert page.evaluate(_LIVE_CONTEXTS) <= live
