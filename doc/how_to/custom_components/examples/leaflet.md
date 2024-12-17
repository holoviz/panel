# Build a Custom Leaflet Component

:::{note}
The `LeafletHeatMap` component is defined before the call to `pn.extension` to allow us to load the `_extension_name` and thereby initialize the required JS and CSS resources. Ordinarily the component would be defined in an external module.
:::

```{pyodide}
import param
import pandas as pd
import panel as pn
import numpy as np

from panel.reactive import ReactiveHTML

class LeafletHeatMap(ReactiveHTML):

    attribution = param.String(doc="Tile source attribution.")

    blur = param.Integer(default=18, bounds=(5, 50), doc="Amount of blur to apply to heatmap")

    center = param.XYCoordinates(default=(0, 0), doc="The center of the map.")

    data = param.DataFrame(doc="The heatmap data to plot, should have 'x', 'y' and 'value' columns.")

    tile_url = param.String(doc="Tile source URL with {x}, {y} and {z} parameter")

    min_alpha = param.Number(default=0.2, bounds=(0, 1), doc="Minimum alpha of the heatmap")

    radius = param.Integer(default=25, bounds=(5, 50), doc="The radius of heatmap values on the map")

    x = param.String(default='longitude', doc="Column in the data with longitude coordinates")

    y = param.String(default='latitude', doc="Column in the data with latitude coordinates")

    value = param.String(doc="Column in the data with the data values")

    zoom = param.Integer(default=13, bounds=(0, 21), doc="The plots zoom-level")

    _template = """
    <div id="map" style="width: 100%; height: 100%;"></div>
    """

    _scripts = {
        'get_data': """
            const records = []
            for (let i=0; i<data.data.index.length; i++)
                records.push([data.data[data.y][i], data.data[data.x][i], data.data[data.value][i]])
            return records
        """,
        'render': """
            state.map = L.map(map).setView(data.center, data.zoom);
            state.map.on('zoom', (e) => { data.zoom = state.map.getZoom() })
            state.tileLayer = L.tileLayer(data.tile_url, {
                attribution: data.attribution,
                maxZoom: 21,
                tileSize: 512,
                zoomOffset: -1,
            }).addTo(state.map);
        """,
        'after_layout': """
           state.map.invalidateSize()
           state.heatLayer = L.heatLayer(self.get_data(), {blur: data.blur, radius: data.radius, max: 10, minOpacity: data.min_alpha}).addTo(state.map)
        """,
        'radius': "state.heatLayer.setOptions({radius: data.radius})",
        'blur': "state.heatLayer.setOptions({blur: data.blur})",
        'min_alpha': "state.heatLayer.setOptions({minOpacity: data.min_alpha})",
        'zoom': "state.map.setZoom(data.zoom)",
        'data': 'state.heatLayer.setLatLngs(self.get_data())'
    }

    _extension_name = 'leaflet'

    __css__ = ['https://unpkg.com/leaflet@1.7.1/dist/leaflet.css']

    __javascript__ = [
        'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',
        'https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.min.js'
    ]

pn.extension('leaflet', template='bootstrap')
```

This example demonstrates how to build a custom component wrapping leaflet.js.

```{pyodide}
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"

earthquakes = pd.read_csv(url)

heatmap = LeafletHeatMap(
    attribution='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    data=earthquakes[['longitude', 'latitude', 'mag']],
    min_height=500,
    tile_url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg',
    radius=30,
    sizing_mode='stretch_both',
    value='mag',
    zoom=2,
)

description=pn.pane.Markdown(f'## Earthquakes between {earthquakes.time.min()} and {earthquakes.time.max()}\n\n[Data Source]({url})', sizing_mode="stretch_width")

pn.Column(
    description,
    pn.Row(
        heatmap.controls(['blur', 'min_alpha', 'radius', 'zoom']).servable(target='sidebar'),
        heatmap.servable(),
        sizing_mode='stretch_both'
    ),
    sizing_mode='stretch_both'
)
```
