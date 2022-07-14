import numpy as np
import pytest

try:
    import pydeck
except Exception:
    pydeck = None

pydeck_available = pytest.mark.skipif(pydeck is None, reason="requires pydeck")

from panel.models.deckgl import DeckGLPlot
from panel.pane import DeckGL, Pane, PaneBase


@pydeck_available
def test_get_pydeck_pane_type_from_deck():
    deck = pydeck.Deck()
    assert PaneBase.get_pane_type(deck) is DeckGL


@pydeck_available
def test_pydeck_pane_deck(document, comm):
    deck = pydeck.Deck(tooltip=True, api_keys={'mapbox': 'ABC'})
    pane = Pane(deck)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, DeckGLPlot)
    assert pane._models[model.ref["id"]][0] is model
    assert model.data == {
        'mapProvider': 'carto',
        'mapStyle': 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
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


def test_deckgl_empty_constructor(document, comm):
    pane = DeckGL()

    model = pane.get_root(document, comm)

    assert model.layers == []
    assert model.initialViewState == {}
    assert model.data == {}
    assert model.data_sources == []

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_deckgl_construct_layer(document, comm):
    pane = DeckGL({'layers': [{'data': [{'a': 1, 'b': 2}, {'a': 3, 'b': 7}]}]})

    model = pane.get_root(document, comm)

    assert model.layers == [{'data': 0}]
    assert len(model.data_sources) == 1
    data = model.data_sources[0].data
    assert np.array_equal(data['a'], np.array([1, 3]))
    assert np.array_equal(data['b'], np.array([2, 7]))


def test_deckgl_update_layer(document, comm):
    layer = {'data': [{'a': 1, 'b': 2}, {'a': 3, 'b': 7}]}
    pane = DeckGL({'layers': [layer]})

    model = pane.get_root(document, comm)

    cds = model.data_sources[0]
    old_data = cds.data
    a_vals = cds.data['a']
    layer['data'] = [{'a': 1, 'b': 3}, {'a': 3, 'b': 9}]
    pane.param.trigger('object')

    assert cds.data['a'] is a_vals
    assert cds.data is old_data
    assert np.array_equal(cds.data['b'], np.array([3, 9]))


def test_deckgl_update_layer_columns(document, comm):
    layer = {'data': [{'a': 1, 'b': 2}, {'a': 3, 'b': 7}]}
    pane = DeckGL({'layers': [layer]})

    model = pane.get_root(document, comm)

    cds = model.data_sources[0]
    old_data = cds.data
    layer['data'] = [{'c': 1, 'b': 3}, {'c': 3, 'b': 9}]
    pane.param.trigger('object')

    assert 'a' not in cds.data
    assert cds.data is not old_data
    assert np.array_equal(cds.data['b'], np.array([3, 9]))
    assert np.array_equal(cds.data['c'], np.array([1, 3]))


def test_deckgl_append_layer(document, comm):
    layer = {'data': [{'a': 1, 'b': 2}, {'a': 3, 'b': 7}]}
    pane = DeckGL({'layers': [layer]})

    model = pane.get_root(document, comm)

    pane.object['layers'].append({'data': [{'c': 1, 'b': 3}, {'c': 3, 'b': 9}]})
    pane.param.trigger('object')

    assert len(model.layers) == 2
    assert len(model.data_sources) == 2
    cds1, cds2 = model.data_sources
    old_data = cds1.data
    a_vals, b_vals = old_data['a'], old_data['b']
    layer1, layer2 = model.layers
    assert layer1['data'] == 0
    assert layer2['data'] == 1

    assert cds1.data is old_data
    assert cds1.data['a'] is a_vals
    assert cds1.data['b'] is b_vals
    assert np.array_equal(cds2.data['b'], np.array([3, 9]))
    assert np.array_equal(cds2.data['c'], np.array([1, 3]))


def test_deckgl_insert_layer(document, comm):
    layer = {'data': [{'a': 1, 'b': 2}, {'a': 3, 'b': 7}]}
    pane = DeckGL({'layers': [layer]})

    model = pane.get_root(document, comm)

    pane.object['layers'].insert(0, {'data': [{'c': 1, 'b': 3}, {'c': 3, 'b': 9}]})
    pane.param.trigger('object')

    assert len(model.layers) == 2
    assert len(model.data_sources) == 2
    cds1, cds2 = model.data_sources
    old_data = cds1.data
    a_vals, b_vals = old_data['a'], old_data['b']
    layer1, layer2 = model.layers
    assert layer1['data'] == 1
    assert layer2['data'] == 0

    assert cds1.data is old_data
    assert cds1.data['a'] is a_vals
    assert cds1.data['b'] is b_vals
    assert np.array_equal(cds2.data['b'], np.array([3, 9]))
    assert np.array_equal(cds2.data['c'], np.array([1, 3]))
