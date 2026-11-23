import datetime as dt
import time

import pytest

pytest.importorskip("playwright")
pytest.importorskip("plotly")

import numpy as np
import param
import plotly.graph_objs as go
import plotly.io as pio

from playwright.sync_api import expect

from panel.custom import Child, ReactComponent
from panel.layout import Column
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

    points = page.locator('.js-plotly-plot .plot-container.plotly path.point')
    expect(points).to_have_count(2)

    for i in range(2):
        points.nth(i).hover(force=True)
        wait_until(lambda i=i: (plotly_2d_plot.hover_data or {}).get('points', [{}])[0].get('pointNumber') == i, page)
        points.nth(i).click(force=True)

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


def test_plotly_click_data_multicategory(page):
    # Regression test for https://github.com/holoviz/panel/issues/7010
    fig = go.Figure(
        data=[go.Scatter(x=[['A', 'A', 'B', 'B'], [0, 1, 2, 3]], y=[0, 2, -1, 1], mode='markers')],
        layout={'xaxis_type': 'multicategory'}
    )
    pane = Plotly(fig)
    serve_component(page, pane)

    points = page.locator('.js-plotly-plot .plot-container.plotly path.point')
    expect(points).to_have_count(4)
    points.nth(2).click(force=True)

    def check_click():
        assert pane.click_data is not None
        point = pane.click_data['points'][0]
        assert point['x'] == ['B', 2]
        assert point['y'] == -1
        assert point['pointNumber'] == 2
        assert 'data' not in point and 'fullData' not in point
        assert 'xaxis' not in point and 'yaxis' not in point
    wait_until(check_click, page)


def test_plotly_click_data_heatmap(page):
    # Regression test for https://github.com/holoviz/panel/issues/7010
    fig = go.Figure(data=[go.Heatmap(z=[[1, 2], [3, 4]], x=['A', 'B'], y=['C', 'D'])])
    pane = Plotly(fig)
    serve_component(page, pane)

    drag = page.locator('.js-plotly-plot .nsewdrag').first
    expect(drag).to_be_visible()
    box = drag.bounding_box()
    page.mouse.click(box['x'] + box['width'] * 0.75, box['y'] + box['height'] * 0.25)

    def check_click():
        assert pane.click_data is not None
        point = pane.click_data['points'][0]
        assert point['x'] == 'B'
        assert point['y'] == 'D'
        assert point['z'] == 4
        assert point['pointNumber'] == [1, 1]
        assert point['pointIndex'] == [1, 1]
        assert 'data' not in point and 'fullData' not in point
        assert 'xaxis' not in point and 'yaxis' not in point
    wait_until(check_click, page)


def test_plotly_click_after_resize_without_size_change(page, plotly_2d_plot):
    serve_component(page, plotly_2d_plot)

    point = page.locator('.js-plotly-plot .plot-container.plotly path.point').nth(0)
    point.hover(force=True)
    wait_until(lambda: (plotly_2d_plot.hover_data or {}).get('points', [{}])[0].get('pointNumber') == 0, page)

    model_id = next(iter(plotly_2d_plot._models.values()))[0].id
    page.evaluate(f"() => Bokeh.index.find_one_by_id('{model_id}').invalidate_layout()")
    page.wait_for_timeout(60)
    point.click(force=True)

    wait_until(lambda: (plotly_2d_plot.click_data or {}).get('points', [{}])[0].get('pointNumber') == 0, page)


@pytest.mark.parametrize('per_point', [False, True])
def test_plotly_batch_update_leaves_unchanged_trace_properties(page, per_point):
    fig = go.Figure([go.Scatter(x=[0, 1, 2], y=[1, 2, 3]) for _ in range(3)])
    serve_component(page, Plotly(fig))

    plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plot).to_have_count(1)

    def color(last):
        return [last] * 3 if per_point else last

    with fig.batch_update():
        for trace, c in zip(fig.data, ['red', 'green', 'blue']):
            trace.marker.color = color(c)
    gd = page.locator('.js-plotly-plot')
    get_colors = "gd => gd.data.map(t => t.marker && t.marker.color)"
    wait_until(lambda: gd.evaluate(get_colors) == [color(c) for c in ['red', 'green', 'blue']], page)

    with fig.batch_update():
        for trace, c in zip(fig.data, ['red', 'green', 'orange']):
            trace.y = [4, 5, 6]
            trace.marker.color = color(c)

    wait_until(lambda: gd.evaluate("gd => gd.data[2].marker.color") == color('orange'), page)
    assert gd.evaluate(get_colors) == [color(c) for c in ['red', 'green', 'orange']]
    assert gd.evaluate("gd => gd.data.map(t => t.y)") == [[4, 5, 6]] * 3


# Can't reliably simulate the clicks so disabling
def _test_plotly_click_data_figure_widget(page, plotly_2d_figure_widget):
    fig = go.FigureWidget(plotly_2d_figure_widget)
    serve_component(page, fig)

    trace = list(fig.select_traces())[0]

    events = []
    trace.on_click(lambda a, b, c: events.append((a, b, c)))

    plotly_plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plotly_plot).to_have_count(1)

    # Select and click on points
    for i in range(2):
        for _ in range(5):
            # Simulating click is unreliable
            point = page.locator('.js-plotly-plot .plot-container.plotly path.point').nth(i)
            point.click(force=True)
            time.sleep(0.1)

        def check_click(i=i):
            if len(events) < ((i+1)*5):
                return False
            click_trace, points, device_state = events[-1 if i else 4]
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

    page.locator('button.modebar-btn[data-val="select"]').click()

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



def test_plotly_click_data_add_trace(page):
    # Regression test for https://github.com/holoviz/panel/issues/8470
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1, 2, 3], y=[0, 1, 2, 3], mode='markers'))
    fig.update_layout(uirevision='keep')

    pane = Plotly(fig)

    def on_click(event):
        if event.new is None:
            return
        pt = event.new['points'][0]
        fig.add_trace(go.Scatter(
            x=[pt['x']], y=[pt['y']], mode='markers', showlegend=False,
        ))

    pane.param.watch(on_click, 'click_data')

    serve_component(page, pane)

    point = page.locator('.js-plotly-plot path.point').first
    expect(point).to_be_visible()

    for _ in range(3):
        point.click(force=True)
        page.wait_for_timeout(100)

    GET_TRACE_COUNT_JS = """() => {
        function find(root) {
          for (const d of root.querySelectorAll('div')) {
            if (d.data && Array.isArray(d.data)) return d.data.length;
          }
          for (const el of root.querySelectorAll('*')) {
            if (el.shadowRoot) { const r = find(el.shadowRoot); if (r !== null) return r; }
          }
          return null;
        }
        return find(document);
    }"""

    wait_until(lambda: page.evaluate(GET_TRACE_COUNT_JS) > 1, page)


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
        assert plotly_img_plot.hover_data is not None
        assert plotly_img_plot.hover_data['device_state'] == {
            'alt': False,
            'button': 0,
            'buttons': 0,
            'ctrl': False,
            'meta': False,
            'shift': False,
        }
        point = plotly_img_plot.hover_data['points'][0]
        assert {k: point[k] for k in ('curveNumber', 'pointNumber', 'pointIndex', 'x', 'y', 'colormodel')} == {
            'curveNumber': 0,
            'pointNumber': [3, 15],
            'pointIndex': [3, 15],
            'x': 15,
            'y': 3,
            'colormodel': 'rgb',
        }
        assert point['z'] == point['color']
    wait_until(check_hover, page)


def test_plotly_update_traces_keeps_date_axis(page):
    index = [dt.datetime(2019, 1, i) for i in range(1, 11)]
    fig = go.Figure([go.Scatter(x=index, y=np.arange(10))])
    plot = Plotly(fig, width=400, height=300)

    serve_component(page, plot)

    plotly_plot = page.locator('.js-plotly-plot')
    expect(plotly_plot).to_have_count(1)
    wait_until(lambda: plotly_plot.evaluate('el => el._fullLayout.xaxis.type') == 'date', page)

    fig.update_traces(x=np.array(index[:5]), y=np.arange(5))

    wait_until(lambda: plotly_plot.evaluate('el => el.data[0].x.length') == 5, page)
    assert plotly_plot.evaluate('el => el._fullLayout.xaxis.type') == 'date'


def test_plotly_python_restyle_is_not_echoed(page):
    fig = go.Figure([go.Scatter(x=[0, 1, 2], y=[1, 2, 3])])
    pane = Plotly(fig)
    serve_component(page, pane)

    plot = page.locator('.js-plotly-plot .plot-container.plotly')
    expect(plot).to_have_count(1)

    echoes = []
    pane.param.watch(lambda e: echoes.append(e.new), 'restyle_data')

    fig.data[0].marker.color = 'red'
    gd = page.locator('.js-plotly-plot')
    wait_until(lambda: gd.evaluate("gd => gd.data[0].marker?.color") == 'red', page)

    page.wait_for_timeout(500)
    assert echoes == []


def test_plotly_js_layout_change_replots_without_roundtrip(page, plotly_2d_plot):
    serve_component(page, plotly_2d_plot)

    expect(page.locator('.js-plotly-plot .plot-container.plotly')).to_have_count(1)

    model_id = next(iter(plotly_2d_plot._models.values()))[0].id
    page.evaluate(f"""() => {{
      const model = Bokeh.index.find_one_by_id('{model_id}').model
      model.layout = {{...model.layout, title: {{text: 'Updated'}}}}
    }}""")

    expect(page.locator('.js-plotly-plot .gtitle')).to_have_text('Updated')

    page.wait_for_timeout(500)
    assert plotly_2d_plot._render_count == 0


def test_plotly_data_update_keeps_frames(page):
    frames = [go.Frame(name='first', data=[go.Scatter(y=[3, 4])])]
    pane = Plotly(go.Figure(data=[go.Scatter(x=[0, 1], y=[1, 2])], frames=frames))

    serve_component(page, pane)

    gd = page.locator('.js-plotly-plot')
    wait_until(lambda: gd.evaluate("gd => gd._transitionData._frames.length") == 1, page)

    page.evaluate("""() => {
      window.__addFrames = 0
      const addFrames = window.Plotly.addFrames
      window.Plotly.addFrames = (...args) => { window.__addFrames += 1; return addFrames(...args) }
    }""")

    pane.object = go.Figure(data=[go.Scatter(x=[0, 1], y=[5, 6])], frames=frames)
    wait_until(lambda: gd.evaluate("gd => gd.data[0].y[0]") == 5, page)
    assert gd.evaluate("gd => gd._transitionData._frames.length") == 1
    assert page.evaluate("() => window.__addFrames") == 0

    new_frames = frames + [go.Frame(name='second', data=[go.Scatter(y=[7, 8])])]
    pane.object = go.Figure(data=[go.Scatter(x=[0, 1], y=[5, 6])], frames=new_frames)
    wait_until(lambda: gd.evaluate("gd => gd._transitionData._frames.length") == 2, page)


class PlotlyToggle(ReactComponent):
    """Renders its child only once `mounted` is set."""

    child = Child()

    mounted = param.Boolean(default=False)

    text = param.String()

    _esm = """
    export function render({ model }) {
      const [mounted] = model.useState("mounted")
      const [text] = model.useState("text")
      const child = model.get_child("child")
      return <div><h2>{text}</h2>{mounted ? child : null}</div>
    }
    """


U = '_undefined_'

RESTYLES = {
    'traces_0_then_01_then_1': [
        ({'marker.color': ['red']}, [0]),
        ({'marker.color': ['blue', 'green']}, [0, 1]),
        ({'marker.color': ['orange']}, [1]),
    ],
    'merge_past_other_key_same_traces': [
        ({'marker.color': ['a1', 'b1']}, [0, 1]),
        ({'opacity': [0.5]}, [1]),
        ({'marker.color': ['red', 'blue']}, [0, 1]),
    ],
    'null_mixed_with_specific': [
        ({'opacity': 0.2}, None),
        ({'opacity': [0.7]}, [1]),
        ({'marker.color': 'red'}, None),
        ({'opacity': [0.9]}, [0]),
        ({'marker.color': ['blue']}, [2]),
        ({'opacity': 0.4}, None),
        ({'marker.color': ['green']}, [1]),
    ],
    'same_key_overlapping_sets_between': [
        ({'marker.color': ['red', 'red']}, [0, 1]),
        ({'marker.color': ['blue', 'blue']}, [1, 2]),
        ({'marker.color': ['green', 'green']}, [0, 1]),
        ({'marker.color': ['black']}, [2]),
        ({'marker.color': ['white', 'white']}, [1, 2]),
    ],
    'overlap_then_same_merge': [
        ({'marker.color': ['red'], 'opacity': [0.3]}, [0]),
        ({'opacity': [0.6, 0.6]}, [0, 1]),
        ({'marker.color': ['blue']}, [0]),
        ({'opacity': [0.8]}, [0]),
    ],
    'nested_parent_child_keys': [
        ({'marker.color': ['red', 'blue']}, [0, 1]),
        ({'marker': [{'color': 'green', 'size': 20}]}, [1]),
        ({'marker.color': ['black', 'white']}, [0, 1]),
    ],
    'undefined_slots': [
        ({'marker.color': ['red', 'blue']}, [0, 1]),
        ({'marker.color': [U, 'green']}, [0, 1]),
    ],
    'undefined_slots_cover': [
        ({'marker.color': ['red']}, [0]),
        ({'marker.color': [U, 'green', 'blue']}, [0, 1, 2]),
    ],
    'negative_trace_index': [
        ({'marker.color': ['red']}, [-1]),
        ({'marker.color': ['blue']}, [2]),
        ({'opacity': [0.4]}, [-1]),
    ],
}

RELAYOUTS = {
    'leaf_then_parent': [{'xaxis.range': [0, 5]}, {'xaxis': {'title': {'text': 'X'}}}],
    'parent_then_leaf': [{'xaxis': {'title': {'text': 'X'}, 'range': [0, 2]}}, {'xaxis.range': [0, 5]}],
    'leaf_parent_leaf': [{'xaxis.range': [0, 5]}, {'xaxis': {'title': {'text': 'X'}}}, {'xaxis.range': [1, 3]}],
    'title_text_then_title': [{'title.text': 'A'}, {'title': {'text': 'B', 'x': 0.2}}, {'title.text': 'C'}],
    'range_then_autorange': [{'xaxis.range': [0, 5]}, {'xaxis.autorange': True}],
    'autorange_then_range': [{'xaxis.autorange': True}, {'xaxis.range': [0, 5]}],
    'annotation_insert': [
        {'annotations[0].text': 'x0'},
        {'annotations[1].text': 'x1'},
        {'annotations[0]': {'x': 0, 'y': 0, 'text': 'new0'}},
        {'annotations[0].text': 'y0'},
        {'annotations[1].x': 2},
    ],
    'annotation_remove': [
        {'annotations[1].text': 'x1'},
        {'annotations[0]': None},
        {'annotations[0].text': 'y0'},
    ],
    'annotations_then_item': [
        {'annotations[0].text': 'x0'},
        {'annotations': [{'x': 0, 'y': 0, 'text': 'w0'}]},
        {'annotations[0].text': 'z0'},
    ],
}

READ_TRACES = "gd => gd.data.map(t => [t.marker?.color ?? null, t.marker?.size ?? null, t.opacity ?? null])"

READ_LAYOUT = """gd => [
  gd.layout.xaxis?.range ?? null, gd.layout.xaxis?.title?.text ?? null, gd.layout.title?.text ?? null,
  gd.layout.title?.x ?? null, gd.layout.xaxis?.autorange ?? null,
  (gd.layout.annotations ?? []).map(a => [a.text, a.x])
]"""


def _serve_mounted_and_unmounted(page):
    figures = [
        go.Figure(
            [go.Scatter(x=[0, 1], y=[i, i + 1], mode='markers') for i in range(3)],
            layout={'annotations': [{'x': 0, 'y': 0, 'text': 'a0'}, {'x': 1, 'y': 1, 'text': 'a1'}]}
        )
        for _ in range(2)
    ]
    mounted, unmounted = Plotly(figures[0]), Plotly(figures[1])
    toggle = PlotlyToggle(child=unmounted, text='Unmounted')
    layout = Column(PlotlyToggle(child=mounted, text='Mounted', mounted=True), toggle)
    serve_component(page, layout)
    gd = page.locator('.js-plotly-plot')
    expect(gd).to_have_count(1)
    models = [next(iter(pane._models.values()))[0] for pane in (mounted, unmounted)]
    return gd, toggle, next(iter(layout._documents)), models, unmounted


def _send(page, doc, models, prop, value):
    def send():
        for model in models:
            setattr(model, prop, value)
    doc.add_next_tick_callback(send)
    wait_until(lambda: all(getattr(model, prop) is None for model in models), page)


@pytest.mark.parametrize('name', list(RESTYLES))
def test_plotly_restyles_before_render_match_mounted_plot(page, name):
    gd, toggle, doc, models, _ = _serve_mounted_and_unmounted(page)

    for data, traces in RESTYLES[name]:
        _send(page, doc, models, 'restyle', {'data': data, 'traces': traces})

    toggle.mounted = True
    expect(gd).to_have_count(2)
    wait_until(lambda: gd.nth(1).evaluate(READ_TRACES) == gd.nth(0).evaluate(READ_TRACES), page)


@pytest.mark.parametrize('name', list(RELAYOUTS))
def test_plotly_relayouts_before_render_match_mounted_plot(page, name):
    gd, toggle, doc, models, _ = _serve_mounted_and_unmounted(page)

    for relayout in RELAYOUTS[name]:
        _send(page, doc, models, 'relayout', relayout)

    toggle.mounted = True
    expect(gd).to_have_count(2)
    wait_until(lambda: gd.nth(1).evaluate(READ_LAYOUT) == gd.nth(0).evaluate(READ_LAYOUT), page)


def test_plotly_updates_before_render_stay_bounded(page):
    gd, toggle, doc, models, _ = _serve_mounted_and_unmounted(page)
    model = models[1]

    def send():
        for i in range(200):
            model.restyle = {'data': {'y': [list(range(i, i+1000))]}, 'traces': [0]}
            model.relayout = {'title.text': f'Title {i}'}
        toggle.text = 'Sent'
    doc.add_next_tick_callback(send)

    # The text arrives in the same patch, after all the updates
    expect(page.locator('h2').nth(1)).to_have_text('Sent')
    pending = page.evaluate(f"() => Bokeh.index.find_one_by_id('{model.id}')._pending_updates.length")
    assert pending == 2

    toggle.mounted = True
    expect(gd).to_have_count(2)
    wait_until(lambda: gd.nth(1).evaluate("gd => [gd.data[0].y[0], gd.data[0].y.length]") == [199, 1000], page)
    expect(gd.nth(1).locator('.gtitle')).to_have_text('Title 199')
