# Add or Remove Components from Panels

This guide addresses how to add or remove components from ``Panels``, starting with the most common: ``Row`` and ``Column``.

## Row & Column Panels

To start, we will declare a ``Column`` and populate it with some text and a widget:

```{pyodide}
import panel as pn
pn.extension() # for notebook

column = pn.Column('some text', pn.widgets.FloatSlider())

column
```

As we can manipulate a ``Row`` or ``Column`` object just like a Python list, we'll use `.append` to add some markdown:

```{pyodide}
column.append('* Item 1\n* Item 2')

column
```

Next, we add a few more widgets:

```{pyodide}
column.extend([pn.widgets.TextInput(), pn.widgets.Checkbox(name='Tick this!')])

column
```

Now, we change our mind and replace the ``Checkbox`` with a button:

```{pyodide}
column[4] = pn.widgets.Button(name='Click here')

column
```

Finally, we decide to remove the FloatSlider widget, but we forget its index. We can use `print` to see the index of the components:

```{pyodide}
print(column)
```

and then `.pop` to remove the FloatSlider:

```{pyodide}
column.pop(1)

column
```

Here is the complete code for this subsection in case you want to easily copy it:

```{pyodide}
import panel as pn
pn.extension() # for notebook

column = pn.Column('some text', pn.widgets.FloatSlider())
column.append('* Item 1\n* Item 2')
column.extend([pn.widgets.TextInput(), pn.widgets.Checkbox(name='Tick this!')])
column[4] = pn.widgets.Button(name='Click here')
column.pop(1)

column
```

## Tabs Panel

``Tabs`` can also be changed like a Python list. However, when adding or replacing tab items, it is also possible to pass a tuple providing a custom title for the tab. First, create a ``Tabs`` panel that contains a plot:

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

Here is the complete code for this subsection in case you want to easily copy it:
```{pyodide}
import panel as pn
pn.extension() # for notebook
from bokeh.plotting import figure

p1 = figure(width=300, height=300)
p1.line([1, 2, 3], [1, 2, 3])

tabs = pn.Tabs(p1)
tabs.append(('Slider', pn.widgets.FloatSlider()))
tabs.extend([
    ('Text', pn.widgets.TextInput()),
    ('Color', pn.widgets.ColorPicker())
])

tabs
```

## GridSpec Panel

A ``GridSpec`` behaves like a 2D array. The indexing is zero-based and specifies the rows first and the columns second.

First, declare a ``GridSpec`` and add red and blue blocks. The red block goes in the first row and spans 3 columns. The blue block spans from the second to fourth row, but only occupies the first column:

```{pyodide}
gridspec = pn.GridSpec(sizing_mode='stretch_both', min_height=600)

gridspec[0, :3] = pn.Spacer(styles={'background': '#FF0000'})
gridspec[1:3, 0] = pn.Spacer(styles={'background': '#0000FF'})

gridspec
```

Next, add our previously created bokeh figure to the remaining slots of the second row:

```{pyodide}
gridspec[1:3, 1:3] = p1

gridspec
```

Then, place an image and a ``Column`` of widgets under the plot:

```{pyodide}
gridspec[3, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(name='Toggle Me!'))
gridspec[3, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'

gridspec
```

Finally, remove the Spacers:

```{pyodide}
del gridspec[0, :3]
del gridspec[1:3, 0]

gridspec
```

Here is the complete code for this subsection in case you want to easily copy it:

``` {pyodide}
import panel as pn
pn.extension() # for notebook

gridspec = pn.GridSpec(sizing_mode='stretch_both', max_height=400)

gridspec[0, :3] = pn.Spacer(styles={'background': '#FF0000'})
gridspec[1:3, 0] = pn.Spacer(styles={'background': '#0000FF'})

gridspec[1:3, 1:3] = p1

gridspec[3, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(name='Toggle Me!'))
gridspec[3, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'

del gridspec[0, :3]
del gridspec[1:3, 0]

gridspec
```

---

## Related Resources

- Learn more about Panes in [Explanation > Components](../../explanation/components/components_overview.md#panes).
- For more detail about `GridSpec` Panels, see the [Component Gallery > GridSpec](../reference/layouts/GridSpec.md).
