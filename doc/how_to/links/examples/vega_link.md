# Vega Link

```{pyodide}
import panel as pn

pn.extension('vega', template='bootstrap')
```

This example demonstrates how to link Panel widgets to a Vega pane by editing the Vega spec using callbacks and triggering updates in the plot.

```{pyodide}
imdb = {
  "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
  "data": {"url": "https://raw.githubusercontent.com/vega/vega/master/docs/data/movies.json"},
  "transform": [{
    "filter": {"and": [
      {"field": "IMDB Rating", "valid": True},
      {"field": "Rotten Tomatoes Rating", "valid": True}
    ]}
  }],
  "mark": "rect",
  "width": "container",
  "height": 400,
  "encoding": {
    "x": {
      "bin": {"maxbins":60},
      "field": "IMDB Rating",
      "type": "quantitative"
    },
    "y": {
      "bin": {"maxbins": 40},
      "field": "Rotten Tomatoes Rating",
      "type": "quantitative"
    },
    "color": {
      "aggregate": "count",
      "type": "quantitative"
    }
  },
  "config": {
    "view": {
      "stroke": "transparent"
    }
  }
}

vega = pn.pane.Vega(imdb, height=425)

# Declare range slider to adjust the color limits
color_lims = pn.widgets.RangeSlider(name='Color limits', start=0, end=125, value=(0, 40), step=1)
color_lims.jslink(vega, code={'value': """
target.data.encoding.color.scale = {domain: source.value};
target.properties.data.change.emit()
"""});

# Declare slider to control the number of bins along the x-axis
imdb_bins = pn.widgets.IntSlider(name='IMDB Ratings Bins', start=0, end=125, value=60, step=25)
imdb_bins.jslink(vega, code={'value': """
target.data.encoding.x.bin.maxbins = source.value;
target.properties.data.change.emit()
"""});

# Declare slider to control the number of bins along the y-axis
tomato_bins = pn.widgets.IntSlider(name='Rotten Tomato Ratings Bins', start=0, end=125, value=40, step=25)
tomato_bins.jslink(vega, code={'value': """
target.data.encoding.y.bin.maxbins = source.value;
target.properties.data.change.emit()
"""});

pn.Row(
    vega, pn.Column(color_lims, imdb_bins, tomato_bins)
)
```
