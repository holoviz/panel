from __future__ import absolute_import

import pytest

try:
    import plotly
    import plotly.graph_objs as go
except:
    plotly = None
plotly_available = pytest.mark.skipif(plotly is None, reason="requires plotly")

import numpy as np
from bokeh.models import Row as BkRow
from panel.pane import Pane, PaneBase
from panel.plotly import Plotly, PlotlyPlot


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
    pane = Pane(trace, layout={'width': 350})

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, PlotlyPlot)
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    assert len(model.data['data']) == 1
    assert model.data['data'][0]['type'] == 'scatter'
    assert model.data['data'][0]['x'] == [0, 1]
    assert model.data['data'][0]['y'] == [2, 3]
    assert model.data['layout'] == {'width': 350}
    assert len(model.data_sources) == 1
    assert model.data_sources[0].data == {}

    # Replace Pane.object
    new_trace = go.Bar(x=[2, 3], y=[4, 5])
    pane.object = new_trace
    assert row.children[0] is model
    assert len(model.data['data']) == 1
    assert model.data['data'][0]['type'] == 'bar'
    assert model.data['data'][0]['x'] == [2, 3]
    assert model.data['data'][0]['y'] == [4, 5]
    assert model.data['layout'] == {'width': 350}
    assert len(model.data_sources) == 1
    assert model.data_sources[0].data == {}
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}


@plotly_available
def test_plotly_pane_numpy_to_cds_traces(document, comm):
    trace = go.Scatter(x=np.array([1, 2]), y=np.array([2, 3]))
    pane = Pane(trace, layout={'width': 350})

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, PlotlyPlot)
    assert row.ref['id'] in pane._callbacks
    assert len(model.data['data']) == 1
    assert model.data['data'][0]['type'] == 'scatter'
    assert 'x' not in model.data['data'][0]
    assert 'y' not in model.data['data'][0]
    assert model.data['layout'] == {'width': 350}
    assert len(model.data_sources) == 1
    cds = model.data_sources[0]
    assert np.array_equal(cds.data['x'], np.array([1, 2]))
    assert np.array_equal(cds.data['y'], np.array([2, 3]))

    # Replace Pane.object
    new_trace = [go.Scatter(x=np.array([5, 6]), y=np.array([6, 7])),
                 go.Bar(x=np.array([2, 3]), y=np.array([4, 5]))]
    pane.object = new_trace
    assert row.children[0] is model
    assert len(model.data['data']) == 2
    assert model.data['data'][0]['type'] == 'scatter'
    assert 'x' not in model.data['data'][0]
    assert 'y' not in model.data['data'][0]
    assert model.data['data'][1]['type'] == 'bar'
    assert 'x' not in model.data['data'][1]
    assert 'y' not in model.data['data'][1]
    assert model.data['layout'] == {'width': 350}
    assert len(model.data_sources) == 2
    cds = model.data_sources[0]
    assert np.array_equal(cds.data['x'], np.array([5, 6]))
    assert np.array_equal(cds.data['y'], np.array([6, 7]))
    cds2 = model.data_sources[1]
    assert np.array_equal(cds2.data['x'], np.array([2, 3]))
    assert np.array_equal(cds2.data['y'], np.array([4, 5]))
    assert row.ref['id'] in pane._callbacks

    # Cleanup
    pane._cleanup(row, True)
    assert pane._callbacks == {}
