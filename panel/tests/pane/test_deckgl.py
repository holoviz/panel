import pytest

try:
    import pydeck
except Exception:
    pydeck = None

pydeck_available = pytest.mark.skipif(pydeck is None, reason="requires pydeck")

from panel.models.deckgl import DeckGLPlot
from panel.pane import Pane, PaneBase, DeckGL


@pydeck_available
def test_get_pydeck_pane_type_from_deck():
    deck = pydeck.Deck()
    assert PaneBase.get_pane_type(deck) is DeckGL


@pydeck_available
def test_pydeck_pane_deck(document, comm):
    deck = pydeck.Deck(tooltip=True, mapbox_key='ABC')
    pane = Pane(deck)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, DeckGLPlot)
    assert pane._models[model.ref["id"]][0] is model
    assert model.data == {
        'description': None,
        'mapStyle': 'mapbox://styles/mapbox/dark-v9',
        'views': [{'@@type': 'MapView', 'controller': True}]
    }
    assert model.mapbox_api_key == deck.mapbox_key
    assert model.tooltip == deck.deck_widget.tooltip

    # Replace Pane.object
    new_deck = pydeck.Deck(tooltip=False)
    pane.object = new_deck

    assert pane._models[model.ref["id"]][0] is model
    assert model.tooltip == new_deck.deck_widget.tooltip

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
