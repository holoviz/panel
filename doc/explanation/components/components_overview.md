# Component overview

Panel provides a wide range of components for easily composing panels, apps, and dashboards both in the notebook and as standalone apps. The components can be broken down into three broad classes of objects:

* ``Pane`` objects allow wrapping external viewable items like Bokeh, Plotly, Vega, or HoloViews plots, so they can be embedded in a panel.
* ``Widget`` objects provide controls that can trigger Python or JavaScript events.
* ``Panel`` layout objects allow combining plots into a ``Row``, ``Column``, ``Tabs`` or a ``Grid``.

All objects share an API that makes it easy to [customize behavior and appearance](../../how_to/styling/index.md), [link parameters](../../how_to/links/index.md), and to [display them in notebooks](../../how_to/notebook/index.md), [serve them as applications](../../how_to/server/index.md) or [export them](../../how_to/export/index.md). To display any panel objects in a notebook environment ensure you load the extension first:


```{pyodide}
import panel as pn
pn.extension()
```

Note that to use certain components such as Vega, LaTeX, and Plotly plots in a notebook, the models must be loaded using the extension. E.g.:

``` python
pn.extension('vega', 'katex')
```

will ensure that the Vega and LaTeX JS dependencies are loaded. Once the extension is loaded, Panel objects will display themselves in the notebook. Outside the notebook, objects can be displayed in a server using the `show` method or run from the commandline by appending ``.servable()`` to the objects to be displayed.

## Parameterized Components

All components in Panel are built on the [Param](https://param.holoviz.org/) library. Each component declares a set of parameters that control the behavior and output of the component. See the [Param documentation](https://param.holoviz.org/) for more details on how to use Param. The basic idea, however, is that the parameter values can be controlled both at the class level:

```{pyodide}
pn.widgets.Select.sizing_mode = 'stretch_both'
```

or on each instance:

```{pyodide}
pn.widgets.Select(sizing_mode='stretch_both');
```

In the first case, all subsequent Select objects created will have sizing mode `stretch_both`; in the second only this particular instance will.

## Panes

``Pane`` objects makes it possible to display and arrange a wide range of plots and other media on a page, including plots (e.g. Matplotlib, Bokeh, Vega/Altair, HoloViews, Plotly), images (e.g. PNGs, SVGs, GIFs, JPEGs), and various markup languages (e.g. Markdown, HTML, LaTeX).

There are two main ways to construct panes.  The first is to explicitly construct a pane:


```{pyodide}
pn.pane.Markdown('''
# H1
## H2
### H3
''')
```

Panel also provides a convenient helper function that will convert objects into a Pane or Panel. This utility is also used internally when passing external objects to a Row, Column, or other Panel. The utility resolves the appropriate representation for an object by checking all Pane object types available and then ranking them by priority. When passing a string (for instance) there are many representations, but the PNG pane takes precedence if the string is a valid URL or local file path ending in ".png".


```{pyodide}
png = pn.panel('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=500)

png
```

To see the type of the pane, use the `print` function, which works with any Widget, Pane, or (perhaps most usefully) Panel:


```{pyodide}
print(png)
```

The `print` representation typically includes *Parameter* values for that object, such as `width` in this case.

All Panel objects store the object they are wrapping on their ``object`` parameter.  By setting that parameter, existing views of this object (whether in this or other notebook cells or on a server instance) will update:


```{pyodide}
png.object = 'https://upload.wikimedia.org/wikipedia/commons/3/39/PNG_demo_heatmap_Banana.png'
```

In addition to the ``object`` parameter, each pane type may have additional parameters that modify how the ``object`` is rendered.

## Widgets

``Widget`` components, like all objects in Panel, sync their parameter state between all views of the object. Widget objects have a ``value`` parameter, layout parameters, and other parameters specific to each widget. In the notebook we can display widgets just like other Panel objects:


```{pyodide}
widget = pn.widgets.TextInput(name='A widget', value='A string')
widget
```

In this way the widget values can easily be accessed and set:


```{pyodide}
widget.value = '3'
widget.width = 100
```

As well as linked to other objects:


```{pyodide}
string = pn.pane.Str()

widget.jslink(string, value='object')

pn.Row(widget, string)
```

See the [How-To > Link section](../../how_to/links/index.md) for recipes on how to link widgets to other objects, using either Python or JavaScript.

## Panels

Panels allow arranging widget and pane objects into fixed-size or responsively resizing layouts, building simple apps or complex dashboards. The whole Panel library is designed to make it easy to create such objects, which is why it takes its name from them.

There are four main types of ``Panel``s:

* **``Row``**: A ``Row`` arranges a list of components horizontally.
* **``Column``**: A ``Column`` arranges a list of components vertically.
* **``Tabs``**: A ``Tabs`` object lays out a list of components as selectable tabs.
* **``GridSpec``**: A ``GridSpec`` lays out components on a grid.

``Spacer`` components are also provided, to control spacing between other components.

### Row & Column

The ``Row``, ``Column``, and ``Tabs`` Panels all behave very similarly.  All of them are list-like, which means they have many of the same methods as a simple Python list, making it easy to add, replace, and remove components interactively using ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__``. These methods make it possible to interactively configure and modify an arrangement of plots, making them an extremely powerful tool for building apps or dashboards.

``Row`` and ``Column`` can be initialized as empty or with the objects to be displayed as arguments. If each of the object(s) provided is not already a ``Widget``, ``Pane``, or ``Panel``, the panel will internally call the ``pn.panel`` function to convert it to a displayable representation (typically a Pane).

To start with, we will declare a ``Column`` and populate it with a title and a widget:


```{pyodide}
column = pn.Column('# A title', pn.widgets.FloatSlider())
```

Next we add another bit of markdown:


```{pyodide}
column.append('* Item 1\n* Item 2')
```

Then we add a few more widgets:


```{pyodide}
column.extend([pn.widgets.TextInput(), pn.widgets.Checkbox(name='Tick this!')])
```

and finally we change our mind and replace the ``Checkbox`` with a button:


```{pyodide}
column[4] = pn.widgets.Button(name='Click here')

column
```

The ability to add, remove, and replace items using list operations opens up the possibility of building rich and responsive GUIs with the ease of manipulating a Python list.

### Tabs

The ``Tabs`` layout allows displaying multiple objects as individually toggleable tabs. Just like ``Column`` and ``Row``, the tabs object can be used like a list.  However, when adding or replacing items, it is also possible to pass a tuple providing a custom title for the tab:


```{pyodide}
from bokeh.plotting import figure

p1 = figure(width=300, height=300)
p1.line([1, 2, 3], [1, 2, 3])

tabs = pn.Tabs(p1)

# Add a tab
tabs.append(('Slider', pn.widgets.FloatSlider()))

# Add multiple tabs
tabs.extend([
    ('Text', pn.widgets.TextInput()),
    ('Color', pn.widgets.ColorPicker())
])

tabs
```

### GridSpec

A ``GridSpec`` is quite different from the other ``Panel`` layout types in that it isn't list-like. Instead it behaves more like a 2D array that automatically expands when assigned to. This property makes it a very powerful means of declaring a dashboard layout with either a fixed size or with responsive sizing, i.e. one that will rescale with the browser window. **Note**: A GridSpec modifies the layout parameters of the objects that are assigned to the grid, so that it can support both fixed and responsive sizing modes.

To create a ``GridSpec`` we first declare it, either with a responsive ``sizing_mode`` or a fixed width and height. Once declared we can use 2D assignment to specify the index or span on indices the object in the grid should occupy. Just like a Python array, the indexing is zero-based and specifies the rows first and the columns second, i.e. ``gspec[0, 1]`` would assign an object to the first row and second column.

Like the other Panel types, any object can be assigned to a grid location.  However, responsive sizing modes will only work well if each object being assigned supports interactive rescaling. To demonstrate the abilities, let us declare a grid with a wide range of different objects, including Spacers, Bokeh figures, HoloViews objects, images, and widgets:


```{pyodide}
import holoviews as hv
import holoviews.plotting.bokeh

from bokeh.plotting import figure

fig = figure()
fig.scatter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 2, 1, 0, -1, -2, -3])

gspec = pn.GridSpec(sizing_mode='stretch_both', max_height=800)

gspec[0, :3] = pn.Spacer(styles=dict(background='#FF0000'))
gspec[1:3, 0] = pn.Spacer(styles=dict(background='#0000FF'))
gspec[1:3, 1:3] = fig
gspec[3:5, 0] = hv.Curve([1, 2, 3])
gspec[3:5, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
gspec[4:5, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(name='Toggle Me!'))

gspec
```

When assigning to a grid cell that is already occupied, the ``GridSpec`` will generate a helpful warning that highlights which objects are overlapping and where. Even so, it will still replace any overlapping items by default. To control this behavior to either error or replace the objects silently, set the ``GridSpec`` mode to 'error' or 'override'.

```{pyodide}
gspec[0:3, :2] = 'Some text'
```

In addition to assignment, we can also slice and index the ``GridSpec`` to access an individual object or a subregion of the grid, returning another GridSpec. Here we will access the last row and everything except the first column:


```{pyodide}
gspec[-1, 1:]
```

For more details on using `GridSpec` Panels, see the [component gallery](../../reference/layouts/GridSpec.ipynb).
