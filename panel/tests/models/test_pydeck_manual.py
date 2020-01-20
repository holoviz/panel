"""In this module we test the PyDeck Bokeh Model

These test can be run partically via pytest and partially by running
`panel serve` on this file and manually verifying the results
"""
import panel as pn
import pydeck as pdk
from panel.models.pydeck import PyDeckPlot
from panel.tests.utils import TestApp

UK_ACCIDENTS_DATA = (
    "https://raw.githubusercontent.com/uber-common/"
    "deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"
)

MAPBOX_KEY = (
    "pk.eyJ1IjoibWFyY3Nrb3ZtYWRzZW4iLCJhIjoiY2s1anMzcG5rMDYzazNvcm10NTFybTE4cSJ9."
    "TV1XBgaMfR-iTLvAXM_Iew"
)


def uk_accidents_deck() -> pdk.Deck:
    """The UK Accidents Deck

    See [PyDec Docs](https://deckgl.readthedocs.io/en/latest/layer.html)

    Returns:
        pdk.Deck: The UK Accidents Deck
    """
    # 2014 location of car accidents in the UK

    # Define a layer to display on a map
    layer = pdk.Layer(
        "HexagonLayer",
        UK_ACCIDENTS_DATA,
        get_position=["lng", "lat",],
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        elevation_range=[0, 3000,],
        extruded=True,
        coverage=1,
    )

    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=-1.415,
        latitude=52.2323,
        zoom=6,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36,
    )

    # Combined all of it and render a viewport
    return pdk.Deck(layers=[layer], initial_view_state=view_state, mapbox_key=MAPBOX_KEY,)


def test_basic():
    """A basic test. We test that

    - json_input
    - mapbox_api_key
    - tooltip

    is shown"""
    deck = uk_accidents_deck()
    plot = PyDeckPlot(
        json_input=deck.to_json(), mapbox_api_key=deck.mapbox_key, tooltip=deck.deck_widget.tooltip,
    )

    return TestApp(test_basic, pn.pane.Bokeh(plot))


def view() -> pn.Column:
    """Wraps all tests in a Column

    Returns:
        pn.Column -- A Column containing all the tests
    """
    return pn.Column(__doc__, test_basic,)


if __name__.startswith("bk"):
    pn.extension()

    view().servable("test_pydeck_manual")
