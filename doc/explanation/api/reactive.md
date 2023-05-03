# Reactive API

The `pn.bind` reactive programming API requires the programmer to select and configure widgets and to lay out components explicitly. Once widgets have been bound to a reactive function, you can lay out the bound function and the widgets in any order or combination you like, including across Jupyter notebook cells if desired.

## Pros:

+ Clear mapping from widgets to the arguments of the function.
+ Explicit layout of each of the different components.
+ Doesn't typically require modifying existing visualization code.

## Cons:

+ Compared to the Declarative API approach, the resulting code is specific to the GUI framework

## Explanation

In this model, we can use an existing plotting function, declare each widget explicitly, and then bind a widget to each of the arguments that we want to be interactive. The `pn.bind` function works much like [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) in that it binds regular arguments and keyword arguments to a function. `partial` can only bind specific, static arguments like `5`, but `pn.bind` can also bind parameters, widgets, and other dynamic functions with dependencies to the arguments, ensuring when the function is called the current values of the parameters are passed to the function. A bound function is then reactive, updating whenever the widget values change.

To make the concept of binding clear, let's look at a trivial example first:

```{pyodide}
import panel as pn
pn.extension()

def fn(a,b): return f'Arguments: {a,b}'
slider = pn.widgets.FloatSlider(value=0.5)

bound_fn = pn.bind(fn, a=slider, b=2)
bound_fn()
```

Here we can see that although `fn` required two arguments, `bound_fn` takes no arguments because `a` has been bound to the slider value and `b` to a static value.

If we display the slider and bound function in Panel, we can see that everything will update reactively as you use the widget, reevaluating the function whenever the bound argument changes:

```{pyodide}
pn.Row(slider, bound_fn)
```

## Example

Now let us create a simple application with some more interesting output. Just like in the [other API examples](index) we will load the AutoMPG dataset and let you pick the axes to plot and how to color the scatter plot. Using the `pn.bind` function, we can easily add the interactivity by binding widgets to each argument and lay out the result with the widgets:

```{pyodide}
import hvplot.pandas

from bokeh.sampledata.autompg import autompg

columns = list(autompg.columns[:-2])

x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#AA0505')

pn.Row(
    pn.Column('## MPG Explorer', x, y, color),
    pn.bind(autompg.hvplot.scatter, x, y, c=color)
)
```

Notice how here we didn't even need the `autompg_plot` function because `bind` works with both methods and functions.

If you are writing code specifically for building an app, and do not wish to keep domain and GUI code separate, the functionality of `pn.bind` is also available as a decorator `@pn.depends`:

```{pyodide}
x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#AA0505')

@pn.depends(x, y, color)
def plot(xval, yval, colorval):
    return autompg.hvplot.scatter(xval, yval, c=colorval)

pn.Row(
    pn.Column('## MPG Explorer', x, y, color),
    plot
)
```

This alternative way of specifying the same app lets you declare the dependency between a function argument and a widget (or parameter) from the start, which can be clearer if you know the function will always and only be used in a GUI. Otherwise, the `pn.bind` version is preferred, because it allows you to keep the Panel-specific code separate (even in a different Python module or file) from the underlying analysis and plotting code.
