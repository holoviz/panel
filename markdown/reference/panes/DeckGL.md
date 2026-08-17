# DeckGL
---
```python
import panel as pn
import pydeck as pdk
pn.extension('deckgl')
```

[Deck.gl](https://deck.gl/#/) is a very powerful WebGL-powered framework for visual exploratory data analysis of large datasets. The `DeckGL` *pane* renders JSON Deck.gl JSON specification as well as `PyDeck` plots inside a panel. If data is encoded in the deck.gl layers the pane will extract the data and send it across the websocket in a binary format speeding up rendering.

The `PyDeck` *package* provides Python bindings. Please follow the [installation instructions](https://github.com/uber/deck.gl/blob/master/bindings/pydeck/README.md) closely to get it working in this Jupyter Notebook.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``mapbox_api_key``** (string): The MapBox API key if not supplied by a PyDeck object.
* **``object``** (object, dict or string): The deck.GL JSON or PyDeck object being displayed
* **``tooltips``** (bool or dict, default=True): Whether to enable tooltips or custom tooltip formatters
* **``throttle``** (dict, default={'view': 200, 'hover': 200}): Throttling timeouts (in milliseconds) for view state and hover events.

In addition to parameters which control how the object is displayed the DeckGL pane also exposes a number of parameters which receive updates from the plot:

* **``click_state``** (dict): Contains the last click event on the DeckGL plot.
* **``hover_state``** (dict): Contains information about the current hover location on the DeckGL plot.
* **``view_state``** (dict): Contains information about the current view port of the DeckGL plot.

____

In order to use Deck.gl you need a MAP BOX Key which you can acquire for free for limited use at [mapbox.com](https://account.mapbox.com/access-tokens/).

Now we can define a JSON spec and pass it to the DeckGL pane along with the Mapbox key (if you have one):

```python
MAPBOX_KEY = ""

if MAPBOX_KEY:
    map_style = "mapbox://styles/mapbox/dark-v9"
else:
    map_style = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

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
        "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211",
        "pickable": True
    }],
    "mapStyle": map_style,
    "views": [
        {"@@type": "MapView", "controller": True}
    ]
}

deck_gl = pn.pane.DeckGL(json_spec, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_width', height=600)

deck_gl
```

If you do not have a Mapbox API key you can use one of the [Carto basemaps](https://deck.gl/docs/api-reference/carto/basemap#supported-basemaps).

Like other panes the DeckGL object can be replaced or updated. In this example we will change the `colorRange` of the HexagonLayer and then trigger an update:

```python
COLOR_RANGE = [
      [1, 152, 189],
      [73, 227, 206],
      [216, 254, 181],
      [254, 237, 177],
      [254, 173, 84],
      [209, 55, 78]
]

json_spec['layers'][0]['colorRange'] = COLOR_RANGE

deck_gl.param.trigger('object')
```

## Tooltips

By default tooltips can be disabled and enabled by setting `tooltips=True/False`. For more customization it is possible to pass in a dictionary defining the formatting. Let us start by declaring a plot with two layers:

```python
DATA_URL = 'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/geojson/vancouver-blocks.json'

LAND_COVER = [[[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]]

json_spec = {
    "initialViewState": {
      'latitude': 49.254,
      'longitude': -123.13,
      'zoom': 11,
      'maxZoom': 16,
      'pitch': 45,
      'bearing': 0
    },
    "layers": [{
        '@@type': 'GeoJsonLayer',
        'id': 'geojson',
        'data': DATA_URL,
        'opacity': 0.8,
        'stroked': True,
        'filled': True,
        'extruded': True,
        'wireframe': True,
        'fp64': True,
        'getLineColor': [255, 255, 255],
        'getElevation': "@@=properties.valuePerSqm / 20",
        'getFillColor': "@@=[255, 255, properties.growth * 255]",
        'pickable': True,
    }, {
        '@@type': 'PolygonLayer',
        'id': 'landcover',
        'data': LAND_COVER,
        'stroked': True,
        'pickable': True,
        # processes the data as a flat longitude-latitude pair
        'getPolygon': '@@=-',
        'getFillColor': [0, 0, 0, 20]
    }],
    "mapStyle": map_style,
    "views": [
        {"@@type": "MapView", "controller": True}
    ]
}
```

We have explicitly given these layers the `id` `'landcover'` and `'geojson'`. Ordinarily we wouldn't enable `pickable` property on the 'landcover' polygon and if we only have a single `pickable` layer it is sufficient to declare a tooltip like this:

```python
geojson_tooltip = {
    "html": """
      <b>Value per Square meter:</b> {properties.valuePerSqm}<br>
      <b>Growth:</b> {properties.growth}
    """,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}
```

Here we created an HTML template which is populated by the `properties` in the GeoJSON and then has the `style` applied. In general the dictionary may contain:

- `html` - Set the innerHTML of the tooltip.

- `text` - Set the innerText of the tooltip.

- `style` - A dictionary of CSS styles that will modify the default style of the tooltip.

If we have multiple pickable layers we can declare distinct tooltips by nesting the tooltips dictionary, indexed by the layer `id` or the index of the layer in the list of layers (note that the dictionary must be either integer indexed or string indexed not both).

```python
tooltip = {
    "geojson": geojson_tooltip,
    "landcover": {
        "html": "The background",
        "style": {
            "backgroundColor": "red",
            "color": "white"
       }
    }
}

pn.pane.DeckGL(json_spec, tooltips=tooltip, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_width', height=600)
```

When hovering on the area around Vancouver you should now see a tooltip saying `'The background'` colored red, while the hover tooltip should show information about each property when hovering over one of the property polygons.

### PyDeck

Instead of writing out raw JSON-like dictionaries the `DeckGL` pane may also be given a PyDeck object to render:

```python
import pydeck

DATA_URL = "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/geojson/vancouver-blocks.json"

LAND_COVER = [[[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]]

INITIAL_VIEW_STATE = pydeck.ViewState(
  latitude=49.254,
  longitude=-123.13,
  zoom=11,
  max_zoom=16,
  pitch=45,
  bearing=0
)

polygon = pydeck.Layer(
    'PolygonLayer',
    LAND_COVER,
    stroked=False,
    # processes the data as a flat longitude-latitude pair
    get_polygon='-',
    get_fill_color=[0, 0, 0, 20]
)

geojson = pydeck.Layer(
    'GeoJsonLayer',
    DATA_URL,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation='properties.valuePerSqm / 20',
    get_fill_color='[255, 255, properties.growth * 255]',
    get_line_color=[255, 255, 255],
    pickable=True
)

r = pydeck.Deck(
    api_keys={'mapbox': MAPBOX_KEY},
    layers=[polygon, geojson],
    map_style=map_style,
    initial_view_state=INITIAL_VIEW_STATE
)

# Tooltip (you can get the id directly from the layer object)
tooltips = {geojson.id: geojson_tooltip}

pn.pane.DeckGL(r, sizing_mode='stretch_width', tooltips=tooltips, height=600)
```

Note that when specifying tooltips using pydeck you must also reference any data fields using the `{properties.<DATA_FIELD_NAME>}` syntax.

## Controls

The `DeckGL` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
deck_gl_example = pn.pane.DeckGL(r, sizing_mode='stretch_width', tooltips=tooltips, height=600)

pn.Row(deck_gl_example.controls(), deck_gl_example)
```

---
