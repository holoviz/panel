import numpy as np
import pytest

try:
    import pydeck
except Exception:
    pydeck = None

pydeck_available = pytest.mark.skipif(pydeck is None, reason="requires pydeck")

from bokeh.core.serialization import Serializer

from panel.models.deckgl import DeckGLPlot
from panel.pane import DeckGL, PaneBase, panel


@pydeck_available
def test_get_pydeck_pane_type_from_deck():
    deck = pydeck.Deck()
    assert PaneBase.get_pane_type(deck) is DeckGL


@pydeck_available
def test_pydeck_pane_deck(document, comm):
    deck = pydeck.Deck(tooltip=True, api_keys={'mapbox': 'ABC'})
    pane = panel(deck)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, DeckGLPlot)
    assert pane._models[model.ref["id"]][0] is model
    expected = {
        'mapProvider': 'carto',
        'mapStyle': 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        'views': [{'@@type': 'MapView', 'controller': True}]
    }
    if 'tooltip' in model.data: # Handle pydeck 0.8.0b4
        expected['tooltip'] = True
    assert model.data == expected
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

@pydeck_available
def test_pydeck_mapbox_api_key_issue_5790(document, comm):
    deck_wo_key = pydeck.Deck()
    pane_w_key = DeckGL(deck_wo_key, mapbox_api_key="ABC")

    model = pane_w_key.get_root(document, comm=comm)
    assert model.mapbox_api_key == "ABC"

@pydeck_available
def test_pydeck_no_min_max_zoom_issue_5790(document, comm):
    state_w_no_min_max_zoom = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "zoom": 10,
        "bearing": 0,
        "pitch": 0,
    }
    view_state = pydeck.ViewState(**state_w_no_min_max_zoom)
    deck = pydeck.Deck(initial_view_state=view_state)
    pane = DeckGL(deck)

    model = pane.get_root(document, comm=comm)
    assert model.initialViewState == state_w_no_min_max_zoom

@pydeck_available
def test_pydeck_type_string_can_be_serialized_issue_5790(document, comm):
    serializer = Serializer(references=document.models.synced_references)
    data = [
                {
                    "name": "24th St. Mission (24TH)",
                    "code": "24",
                    "address": "2800 Mission Street, San Francisco CA 94110",
                    "entries": 12817,
                    "exits": 12529,
                    # "coordinates": [-122.418466, 37.752254]
                }
    ]


    layer = pydeck.Layer(
        "TextLayer",
        data,
        get_text_anchor=pydeck.types.String("middle"),
        get_alignment_baseline=pydeck.types.String("center"),
        size_units = pydeck.types.String("meters")   # <--- The key addition to switch to meters as the units.
    )
    deck = pydeck.Deck(layers=[layer])
    pane = DeckGL(deck)

    model = pane.get_root(document, comm=comm)
    serializer.serialize(model)
    assert Serializer._encoders.pop(pydeck.types.String)
