# Add or Remove Components

## Row & Column

Manipulate the components in a ``Row`` and ``Column`` ``Panel``s just like a Python list. To start, we will declare a ``Column`` and populate it with some text and a widget:

```{pyodide}
import panel as pn
pn.extension()

column = pn.Column('# some text', pn.widgets.FloatSlider())

column
```

Next we add another bit of markdown:

```{pyodide}
column.append('* Item 1\n* Item 2')

column
```

Then we add a few more widgets:

```{pyodide}
column.extend([pn.widgets.TextInput(), pn.widgets.Checkbox(name='Tick this!')])

column
```

Finally, we change our mind and replace the ``Checkbox`` with a button:

```{pyodide}
column[4] = pn.widgets.Button(name='Click here')

column
```

## Tabs

Just like ``Column``, ``Tabs`` components can be changed like a Python list. However, when adding or replacing items, it is also possible to pass a tuple providing a custom title for the tab. First, create a ``Tabs`` panel that contains a plot:

```{pyodide}
from bokeh.plotting import figure

p1 = figure(width=300, height=300)
p1.line([1, 2, 3], [1, 2, 3])

tabs = pn.Tabs(p1)

tabs
```

Then, add a new tab for a slider widget and include a title for this new tab:

```{pyodide}
tabs.append(('Slider', pn.widgets.FloatSlider()))

tabs
```

Finally, add multiple additional tabs at once using `.extend`, passing titles for each:

```{pyodide}
tabs.extend([
    ('Text', pn.widgets.TextInput()),
    ('Color', pn.widgets.ColorPicker())
])

tabs
```

## GridSpec

A ``GridSpec`` isn't list-like, and behaves more like a 2D array. Just like a Python array, the indexing is zero-based and specifies the rows first and the columns second, for instance, ``gridspec[0, 1] = object`` would assign the object to the first row and second column.

First, declare a ``GridSpec`` and add red and blue blocks. The red block goes in the first row and span 3 columns. The blue block spans from the second to fourth row, but only occupies the first column

```{pyodide}
gridspec = pn.GridSpec(sizing_mode='stretch_both', max_height=400)

gridspec[0, :3] = pn.Spacer(background='#FF0000')
gridspec[1:3, 0] = pn.Spacer(background='#0000FF')

gridspec
```

Now, add our previously created bokeh figure to the remaining slots of the second row,

```{pyodide}
gridspec[1:3, 1:3] = p1

gridspec
```

Finally, place an image and a ``Column`` of widgets under the plot:

```{pyodide}
gridspec[3, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(name='Toggle Me!'))
gridspec[3, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'

gridspec
```

:::{admonition} Panels Background
:class: info

Read more about ``Panel``s in the [Background for Components](../background/components/components_overview.md#Panels).
:::
