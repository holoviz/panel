# Interact Functions

The ``interact`` function will automatically generate a UI (including widgets) by inspecting the arguments of the function given to it, or by using additional hints you provide in the ``interact`` function call. If you have worked with the [``ipywidgets``](https://github.com/jupyter-widgets/ipywidgets) package you may already be familiar with this approach. (In fact, the Panel interact function is modeled on the one from ipywidgets, making it simpler to port code between the two platforms.) The basic idea is that given a function that returns some object, Panel will inspect the arguments to that function, try to infer appropriate widgets for those arguments, and then re-run that function to update the output whenever one of the widgets generates an event. For more detail on how interact creates widgets and other ways of using it, see the Panel [interact user guide](./Interact.md).  This section instead focuses on when and why to use this API, laying out its benefits and drawbacks.

The main benefit of this approach is convenience and ease of use.  You start by writing some function that returns an object, be that a plot, a dataframe, or anything else that Panel can render. Then with a single call to `pn.interact()`, you can immediately get an interactive UI, without ever instantiating any widgets or wiring up any callbacks explicitly. Unlike ipywidgets, the ``pn.interact`` call will return a Panel. This Panel can then be further modified by laying out the widgets and output separately, or combining these components with other panes. Even though `pn.interact` itself is limited in flexibility compared to the rest of Panel, you can still unpack and reconfigure the results from it to generate fairly complex GUIs in very little code.

## Pros:

+ Easy to use (or at least easy to get started!).
+ Doesn't typically require modifying existing visualization code.

## Cons:

- Most of the behavior is implicit, with magic happening by introspection, making it difficult to see how to modify the appearance or functionality of the resulting object.
- Customizing the layout requires indexing into the panel returned by `interact`.

## Explanation

The magic of the `interact` API derives from the fact that it inspects the signature of a function and/or the arguments passed to `interact` and automatically generates widgets appropriate for controlling those arguments.

As an example let us declare a simple function that returns the arguments formatted as a string. If we pass in an integer for argument `a` and a string for argument `b` it will generate a slider and string input widget for each argument respectively:

```{pyodide}
import panel as pn
pn.extension()

def fn(a, b):
    return f'Arguments: {a,b}'

pn.interact(fn, a=1, b='string')
```

This makes it very powerful for quickly making a function interactive but the behavior is very implicit and a more declarative approach is usually preferable for most usecases.

## Example

The simplest `interact` call can be a one-liner, but here we'll show an example of intermediate complexity so that you get a good idea of what `interact` can do in practice. In this code, ``pn.interact`` infers the initial value for `x` and `y` from the `autompg_plot` function default arguments and their widget type and range from the `columns` list provided to `interact`. `interact` wouldn't normally put up a color widget because it would have no way of knowing that this string-type argument represents an RGB color, and so here we explicitly create a color-picker widget and pass that as the value for the color so that we can control the color as well.

Finally, we unpack the result from `interact` and rearrange it in a different layout with a title, to create the final app. See the Panel [interact user guide](./Interact.md) for even simpler examples along with details about how to control the widgets and how to rearrange the layout.

```{pyodide}
import hvplot.pandas

from bokeh.sampledata.autompg import autompg

def autompg_plot(x='mpg', y='hp', color='#058805'):
    return autompg.hvplot.scatter(x, y, c=color, padding=0.1)

columns = list(autompg.columns[:-2])

color = pn.widgets.ColorPicker(name='Color', value='#4f4fdf')
layout = pn.interact(autompg_plot, x=columns, y=columns, color=color)

pn.Row(pn.Column('## MPG Explorer', layout[0]), layout[1])
```
