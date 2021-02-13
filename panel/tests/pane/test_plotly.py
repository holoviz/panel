import datetime as dt

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
    assert model.data_sources[0].data['x'][0].dtype.kind in 'SU'


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
    model.sizing_mode == 'stretch_both'

    pane.object['layout']['autosize'] = False
    pane.param.trigger('object')
    model.sizing_mode == 'fixed'

    pane._cleanup(model)
    
    pane = Plotly(dict(data=[trace], layout={'autosize': True}), sizing_mode='fixed')
    model = pane.get_root(document, comm=comm)
    model.sizing_mode == 'fixed'

    pane._cleanup(model)
