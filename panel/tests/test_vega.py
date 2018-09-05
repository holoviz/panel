from __future__ import absolute_import

import numpy as np
from bokeh.models import Row as BkRow
from panel.pane import Pane, PaneBase
from panel.vega import Vega, VegaPlot

vega_example = {
    'config': {'view': {'width': 400, 'height': 300}},
    'data': {'values': [{'x': 'A', 'y': 5},
                        {'x': 'B', 'y': 3},
                        {'x': 'C', 'y': 6},
                        {'x': 'D', 'y': 7},
                        {'x': 'E', 'y': 2}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v2.6.0.json'
}


def test_get_vega_pane_type_from_dict():
    assert PaneBase.get_pane_type(vega_example) is Vega


def test_vega_pane(document, comm):
    pane = Pane(vega_example)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})

    assert model.data == expected
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    point_example = dict(vega_example, mark='point')
    point_example['data']['values'][0]['x'] = 'C'
    pane.object = point_example
    point_example['data'].pop('values')
    assert model.data == point_example
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._callbacks == {}
