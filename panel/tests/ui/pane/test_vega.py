import time

import pytest

try:
    import altair as alt
except Exception:
    alt = None

altair_available = pytest.mark.skipif(alt is None, reason='Requires altair')

from panel.io.server import serve
from panel.pane import Vega

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

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

def test_vega_no_console_errors(page, port):
    vega = Vega(vega_example)
    serve(vega, port=port, threaded=True, show=False)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@altair_available
def test_altair_select_point(page, port, dataframe):
    multi = alt.selection_point(name='multi')  # selection of type "interval"

    chart = alt.Chart(dataframe).mark_point(size=12000).encode(
        x='int',
        y='float',
        color=alt.condition(multi, alt.value('black'), alt.value('lightgray'))
    ).add_params(multi)

    pane = Vega(chart)

    serve(pane, port=port, threaded=True, show=False)

    time.sleep(1)

    page.goto(f"http://localhost:{port}")

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()

    page.mouse.click(bbox['x']+200, bbox['y']+150)

    time.sleep(0.2)

    assert pane.selection.multi == [2]

    page.keyboard.down('Shift')
    page.mouse.click(bbox['x']+300, bbox['y']+100)

    time.sleep(0.2)

    assert pane.selection.multi == [2, 3]

@altair_available
def test_altair_select_interval(page, port, dataframe):
    brush = alt.selection_interval(name='brush')  # selection of type "interval"

    chart = alt.Chart(dataframe).mark_circle().encode(x='int', y='float').add_params(brush)

    pane = Vega(chart)

    serve(pane, port=port, threaded=True, show=False)

    time.sleep(1)

    page.goto(f"http://localhost:{port}")

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()
    vega_plot.click()

    page.mouse.move(bbox['x']+100, bbox['y']+100)
    page.mouse.down()
    page.mouse.move(bbox['x']+300, bbox['y']+300, steps=5)
    page.mouse.up()

    time.sleep(0.2)

    assert pane.selection.brush == {'int': [0.61, 2.61], 'float': [0.33333333333333326, 7]}


@altair_available
def test_altair_select_agg(page, port, dataframe):
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

    serve(pane, port=port, threaded=True, show=False)

    time.sleep(1)

    page.goto(f"http://localhost:{port}")

    vega_plot = page.locator('.vega-embed')
    expect(vega_plot).to_have_count(1)

    bbox = vega_plot.bounding_box()

    page.mouse.click(bbox['x']+50, bbox['y']+50)

    time.sleep(0.2)

    assert pane.selection.multi_bar_ref == [{'str': 'C'}]

    page.keyboard.down('Shift')
    page.mouse.click(bbox['x']+50, bbox['y']+10)

    time.sleep(0.2)

    assert pane.selection.multi_bar_ref == [{'str': 'C'}, {'str': 'A'}]
