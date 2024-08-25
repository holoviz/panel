# Build a Custom Leaflet Component

The custom `LeafletHeatMap` component demonstrates a number of concepts. Let us start by defining the component:

```{pyodide}
import param
import pandas as pd
import panel as pn
import numpy as np

from panel.custom import JSComponent

class LeafletHeatMap(JSComponent):

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

    _esm = """
    import L from "https://esm.sh/leaflet@1.7.1"
    import * as Lheat from "https://esm.sh/leaflet.heat@0.2.0"

    function get_records(model) {
      const records = []
      for (let i=0; i<model.data.index.length; i++)
        records.push([model.data[model.y][i], model.data[model.x][i], model.data[model.value][i]])
      return records
    }

    export function render({ model, el }) {
      const map = L.map(el).setView(model.center, model.zoom);

      map.on('change:zoom', () => { model.zoom = map.getZoom() })

      const tileLayer = L.tileLayer(model.tile_url, {
        attribution: model.attribution,
        maxZoom: 21,
        tileSize: 512,
        zoomOffset: -1,
      }).addTo(map)

      model.on("after_render", () => {
        console.log(Lheat)
        map.invalidateSize()
        const data = get_records(model)
        const heatLayer = L.heatLayer(
          data, {
            blur: model.blur,
            radius: model.radius,
            max: 10,
            minOpacity: model.min_alpha
        }).addTo(map)

        model.on(['blur', 'min_alpha', 'radius'], () => {
          heatLayer.setOptions({
            blur: model.blur,
            minOpacity: model.min_alpha,
            radius: model.radius,
          })
        })
        model.on('change:data', () => heatLayer.setLatLngs(get_records(model)))
      })
    }"""

    _stylesheets = ['https://unpkg.com/leaflet@1.7.1/dist/leaflet.css']
```

Some of the concepts this component demonstrates:

- Loading of external libraries, specifically leaflet.js and the leaflet.heat plugin.
- Adding event listeners with `model.on`
- Delaying rendering by defining an `after_render` lifecycle hook.
- Loading of an external stylesheet by including it in the list of `_stylesheets`.

Now let's try this component:

```{pyodide}
pn.extension(template='bootstrap')

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
