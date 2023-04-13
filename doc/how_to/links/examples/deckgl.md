# Deck.gl JSON Editor

```{pyodide}
import json
import panel as pn

pn.extension('codeeditor', 'deckgl', template='bootstrap')
```

This example demonstrates how to `jslink` a JSON editor to a DeckGL pane to enable super fast, live editing of a plot:

```{pyodide}
MAPBOX_KEY = "pk.eyJ1IjoicGFuZWxvcmciLCJhIjoiY2s1enA3ejhyMWhmZjNobjM1NXhtbWRrMyJ9.B_frQsAVepGIe-HiOJeqvQ"

json_spec = {
    "initialViewState": {
        "bearing": -27.36,
        "latitude": 52.2323,
        "longitude": -1.415,
        "maxZoom": 15,
        "minZoom": 5,
        "pitch": 40.5,
        "zoom": 6
    },
    "layers": [{
        "@@type": "HexagonLayer",
        "autoHighlight": True,
        "coverage": 1,
        "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv",
        "elevationRange": [0, 3000],
        "elevationScale": 50,
        "extruded": True,
        "getPosition": "@@=[lng, lat]",
        "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211", "pickable": True
    }],
    "mapStyle": "mapbox://styles/mapbox/dark-v9",
    "views": [{"@@type": "MapView", "controller": True}]
}


view_editor = pn.widgets.CodeEditor(
    value=json.dumps(json_spec['initialViewState'], indent=4),
    theme= 'monokai', width=500, height=225
)
layer_editor = pn.widgets.CodeEditor(
    value=json.dumps(json_spec['layers'][0], indent=4),
    theme= 'monokai', width=500, height=365
)

deck_gl = pn.pane.DeckGL(json_spec, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_width', height=600)

view_editor.jscallback(args={'deck_gl': deck_gl}, value="deck_gl.initialViewState = JSON.parse(cb_obj.code)")
layer_editor.jscallback(args={'deck_gl': deck_gl}, value="deck_gl.layers = [JSON.parse(cb_obj.code)]")

pn.Row(pn.Column(view_editor, layer_editor), deck_gl).servable()
```
