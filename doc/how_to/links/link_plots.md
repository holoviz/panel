# Link Plot Parameters in Javascript

This guide addresses how to link Bokeh and HoloViews plot parameters in Javascript.

```{admonition} Prerequisites
1. The [How to > Link Two Objects in Javascript](./links) guide demonstrates how to use the `.jslink` API to link parameters in Javascript.
```

---

The [How to > Link Two Objects in Javascript](./jslinks) guide demonstrated how to link simple static panes, but links are probably most useful when combined with dynamic objects like plots.

## Link Bokeh plots

The ``jslink`` API trivially allows us to link a parameter on a Panel widget to a Bokeh plot property. Here we create a Bokeh Figure with a simple sine curve. The ``jslink`` method allows us to pass any Bokeh model held by the Figure as the ``target``, then link the widget value to some property on it. E.g. here we link a ``FloatSlider`` value to the ``line_width`` of the ``Line`` glyph:

```{pyodide}
import numpy as np
import panel as pn

from bokeh.plotting import figure

pn.extension()

p = figure(width=300, height=300)
xs = np.linspace(0, 10)
r = p.line(xs, np.sin(xs))

width_slider = pn.widgets.FloatSlider(name='Line Width', start=0.1, end=10)
width_slider.jslink(r.glyph, value='line_width')

pn.Column(width_slider, p)
```

### Link HoloViews plots

Bokeh models allow us to directly access the underlying models and properties, but this access is more indirect when working with HoloViews objects. HoloViews makes various models available directly in the namespace so that they can be accessed for linking:

* **``cds``**: The bokeh ``ColumnDataSource`` model which holds the data used to render the plot
* **``glyph``**: The bokeh ``Glyph`` defining the style of the element
* **``glyph_renderer``**: The Bokeh ``GlyphRenderer`` responsible for rendering the element
* **``plot``**: The bokeh ``Figure``
* **``xaxis``/``yaxis``**: The Axis models of the plot
* **``x_range``/``y_range``**: The x/y-axis ``Range1d`` models defining the axis ranges

All these are made available in the JS code's namespace if we decide to provide a JS code snippet, but can also be referenced in the property mapping. We can map the widget value to a property on the ``glyph`` by providing a specification separated by periods. E.g. in this case we can map the value to the ``glyph.size``:


```{pyodide}
import holoviews as hv
import holoviews.plotting.bokeh

colors = ["black", "red", "blue", "green", "gray"]

size_widget = pn.widgets.FloatSlider(value=8, start=3, end=20, name='Size')
color_widget = pn.widgets.Select(name='Color', options=colors, value='black')

points = hv.Points(np.random.rand(10, 2)).options(padding=0.1, line_color='black')

size_widget.jslink(points, value='glyph.size')
color_widget.jslink(points, value='glyph.fill_color')

pn.Row(points, pn.Column(size_widget, color_widget))
```

Of course, if you need to transform between the displayed widget value and the value to be used on the underlying Bokeh property, you can add custom JS code as shown in [the guide on JS-callbacks](./jscallbacks.md). Together these linking options should allow you to express whatever interactions you wish between your Panel objects.

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
