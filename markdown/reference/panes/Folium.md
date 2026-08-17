# Folium
---
```python
import folium
import panel as pn

pn.extension(sizing_mode="stretch_width")
```

The ``Folium`` pane renders [folium](http://python-visualization.github.io/folium/) interactive maps.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (object): The Folium object being displayed
___

The `Folium` pane uses the built-in HTML representation provided by `folium` to render the map:

```python
m = folium.Map(location=[52.51, 13.39], zoom_start=12)

folium_pane = pn.pane.plot.Folium(m, height=400)

folium_pane
```

Like any other pane, the `Folium` pane's view can be updated by setting the `object` parameter:

```python
# Add a marker to the map
folium.Marker(
    [52.516, 13.381], popup="<i>Brandenburg Gate</i>", tooltip="Click me!"
).add_to(m)

folium_pane.object = m
```

---
