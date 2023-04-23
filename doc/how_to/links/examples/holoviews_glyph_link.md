# HoloViews Glyph Link

```{pyodide}
import numpy as np
import panel as pn

import holoviews as hv
import holoviews.plotting.bokeh

pn.extension()
```

HoloViews-generated Bokeh plots can be statically linked to widgets that control their properties, allowing you to export static HTML files that allow end-user customization of appearance.

```{pyodide}
from bokeh.core.enums import MarkerType

colors = ["black", "red", "blue", "green", "gray"]
markers = list(MarkerType)

# Define widget for properties we want to change
alpha_widget = pn.widgets.FloatSlider(value=0.5, start=0, end=1, name='Alpha')
size_widget = pn.widgets.FloatSlider(value=12, start=3, end=20, name='Size')
color_widget = pn.widgets.ColorPicker(value='#f80000', name='Color')
marker_widget = pn.widgets.Select(options=markers, value='circle', name='Marker')

# Declare a Points object and apply some options
points = hv.Points(np.random.randn(200, 2)).options(
    padding=0.1, height=500, line_color='black', responsive=True)

# Link the widget value parameter to the property on the glyph
alpha_widget.jslink(points, value='glyph.fill_alpha')
size_widget.jslink(points, value='glyph.size')
color_widget.jslink(points, value='glyph.fill_color')
marker_widget.jslink(points, value='glyph.marker')

pn.Row(pn.Column(alpha_widget, color_widget, marker_widget, size_widget), points).servable()
```
