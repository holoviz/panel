# Bokeh
---
```python
import panel as pn
import numpy as np
import pandas as pd

pn.extension()
```

The ``Bokeh`` pane allows displaying any displayable [Bokeh](http://bokeh.org) model inside a Panel app. Since Panel is built on Bokeh internally, the Bokeh model is simply inserted into the plot. Since Bokeh models are ordinarily only displayed once, some Panel-related functionality such as syncing multiple views of the same model may not work. Nonetheless this pane type is very useful for combining raw Bokeh code with the higher-level Panel API.

When working in a notebook any changes to a Bokeh objects may not be synced automatically requiring an explicit call to `pn.state.push_notebook` with the Panel component containing the Bokeh object.

#### Parameters:
For the ``theme`` parameter, see the [bokeh themes docs](https://docs.bokeh.org/en/latest/docs/reference/themes.html).

* **``object``** (bokeh.layouts.LayoutDOM): The Bokeh model to be displayed
* **``theme``** (bokeh.themes.Theme): The Bokeh theme to apply

___

```python
from math import pi

from bokeh.palettes import Category20c, Category20
from bokeh.plotting import figure
from bokeh.transform import cumsum

x = {
    'United States': 157,
    'United Kingdom': 93,
    'Japan': 89,
    'China': 63,
    'Germany': 44,
    'India': 42,
    'Italy': 40,
    'Australia': 35,
    'Brazil': 32,
    'France': 31,
    'Taiwan': 31,
    'Spain': 29
}

data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
data['angle'] = data['value']/data['value'].sum() * 2*pi
data['color'] = Category20c[len(x)]

p = figure(height=350, title="Pie Chart", toolbar_location=None,
           tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

r = p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='country', source=data)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

bokeh_pane = pn.pane.Bokeh(p, theme="dark_minimal")
bokeh_pane
```

To update a plot with a live server, we can simply modify the underlying model. If we are working in a Jupyter notebook we also have to call the `pn.io.push_notebook` helper function on the component or explicitly trigger an event with `bokeh_pane.param.trigger('object')`:

```python
r.data_source.data['color'] = Category20[len(x)]
pn.io.push_notebook(bokeh_pane)
```

Alternatively the model may also be replaced entirely, in a live server:

```python
from bokeh.models import Div

bokeh_pane.object = Div(text='<h2>This text replaced the pie chart</h2>')
```

The other nice feature when using Panel to render bokeh objects is that callbacks will work just like they would on the server. So you can simply wrap your existing bokeh app in Panel and it will render and work out of the box both in the notebook and when served as a standalone app:

```python
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))

# Set up plot
plot = figure(height=400, width=400, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4*np.pi, N)
    y = a*np.sin(k*x + w) + b

    source.data = dict(x=x, y=y)

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(text, offset, amplitude, phase, freq)

bokeh_app = pn.pane.Bokeh(row(inputs, plot, width=800))

bokeh_app
```

### Controls

The `Bokeh` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(bokeh_app.controls(jslink=True), bokeh_app)
```

---
