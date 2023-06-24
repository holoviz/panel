import time

import pytest

try:
    import plotly
    import plotly.graph_objs as go
    import plotly.io as pio
    pio.templates.default = None
except Exception:
    plotly = None
plotly_available = pytest.mark.skipif(plotly is None, reason="requires plotly")

import numpy as np

from panel.io.server import serve
from panel.pane import Plotly

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui


@pytest.fixture
def plotly_2d_plot():
    trace = go.Scatter(x=[0, 1], y=[2, 3], uid='Test')
    plot_2d = Plotly({'data': [trace], 'layout': {'width': 350}})
    return plot_2d


@pytest.fixture
def plotly_3d_plot():
    xx = np.linspace(-3.5, 3.5, 100)
    yy = np.linspace(-3.5, 3.5, 100)
    x, y = np.meshgrid(xx, yy)
    z = np.exp(-(x - 1) ** 2 - y ** 2) - (x ** 3 + y ** 4 - x / 5) * np.exp(-(x ** 2 + y ** 2))

    surface = go.Surface(z=z)
    title = 'Plotly 3D Plot'
    layout = go.Layout(
        title=title,
        autosize=False,
        width=500,
        height=500,
        margin=dict(t=50, b=50, r=50, l=50)
    )
    fig = dict(data=[surface], layout=layout)
    plot_3d = Plotly(fig, width=500, height=500)

    return plot_3d, title


@plotly_available
def test_plotly_no_console_errors(page, port, plotly_2d_plot):
    serve(plotly_2d_plot, port=port, threaded=True, show=False)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@plotly_available
def test_plotly_2d_plot(page, port, plotly_2d_plot):
    serve(plotly_2d_plot, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # main pane
    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # x y axes
    xaxis = page.locator('g.xaxislayer-above')
    yaxis = page.locator('g.yaxislayer-above')
    expect(xaxis).to_have_count(1)
    expect(yaxis).to_have_count(1)

    # mode bar
    modebar = page.locator('.modebar-container')
    expect(modebar).to_have_count(1)

    hover = page.locator('.hoverlayer')
    expect(hover).to_have_count(1)

    time.sleep(0.2)

    assert plotly_2d_plot.viewport == {
        'xaxis.range': [-0.08103975535168195, 1.081039755351682],
        'yaxis.range': [1.9267515923566878, 3.073248407643312]
    }


@plotly_available
@pytest.mark.flaky(max_runs=3)
def test_plotly_3d_plot(page, port, plotly_3d_plot):
    plot_3d, title = plotly_3d_plot
    serve(plot_3d, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # main pane
    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1, timeout=10_000)
    expect(plotly_plot).to_contain_text(title, use_inner_text=True)

    plot_title = page.locator('.g-gtitle')
    expect(plot_title).to_have_count(1)

    # actual plot
    plot = page.locator('.js-plotly-plot .plot-container.plotly .gl-container #scene')
    expect(plot).to_have_count(1)

    color_bar = page.locator('.colorbar')
    expect(color_bar).to_have_count(1)

    modebar = page.locator('.modebar-container')
    expect(modebar).to_have_count(1)


@plotly_available
@pytest.mark.flaky(max_runs=3)
def test_plotly_hover_data(page, port, plotly_2d_plot):
    serve(plotly_2d_plot, port=port, threaded=True, show=False)

    hover_data = []
    plotly_2d_plot.param.watch(lambda e: hover_data.append(e.new), 'hover_data')

    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and hover on first point
    point = plotly_plot.locator('g.points path.point').nth(0)
    point.hover(force=True)

    time.sleep(0.2)

    assert {
        'points': [{
            'curveNumber': 0,
            'pointIndex': 0,
            'pointNumber': 0,
            'x': 0,
            'y': 2
        }]
    } in hover_data

    # Hover somewhere else
    plot = page.locator('.js-plotly-plot .plot-container.plotly g.scatterlayer')
    plot.hover(force=True)

    time.sleep(0.2)

    assert plotly_2d_plot.hover_data is None


@plotly_available
@pytest.mark.flaky(max_runs=3)
def test_plotly_click_data(page, port, plotly_2d_plot):
    serve(plotly_2d_plot, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and click on first point
    point = page.locator('.js-plotly-plot .plot-container.plotly path.point').nth(0)
    point.click(force=True)

    time.sleep(0.2)

    assert plotly_2d_plot.click_data == {
        'points': [{
            'curveNumber': 0,
            'pointIndex': 0,
            'pointNumber': 0,
            'x': 0,
            'y': 2
        }]
    }



@plotly_available
@pytest.mark.flaky(max_runs=3)
def test_plotly_select_data(page, port, plotly_2d_plot):
    serve(plotly_2d_plot, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    page.locator('a.modebar-btn[data-val="select"]').click()

    bbox = page.locator('.js-plotly-plot .plot-container.plotly').bounding_box()

    page.mouse.move(bbox['x']+100, bbox['y']+100)
    page.mouse.down()
    page.mouse.move(bbox['x']+bbox['width'], bbox['y']+bbox['height'], steps=5)
    page.mouse.up()

    time.sleep(0.2)

    selected = plotly_2d_plot.selected_data
    assert selected is not None
    assert 'points' in selected
    assert selected['points'] == [{
        'curveNumber': 0,
        'pointIndex': 1,
        'pointNumber': 1,
        'x': 1,
        'y': 3
    }]
    assert 'range' in selected
    assert 'x' in selected['range']
    assert 'y' in selected['range']
