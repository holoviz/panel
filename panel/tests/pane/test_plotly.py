import datetime as dt

from importlib.util import find_spec

import pytest

try:
    import plotly
    import plotly.express as px
    import plotly.figure_factory as ff
    import plotly.graph_objs as go
    import plotly.io as pio
    pio.templates.default = None
except Exception:
    plotly = None
plotly_available = pytest.mark.skipif(plotly is None, reason="requires plotly")

import numpy as np
import pandas as pd

from panel.models.plotly import PlotlyPlot
from panel.pane import PaneBase, Plotly


@plotly_available
def test_get_plotly_pane_type_from_figure():
    trace = go.Scatter(x=[0, 1], y=[2, 3])
    fig = go.Figure([trace])
    assert PaneBase.get_pane_type(fig) is Plotly


@plotly_available
def test_get_plotly_pane_type_from_traces():
    trace = go.Scatter(x=[0, 1], y=[2, 3])
    assert PaneBase.get_pane_type([trace]) is Plotly


@plotly_available
def test_get_plotly_pane_type_from_trace():
    trace = go.Scatter(x=[0, 1], y=[2, 3])
    assert PaneBase.get_pane_type(trace) is Plotly


@plotly_available
def test_plotly_pane_single_trace(document, comm):
    trace = go.Scatter(x=[0, 1], y=[2, 3], uid='Test')
    pane = Plotly({'data': [trace], 'layout': {'width': 350}})

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, PlotlyPlot)
    assert pane._models[model.ref['id']][0] is model
    assert len(model.data) == 1
    assert model.data[0]['type'] == 'scatter'
    assert model.data[0]['x'] == [0, 1]
    assert model.data[0]['y'] == [2, 3]
    assert model.layout == {'width': 350}
    assert len(model.data_sources) == 1
    assert model.data_sources[0].data == {}

    # Replace Pane.object
    new_trace = go.Bar(x=[2, 3], y=[4, 5])
    pane.object = {'data': new_trace, 'layout': {'width': 350}}
    assert len(model.data) == 1
    assert model.data[0]['type'] == 'bar'
    assert model.data[0]['x'] == [2, 3]
    assert model.data[0]['y'] == [4, 5]
    assert model.layout == {'width': 350}
    assert len(model.data_sources) == 1
    assert model.data_sources[0].data == {}
    assert pane._models[model.ref['id']][0] is model

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@plotly_available
def test_plotly_pane_datetime_list_transform(document, comm):
    index = [dt.datetime(2019, 1, i) for i in range(1, 11)]
    data = np.random.randn(10)
    traces = [go.Scatter(x=index, y=data)]
    fig = go.Figure(traces)
    pane = Plotly(fig)

    model = pane.get_root(document, comm)
    assert all(isinstance(v, str) for v in model.data[0]['x'])


@plotly_available
def test_plotly_pane_datetime_array_transform(document, comm):
    index = np.array([dt.datetime(2019, 1, i) for i in range(1, 11)])
    data = np.random.randn(10)
    traces = [go.Scatter(x=index, y=data)]
    fig = go.Figure(traces)
    pane = Plotly(fig)

    model = pane.get_root(document, comm)
    assert model.data_sources[0].data['x'][0].dtype.kind == 'U'


@plotly_available
def test_plotly_pane_datetime64_list_transform(document, comm):
    index = [np.datetime64(dt.datetime(2019, 1, i)) for i in range(1, 11)]
    data = np.random.randn(10)
    traces = [go.Scatter(x=index, y=data)]
    fig = go.Figure(traces)
    pane = Plotly(fig)

    model = pane.get_root(document, comm)
    assert all(isinstance(v, str) for v in model.data[0]['x'])


@plotly_available
def test_plotly_pane_datetime64_array_transform(document, comm):
    index = np.array([dt.datetime(2019, 1, i) for i in range(1, 11)]).astype('M8[us]')
    data = np.random.randn(10)
    traces = [go.Scatter(x=index, y=data)]
    fig = go.Figure(traces)
    pane = Plotly(fig)

    model = pane.get_root(document, comm)
    assert model.data_sources[0].data['x'][0].dtype.kind in 'SU'


@plotly_available
def test_plotly_pane_numpy_to_cds_traces(document, comm):
    trace = go.Scatter(x=np.array([1, 2]), y=np.array([2, 3]))
    pane = Plotly({'data': [trace], 'layout': {'width': 350}})

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, PlotlyPlot)
    assert len(model.data) == 1
    assert model.data[0]['type'] == 'scatter'
    assert 'x' not in model.data[0]
    assert 'y' not in model.data[0]
    assert model.layout == {'width': 350}
    assert len(model.data_sources) == 1
    cds = model.data_sources[0]
    assert np.array_equal(cds.data['x'][0], np.array([1, 2]))
    assert np.array_equal(cds.data['y'][0], np.array([2, 3]))

    # Replace Pane.object
    new_trace = [go.Scatter(x=np.array([5, 6]), y=np.array([6, 7])),
                 go.Bar(x=np.array([2, 3]), y=np.array([4, 5]))]
    pane.object = {'data': new_trace, 'layout': {'width': 350}}
    assert len(model.data) == 2
    assert model.data[0]['type'] == 'scatter'
    assert 'x' not in model.data[0]
    assert 'y' not in model.data[0]
    assert model.data[1]['type'] == 'bar'
    assert 'x' not in model.data[1]
    assert 'y' not in model.data[1]
    assert model.layout == {'width': 350}
    assert len(model.data_sources) == 2
    cds = model.data_sources[0]
    assert np.array_equal(cds.data['x'][0], np.array([5, 6]))
    assert np.array_equal(cds.data['y'][0], np.array([6, 7]))
    cds2 = model.data_sources[1]
    assert np.array_equal(cds2.data['x'][0], np.array([2, 3]))
    assert np.array_equal(cds2.data['y'][0], np.array([4, 5]))

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@plotly_available
def test_plotly_autosize(document, comm):
    trace = go.Scatter(x=[0, 1], y=[2, 3])

    pane = Plotly(dict(data=[trace], layout={'autosize': True}))

    model = pane.get_root(document, comm=comm)
    assert model.sizing_mode == 'stretch_both'

    pane.object['layout']['autosize'] = False
    pane.param.trigger('object')
    assert model.sizing_mode == 'fixed'

    pane._cleanup(model)

    pane = Plotly(dict(data=[trace], layout={'autosize': True}), sizing_mode='fixed')
    model = pane.get_root(document, comm=comm)
    assert model.sizing_mode == 'fixed'

    pane._cleanup(model)


@plotly_available
def test_clean_relayout_data():
    relayout_data = {
        "mapbox.center": {"lon": -73.59183434290809, "lat": 45.52341668343991},
        "mapbox.zoom": 10,
        "mapbox.bearing": 0,
        "mapbox.pitch": 0,
        "mapbox._derived": {
            "coordinates": [
                [-73.92279747767401, 45.597934047192865],
                [-73.26087120814279, 45.597934047192865],
                [-73.26087120814279, 45.44880048640681],
                [-73.92279747767401, 45.44880048640681],
            ]
        },
    }
    result = Plotly._clean_relayout_data(relayout_data)
    assert result == {
        "mapbox.center": {"lon": -73.59183434290809, "lat": 45.52341668343991},
        "mapbox.zoom": 10,
        "mapbox.bearing": 0,
        "mapbox.pitch": 0,
    }


@pytest.mark.skipif(not find_spec("scipy"), reason="requires scipy")
@plotly_available
def test_plotly_swap_traces(document, comm):
    data_bar = pd.DataFrame({'Count': [1, 2, 3, 4], 'Category': ["A", "B", "C", "D"]})
    data_cts = np.random.randn(1000)

    bar_plot = px.bar(x=data_bar["Category"], y=data_bar["Count"])
    dist_plot = ff.create_distplot(
        [data_cts],
        ["distplot"],
        bin_size=0.5,
        show_hist=False,
        show_rug=False,
        histnorm="probability",
    )


    plotly = Plotly(bar_plot)

    model = plotly.get_root(document, comm)

    assert len(model.data_sources) == 1
    cds = model.data_sources[0]
    assert (cds.data['x'] == data_bar.Category.values).all()
    assert (cds.data['y'] == data_bar.Count.values).all()

    plotly.object = dist_plot

    assert 'x' not in cds.data
    assert len(cds.data['y'][0]) == 500


@plotly_available
def test_plotly_shape_datetime_converted(document, comm):
    # see https://github.com/holoviz/panel/issues/5252
    start = pd.Timestamp('2022-05-11 0:00:00', tz=dt.timezone.utc)
    date_range = pd.date_range(start=start, periods=20, freq='h')

    df = pd.DataFrame({
        "x": date_range,
        "y": list(range(len(date_range))),
    })

    fig = px.scatter(df, x="x", y="y")
    fig.add_vline(x=pd.Timestamp('2022-05-11 9:00:00', tz=dt.timezone.utc))

    p = Plotly(fig)

    model = p.get_root(document, comm)

    assert model.layout['shapes'][0]['x0'] == '2022-05-11 09:00:00+00:00'


@plotly_available
def test_plotly_datetime_converted_2d_array(document, comm):
    # see https://github.com/holoviz/panel/issues/7309
    n_points = 3
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=n_points, freq='min'),
        'latitude': np.cumsum(np.random.randn(n_points) * 0.01) + 52.3702,  # Centered around Amsterdam
        'longitude': np.cumsum(np.random.randn(n_points) * 0.01) + 4.8952,  # Centered around Amsterdam
    })

    fig = px.scatter_mapbox(data, lon='longitude', lat='latitude', custom_data='timestamp')

    p = Plotly(fig)

    model = p.get_root(document, comm)

    assert len(model.data_sources) == 1

    cds = model.data_sources[0]
    assert isinstance(cds.data['customdata'], list)
    assert len(cds.data['customdata']) == 1
    data = cds.data['customdata'][0]
    assert isinstance(data, np.ndarray)
    assert data.dtype.kind == 'U'
    np.testing.assert_equal(
        data,
        np.array([
            ['2023-01-01 00:00:00'],
            ['2023-01-01 00:01:00'],
            ['2023-01-01 00:02:00']
        ])
    )
