"""In this module we test the DeckGL Bokeh Model"""

import json

import pytest

from panel.models.deckgl import DeckGLPlot


@pytest.fixture
def json_input():
    return ('{"initialViewState": {"bearing": -27.36, "latitude": 52.2323, '
            '"longitude": -1.415, "maxZoom": 15, "minZoom": 5, "pitch": 40.5, '
            '"zoom": 6}, "layers": [{"@@type": "HexagonLayer", "autoHighlight": '
            'true, "coverage": 1, "data": "https://raw.githubusercontent.com/'
            'uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv", '
            '"elevationRange": [0, 3000], "elevationScale": 50, "extruded": true, '
            '"getPosition": "@@=[lng, lat]", "id": "18a4e022-062c-428f-877f-c8c089472297", '
            '"pickable": true}], "mapStyle": "mapbox://styles/mapbox/dark-v9", '
            '"views": [{"@@type": "MapView", "controller": true}]}')


@pytest.fixture
def mapbox_api_key():
    return (
        "pk.eyJ1IjoibWFyY3Nrb3ZtYWRzZW4iLCJhIjoiY2s1anMzcG5rMDYzazNvcm10NTFybTE4cSJ9."
        "TV1XBgaMfR-iTLvAXM_Iew"
    )


@pytest.fixture
def tooltip():
    return True


def test_constructor(json_input, mapbox_api_key, tooltip):
    # When
    data = json.loads(json_input)
    layers = data.pop('layers')
    view_state = data.pop('initialViewState')
    actual = DeckGLPlot(data=data, layers=layers, initialViewState=view_state,
                        mapbox_api_key=mapbox_api_key, tooltip=tooltip,)
    # Then
    assert actual.data == data
    assert actual.layers == layers
    assert actual.initialViewState == view_state
    assert actual.mapbox_api_key == mapbox_api_key
    assert actual.tooltip == tooltip
