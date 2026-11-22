import pytest

pytest.importorskip("playwright")

try:
    import altair as alt
except Exception:
    alt = None  # type: ignore

altair_available = pytest.mark.skipif(alt is None, reason='Requires altair')

import pandas as pd

from playwright.sync_api import expect

from panel.layout import Column
from panel.pane import Vega
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

vega_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': [{'x': 'A', 'y': 5},
                        {'x': 'B', 'y': 3},
                        {'x': 'C', 'y': 6},
                        {'x': 'D', 'y': 7},
                        {'x': 'E', 'y': 2}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}

def test_vega_no_console_errors(page):
    vega = Vega(vega_example)

    msgs, _ = serve_component(page, vega)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

def test_vega_update_inline_data(page):
    """
    Ensure new data is rendered when the Vega object is updated with new inline data.
    """
    obj = {
        "$schema": "https://vega.github.io/schema/vega-lite/v3.2.1.json",
        "mark": "bar",
        "encoding": {
            "x": {"field": "month", "type": "ordinal"},
            "y": {"field": "revenue", "type": "quantitative"},
        },
        "width": "container",
        "data": {
            "values": pd.DataFrame(
                {"month": ["Jan", "Feb", "Mar"], "revenue": [100000, 125000, 150000]}
            )
        },
    }
    vega = Vega(obj)

    serve_component(page, vega)

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    wait_until(lambda: vega_plot.locator('path[aria-label*="Jan"]').count() > 0, page)

    new_obj = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "mark": "bar",
        "encoding": {
            "x": {"field": "month", "type": "ordinal"},
            "y": {"field": "revenue", "type": "quantitative"},
        },
        "width": "container",
        "data": {
            "values": pd.DataFrame(
                {"month": ["Apr", "May", "Jun"], "revenue": [175000, 200000, 225000]}
            )
        },
    }
    vega.object = new_obj
    wait_until(lambda: vega_plot.locator('path[aria-label*="Apr"]').count() > 0, page)
    wait_until(lambda: vega_plot.locator('path[aria-label*="Jan"]').count() == 0, page)


@altair_available
def test_altair_select_point(page, dataframe):
    multi = alt.selection_point(name='multi')  # selection of type "interval"

    chart = alt.Chart(dataframe).mark_point(size=12000).encode(
        x='int',
        y='float',
        color=alt.condition(multi, alt.value('black'), alt.value('lightgray'))
    ).add_params(multi)

    pane = Vega(chart)

    serve_component(page, pane)

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()

    page.mouse.click(bbox['x']+200, bbox['y']+150)

    wait_until(lambda: pane.selection.multi == [2], page)

    page.keyboard.down('Shift')
    page.mouse.click(bbox['x']+300, bbox['y']+100)

    wait_until(lambda: pane.selection.multi == [2, 3], page)

@altair_available
def test_altair_select_interval(page, dataframe):
    brush = alt.selection_interval(name='brush')  # selection of type "interval"

    chart = alt.Chart(dataframe).mark_circle().encode(x='int', y='float').add_params(brush)

    pane = Vega(chart)

    serve_component(page, pane)

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()
    vega_plot.click()

    page.mouse.move(bbox['x']+100, bbox['y']+100)
    page.mouse.down()
    page.mouse.move(bbox['x']+300, bbox['y']+300, steps=5)
    page.mouse.up()

    wait_until(lambda: pane.selection.brush == {'int': [0.61, 2.61], 'float': [0.33333333333333326, 7]}, page)


@altair_available
def test_altair_select_agg(page, dataframe):
    multi_bar_ref = alt.selection_point(fields=['str'], name='multi_bar_ref')

    chart = (alt.Chart(dataframe).mark_bar()
        .transform_aggregate(
            x = 'mean(float)',
            groupby=['str']
        )
        .encode(
            x=alt.X('x:Q'),
            y=alt.Y('str:N'),
            color=alt.condition(multi_bar_ref, alt.value('black'), alt.value('lightgray'))
        )
        .add_params(multi_bar_ref)
    )

    pane = Vega(chart)

    serve_component(page, pane)

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()

    page.mouse.click(bbox['x']+50, bbox['y']+50)

    wait_until(lambda: pane.selection.multi_bar_ref == [{'str': 'C'}], page)

    page.keyboard.down('Shift')
    page.mouse.click(bbox['x']+50, bbox['y']+10)

    wait_until(lambda: pane.selection.multi_bar_ref == [{'str': 'C'}, {'str': 'A'}], page)


def test_vega_update_data_without_reembedding(page):
    obj = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "mark": "bar",
        "encoding": {
            "x": {"field": "month", "type": "ordinal"},
            "y": {"field": "revenue", "type": "quantitative"},
        },
        "data": {
            "values": pd.DataFrame(
                {"month": ["Jan", "Feb", "Mar"], "revenue": [100000, 125000, 150000]}
            )
        },
    }
    vega = Vega(obj)

    serve_component(page, vega)

    vega_plot = page.locator('.vega-embed')
    wait_until(lambda: vega_plot.locator('path[aria-label*="Jan"]').count() > 0, page)

    page.evaluate("""() => {
      window.__embeds = 0
      const embed = window.vegaEmbed
      window.vegaEmbed = (...args) => { window.__embeds += 1; return embed(...args) }
    }""")

    new_values = pd.DataFrame({"month": ["Apr", "May", "Jun"], "revenue": [175000, 200000, 225000]})
    vega.object = {**obj, "data": {"values": new_values}}
    wait_until(lambda: vega_plot.locator('path[aria-label*="Apr"]').count() > 0, page)
    wait_until(lambda: vega_plot.locator('path[aria-label*="Jan"]').count() == 0, page)
    # The data is pushed into the existing view instead of recompiling the spec
    assert page.evaluate("() => window.__embeds") == 0

    vega.object = {**obj, "mark": "point", "data": {"values": new_values}}
    wait_until(lambda: page.evaluate("() => window.__embeds") == 1, page)
    wait_until(lambda: vega_plot.locator('path[aria-label*="Apr"]').count() > 0, page)


def _bar_spec(renderer, **size):
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "mark": "bar",
        "encoding": {
            "x": {"field": "x", "type": "ordinal"},
            "y": {"field": "y", "type": "quantitative"},
        },
        "data": {"values": [{"x": "A", "y": 5}, {"x": "B", "y": 3}]},
        "usermeta": {"embedOptions": {"renderer": renderer}},
        **size,
    }


def _css_sized_column(vega, height):
    # The height comes from a CSS variable on the document, so changing it
    # resizes the column without going through Bokeh's layout, like a
    # splitter or a docked panel does.
    return Column(
        vega, width=400,
        stylesheets=[f':host {{ height: var(--vega-test-height, {height}) !important; }}']
    )


def _set_css_height(page, height):
    page.evaluate(f"() => document.documentElement.style.setProperty('--vega-test-height', '{height}')")


def _chart(page, renderer):
    return page.locator(f'.vega-embed {renderer}.marks')


def _chart_size(page, renderer):
    bbox = _chart(page, renderer).bounding_box()
    return bbox['width'], bbox['height']


def _fills_container(page, renderer, height=None):
    width, chart_height = _chart_size(page, renderer)
    bbox = page.locator('.vega-embed').bounding_box()
    if height is not None and abs(bbox['height'] - height) > 2:
        return False
    return chart_height > 0 and abs(width - bbox['width']) <= 2 and abs(chart_height - bbox['height']) <= 2


# Vertical space taken by the pane's margin and the vega-embed padding
MARGIN = 20


@pytest.mark.parametrize('renderer', ['canvas', 'svg'])
def test_vega_container_size_follows_css_resize(page, renderer):
    vega = Vega(_bar_spec(renderer, width="container", height="container"))

    serve_component(page, _css_sized_column(vega, '200px'))

    expect(_chart(page, renderer)).to_have_count(1)
    wait_until(lambda: _fills_container(page, renderer, 200 - MARGIN), page)

    for height in (400, 250, 350):
        _set_css_height(page, f'{height}px')
        wait_until(lambda h=height: _fills_container(page, renderer, h - MARGIN), page)


@pytest.mark.parametrize('renderer', ['canvas', 'svg'])
def test_vega_container_size_embedded_at_zero_height(page, renderer):
    vega = Vega(_bar_spec(renderer, width="container", height="container"))

    serve_component(page, _css_sized_column(vega, '0px'))

    expect(_chart(page, renderer)).to_have_count(1)
    page.wait_for_timeout(200)

    for height in (300, 200):
        _set_css_height(page, f'{height}px')
        wait_until(lambda h=height: _fills_container(page, renderer, h - MARGIN), page)


@pytest.mark.parametrize('renderer', ['canvas', 'svg'])
def test_vega_container_size_follows_layout_resize(page, renderer):
    vega = Vega(_bar_spec(renderer, width="container", height="container"))
    col = Column(vega, width=400, height=200)

    serve_component(page, col)

    expect(_chart(page, renderer)).to_have_count(1)
    wait_until(lambda: _fills_container(page, renderer, 200 - MARGIN), page)

    for height in (400, 300):
        col.height = height
        wait_until(lambda h=height: _fills_container(page, renderer, h - MARGIN), page)


@pytest.mark.parametrize('renderer', ['canvas', 'svg'])
def test_vega_fixed_size_ignores_container_resize(page, renderer):
    vega = Vega(_bar_spec(renderer, width=200, height=150))

    serve_component(page, _css_sized_column(vega, '300px'))

    expect(_chart(page, renderer)).to_have_count(1)
    page.wait_for_timeout(200)
    initial = _chart_size(page, renderer)

    _set_css_height(page, '500px')
    page.wait_for_timeout(500)

    assert _chart_size(page, renderer) == initial
