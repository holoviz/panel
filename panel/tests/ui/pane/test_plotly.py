import time

import pytest

pytest.importorskip("playwright")
pytest.importorskip("plotly")

import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from playwright.sync_api import expect

from panel.pane import Plotly
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui

pio.templates.default = None

@pytest.fixture
def plotly_2d_plot():
    trace = go.Scatter(x=[0, 1], y=[2, 3], uid='Test')
    plot_2d = Plotly({'data': [trace], 'layout': {'width': 350}})
    return plot_2d

@pytest.fixture
def plotly_2d_figure_widget():
    trace = go.Scatter(x=[0, 1], y=[2, 3], uid='Test')
    plot_2d = go.FigureWidget(data=[trace])
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


@pytest.fixture
def plotly_img_plot():
    fig_dict = dict(
        data={
            "z": np.random.randint(0, 255, size=(6, 30, 3)).astype(np.uint8),
            "type": "image",
        },
        layout={
            "width": 300,
            "height": 60,
            "margin": {"l": 0, "r": 0, "b": 0, "t": 0},
        },
    )
    return Plotly(fig_dict, width=300, height=60)


def test_plotly_no_console_errors(page, plotly_2d_plot):
    msgs, _ = serve_component(page, plotly_2d_plot)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []



def test_plotly_2d_plot(page, plotly_2d_plot):
    serve_component(page, plotly_2d_plot)

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

    wait_until(lambda: plotly_2d_plot.viewport == {
        'xaxis.range': [-0.08103975535168195, 1.081039755351682],
        'yaxis.range': [1.9267515923566878, 3.073248407643312]
    }, page)


def test_plotly_3d_plot(page, plotly_3d_plot):
    plot_3d, title = plotly_3d_plot

    serve_component(page, plot_3d)

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


def test_plotly_hover_data(page, plotly_2d_plot):
    hover_data = []
    plotly_2d_plot.param.watch(lambda e: hover_data.append(e.new), 'hover_data')

    serve_component(page, plotly_2d_plot)

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and hover on first point
    point = plotly_plot.locator('g.points path.point').nth(0)
    point.hover(force=True)

    def check_hover():
        assert plotly_2d_plot.hover_data == {
            'selector': None,
            'device_state': {
                'alt': False,
                'button': 0,
                'buttons': 0,
                'ctrl': False,
                'meta': False,
                'shift': False,
            },
            'points': [{
                'curveNumber': 0,
                'pointIndex': 0,
                'pointNumber': 0,
                'x': 0,
                'y': 2
            }]
        }
    wait_until(check_hover, page)

    # Hover somewhere else
    plot = page.locator('.js-plotly-plot .plot-container.plotly g.scatterlayer')
    plot.hover(force=True)

    wait_until(lambda: plotly_2d_plot.hover_data is None, page)


def test_plotly_click_data(page, plotly_2d_plot):
    serve_component(page, plotly_2d_plot)

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and click on points
    for i in range(2):
        point = page.locator('.js-plotly-plot .plot-container.plotly path.point').nth(i)
        point.click(force=True)

        def check_click(i=i):
            assert plotly_2d_plot.click_data == {
                'selector': None,
                'device_state': {
                    'alt': False,
                    'button': 0,
                    'buttons': 1,
                    'ctrl': False,
                    'meta': False,
                    'shift': False,
                },
                'points': [{
                    'curveNumber': 0,
                    'pointIndex': i,
                    'pointNumber': i,
                    'x': 0+i,
                    'y': 2+i
                }]
            }
        wait_until(check_click, page)
        time.sleep(0.2)


def test_plotly_click_data_figure_widget(page, plotly_2d_figure_widget):
    fig = go.FigureWidget(plotly_2d_figure_widget)
    serve_component(page, fig)

    trace = list(fig.select_traces())[0]

    events = []
    trace.on_click(lambda a, b, c: events.append((a, b, c)))

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and click on points
    for i in range(2):
        point = page.locator('.js-plotly-plot .plot-container.plotly path.point').nth(i)
        point.click(force=True)

        def check_click(i=i):
            if len(events) < (i+1):
                return False
            click_trace, points, device_state = events[i]
            assert click_trace is trace
            assert points.xs == [0+i]
            assert points.ys == [2+i]
            assert not device_state.ctrl
            assert not device_state.alt
            assert not device_state.shift
            assert not device_state.meta
        wait_until(check_click, page)
        time.sleep(0.2)


def test_plotly_select_data(page, plotly_2d_plot):
    serve_component(page, plotly_2d_plot)

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    page.locator('a.modebar-btn[data-val="select"]').click()

    bbox = page.locator('.js-plotly-plot .plot-container.plotly').bounding_box()

    page.mouse.move(bbox['x']+100, bbox['y']+100)
    page.mouse.down()
    page.mouse.move(bbox['x']+bbox['width'], bbox['y']+bbox['height'], steps=5)
    page.mouse.up()

    wait_until(lambda: plotly_2d_plot.selected_data is not None, page)

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



def test_plotly_img_plot(page, plotly_img_plot):
    msgs, _ = serve_component(page, plotly_img_plot)

    # main pane
    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

    # Select and hover on first point
    point = plotly_plot.locator('image')
    point.hover(force=True)

    def check_hover():
        assert plotly_img_plot.hover_data == {
            'selector': None,
            'device_state': {
                'alt': False,
                'button': 0,
                'buttons': 0,
                'ctrl': False,
                'meta': False,
                'shift': False,
            },
            'points': [{'curveNumber': 0, 'x': 15, 'y': 3, 'colormodel': 'rgb'}]
        }
    wait_until(check_hover, page)
