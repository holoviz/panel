from copy import deepcopy

import pytest

from packaging.version import Version

try:
    import altair as alt
    altair_version = Version(alt.__version__)
except Exception:
    alt = None  # type: ignore

altair_available = pytest.mark.skipif(alt is None, reason="requires altair")

import numpy as np
import pandas as pd

import panel as pn

from panel.models.vega import VegaPlot
from panel.pane import PaneBase, Vega

blank_schema = {'$schema': ''}

vega4_config = {'view': {'continuousHeight': 300, 'continuousWidth': 400}}
vega5_config = {'view': {'continuousHeight': 300, 'continuousWidth': 300}}

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

vega_df_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': pd.DataFrame({'x': ['A', 'B', 'C', 'D', 'E'], 'y': [5, 3, 6, 7, 2]})},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}

vega4_selection_example = {
    'config': {'view': {'continuousWidth': 300, 'continuousHeight': 300}},
    'data': {'url': 'https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json'},
    'mark': {'type': 'point'},
    'encoding': {
        'color': {
            'condition': {
                'selection': 'brush',
                'field': 'Species',
                'type': 'nominal'
            },
            'value': 'lightgray'},
        'x': {
            'field': 'Beak Length (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'
        },
        'y': {
            'field': 'Beak Depth (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'}
    },
    'height': 250,
    'selection': {'brush': {'type': 'interval'}},
    'width': 250,
    '$schema': 'https://vega.github.io/schema/vega-lite/v4.17.0.json'
}

vega5_selection_example = {
    'config': {'view': {'continuousWidth': 300, 'continuousHeight': 300}},
    'data': {'url': 'https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json'},
    'mark': {'type': 'point'},
    'encoding': {
        'color': {
            'condition': {
                'param': 'brush',
                'field': 'Species',
                'type': 'nominal'
            },
            'value': 'lightgray'},
        'x': {
            'field': 'Beak Length (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'
        },
        'y': {
            'field': 'Beak Depth (mm)',
            'scale': {'zero': False},
            'type': 'quantitative'}
    },
    'height': 250,
    'params': [{'name': 'brush', 'select': {'type': 'interval'}}],
    'width': 250,
    '$schema': 'https://vega.github.io/schema/vega-lite/v5.6.1.json'
}

vega_inline_example = {
    'config': {
        'view': {'width': 400, 'height': 300},
        'mark': {'tooltip': None}},
    'data': {'name': 'data-2f2c0ff233b8675aa09202457ebe7506',
             'format': {'property': 'features', 'type': 'json'}},
    'mark': 'geoshape',
    'encoding': {
        'color': {
            'type': 'quantitative',
            'field': 'properties.percent_no_internet'
        }
    },
    'projection': {'type': 'albersUsa'},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json',
    'datasets': {
        'data-2f2c0ff233b8675aa09202457ebe7506': {
            'type': 'FeatureCollection',
            'features': [
                {'id': '0',
                 'type': 'Feature',
                 'properties': {
                     'name': 'Autauga County, Alabama',
                     'percent_no_internet': 0.2341122827016244,
                     'percent_no_internet_normalized': 0.2589760005042632},
                 'geometry': {
                     'type': 'Polygon',
                     'coordinates': [[[-86.411786, 32.706342],
                                      [-86.411786, 32.410587],
                                      [-86.499417, 32.344863],
                                      [-86.817079, 32.339387],
                                      [-86.915664, 32.662526],
                                      [-86.411786, 32.706342]]]
                 }
                }
            ]
        }
    }
}

gdf_example = {
    'config': {'view': {'continuousWidth': 400, 'continuousHeight': 300}},
    'data': {'name': 'data-778223ce4ff5da49611148b060c0cd3d'},
    'mark': {'type': 'geoshape', 'fill': 'lightgray', 'stroke': 'white'},
    'height': 600,
    'projection': {'reflectY': True, 'type': 'identity'},
    'width': 800,
    '$schema': 'https://vega.github.io/schema/vega-lite/v4.0.0.json',
    'datasets': {
        'data-778223ce4ff5da49611148b060c0cd3d': [
            {
                'bid': 'SR01-01',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[120.0, 855.0],
                         [120.0, 925.0],
                         [20.0, 925.0],
                         [20.0, 855.0],
                         [120.0, 855.0]]
                    ]
                }
            },
            {
                'bid': 'SR02-02',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[120.0, 940.0],
                         [120.0, 1010.0],
                         [20.0, 1010.0],
                         [20.0, 940.0],
                         [120.0, 940.0]]
                    ]
                }
            },
            {
                'bid': 'SR03-03',
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [[240.0, 940.0],
                         [240.0, 1010.0],
                         [140.0, 1010.0],
                         [140.0, 940.0],
                         [240.0, 940.0]]
                    ]
                }
            }
        ]
    }
}

def test_get_vega_pane_type_from_dict():
    assert PaneBase.get_pane_type(vega_example) is Vega


@pytest.mark.parametrize('example', [vega_example, vega_df_example])
def test_vega_pane(document, comm, example):
    pane = pn.panel(example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})

    assert dict(model.data, **blank_schema) == dict(expected, **blank_schema)
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    point_example = dict(deepcopy(vega_example), mark='point')
    point_example['data']['values'][0]['x'] = 'C'
    pane.object = point_example
    point_example = dict(point_example, data={})
    assert model.data == point_example
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}


def test_vega_geometry_data(document, comm):
    pane = pn.panel(gdf_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    # Ensure geometries are not packed into CDS
    assert model.data_sources == {}


def test_vega_pane_inline(document, comm):
    pane = pn.panel(vega_inline_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    assert dict(model.data, **blank_schema) == dict(vega_inline_example, **blank_schema)
    assert model.data_sources == {}

    pane._cleanup(model)
    assert pane._models == {}


def test_vega_lite_4_selection_spec(document, comm):
    vega = Vega(vega4_selection_example)
    assert vega._selections == {'brush': 'interval'}

def test_vega_lite_5_selection_spec(document, comm):
    vega = Vega(vega5_selection_example)
    assert vega._selections == {'brush': 'interval'}

def altair_example():
    import altair as alt
    data = alt.Data(values=[{'x': 'A', 'y': 5},
                            {'x': 'B', 'y': 3},
                            {'x': 'C', 'y': 6},
                            {'x': 'D', 'y': 7},
                            {'x': 'E', 'y': 2}])
    chart = alt.Chart(data).mark_bar().encode(
        x='x:O',  # specify ordinal data
        y='y:Q',  # specify quantitative data
    )
    return chart

@altair_available
def test_get_vega_pane_type_from_altair():
    assert PaneBase.get_pane_type(altair_example()) is Vega

@altair_available
def test_altair_pane(document, comm):
    pane = Vega(altair_example())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})
    if altair_version >= Version('5.0.0rc1'):
        expected['mark'] = {'type': 'bar'}
        expected['config'] = vega5_config
    elif altair_version >= Version('4.0.0'):
        expected['config'] = vega4_config
    assert dict(model.data, **blank_schema) == dict(expected, **blank_schema)

    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    chart = altair_example()
    chart.mark = 'point'
    chart.data.values[0]['x'] = 'C'
    pane.object = chart
    point_example = dict(vega_example, data={},  mark='point')
    if altair_version >= Version('5.0.0rc1'):
        point_example['mark'] = {'type': 'point'}
        point_example['config'] = vega5_config
    elif altair_version >= Version('4.0.0'):
        point_example['config'] = vega4_config
    assert dict(model.data, **blank_schema) == dict(point_example, **blank_schema)
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E']))
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}

def test_vega_can_instantiate_empty_with_sizing_mode(document, comm):
    pane = Vega(sizing_mode="stretch_width")
    pane.get_root(document, comm=comm)
