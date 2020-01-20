"""In this module we test the PyDeck Bokeh Model"""

import pytest
from panel.models.pydeck import PyDeckPlot

# from pydeck import pdk

# pylint: disable=line-too-long
@pytest.fixture
def json_input() -> str:
    return '{"initialViewState": {"bearing": -27.36, "latitude": 52.2323, "longitude": -1.415, "maxZoom": 15, "minZoom": 5, "pitch": 40.5, "zoom": 6}, "layers": [{"@@type": "HexagonLayer", "autoHighlight": true, "coverage": 1, "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv", "elevationRange": [0, 3000], "elevationScale": 50, "extruded": true, "getPosition": "@@=[lng, lat]", "id": "18a4e022-062c-428f-877f-c8c089472297", "pickable": true}], "mapStyle": "mapbox://styles/mapbox/dark-v9", "views": [{"@@type": "MapView", "controller": true}]}'


# pylint: enable=line-too-long


@pytest.fixture
def mapbox_api_key() -> str:
    return (
        "pk.eyJ1IjoibWFyY3Nrb3ZtYWRzZW4iLCJhIjoiY2s1anMzcG5rMDYzazNvcm10NTFybTE4cSJ9."
        "TV1XBgaMfR-iTLvAXM_Iew"
    )


@pytest.fixture
def tooltip() -> bool:
    return True


# @pytest.fixture
# def uk_accidents_deck() -> pdk.Deck:
#     """The UK Accidents Deck

#     See [PyDec Docs](https://deckgl.readthedocs.io/en/latest/layer.html)

#     Returns:
#         pdk.Deck: The UK Accidents Deck
#     """
#     # 2014 location of car accidents in the UK

#     # Define a layer to display on a map
#     layer = pdk.Layer(
#         "HexagonLayer",
#         UK_ACCIDENTS_DATA,
#         get_position=["lng", "lat",],
#         auto_highlight=True,
#         elevation_scale=50,
#         pickable=True,
#         elevation_range=[0, 3000,],
#         extruded=True,
#         coverage=1,
#     )

#     # Set the viewport location
#     view_state = pdk.ViewState(
#         longitude=-1.415,
#         latitude=52.2323,
#         zoom=6,
#         min_zoom=5,
#         max_zoom=15,
#         pitch=40.5,
#         bearing=-27.36,
#     )

#     # Combined all of it and render a viewport
#     return pdk.Deck(layers=[layer], initial_view_state=view_state, mapbox_key=MAPBOX_KEY,)


def test_constructor(json_input, mapbox_api_key, tooltip):
    # When
    actual = PyDeckPlot(json_input=json_input, mapbox_api_key=mapbox_api_key, tooltip=tooltip,)
    # Then
    assert actual.json_input == json_input
    assert actual.mapbox_api_key == mapbox_api_key
    assert actual.tooltip == tooltip
