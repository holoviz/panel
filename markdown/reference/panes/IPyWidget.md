# IPyWidget
---
```python
import numpy as np
import panel as pn
import ipywidgets as ipw

pn.extension('ipywidgets')
```

The ``IPyWidget`` pane renders any ipywidgets model both in the notebook and in a deployed server. This makes it possible to leverage this growing ecosystem directly from within Panel simply by wrapping the component in a Pane or Panel.

In the notebook this is not necessary since Panel simply uses the regular notebook ipywidget renderer. Particularly in JupyterLab importing the ipywidgets extension in this way may interfere with the UI and render the JupyterLab UI unusable, so enable the extension with care.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (object): The ipywidget object being displayed

##### Display

* **``default_layout``** (pn.layout.Panel, default=Row): Layout to wrap the plot and widgets in

___

The `panel` function will automatically convert any ``ipywidgets`` object into a displayable panel, while keeping all of its interactive features:

```python
date   = ipw.DatePicker(description='Date')
slider = ipw.FloatSlider(description='Float')
play   = ipw.Play()

layout = ipw.HBox(children=[date, slider, play])

pn.panel(layout)
```

### Interactivity and callbacks

Any ipywidget with a `value` parameter can also be used in a `pn.depends` decorated callback, e.g. here we declare a function that depends on the value of a `FloatSlider`:

```python
slider = ipw.IntSlider(description='Slider', min=-5, max=5)

def cb(value):
    return 'The slider value is ' + (
        'negative' if value < 0 else 'nonnegative'
    )

pn.Row(slider, pn.bind(cb, slider))
```

If instead you want to write a callback yourself you can also use the `traitlets` `observe` method as you would usually. To read more about this see the [Widget Events](https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Events.html) section of the ipywidgets documentation.

```python
caption = ipw.Label(value='The slider value is nonnegative')
slider = ipw.IntSlider(min=-5, max=5, value=1, description='Slider')

def handle_slider_change(change):
    caption.value = 'The slider value is ' + (
        'negative' if change.new < 0 else 'nonnegative'
    )

slider.observe(handle_slider_change, names='value')

pn.Row(slider, caption)
```

### External widget libraries

The `IPyWidget` panel is also not restricted to simple widgets, ipywidget libraries such as `ipyvolume` and `ipyleaflet` are also supported.

```python
import ipyvolume as ipv
x, y, z, u, v = ipv.examples.klein_bottle(draw=False)
fig = ipv.figure()
m = ipv.plot_mesh(x, y, z, wireframe=False)
ipv.squarelim()

pn.panel(fig)
```

```python
from ipyleaflet import Map, VideoOverlay

m = Map(center=(25, -115), zoom=4)

video = VideoOverlay(
    url="https://www.mapbox.com/bites/00188/patricia_nasa.webm",
    bounds=((13, -130), (32, -100))
)

m.add(video);

pn.panel(m)
```

## Limitations

The ipywidgets support has some limitations because it is integrating two very distinct ecosystems. In particular it is not yet possible to set up JS-linking between a Panel and an ipywidget object or support for embedding. These limitations are not fundamental technical limitations and may be solved in future.

---
