# Reactive API

Most people are familiar with the reactive programming model due to Excel, where formulas can reference cells or ranges and dynamically (or rather reactively) recompute when the inputs to a formula changes. In Panel reactive APIs build on top of Param. Sticking with the Excel analogy, `Parameter` objects represent the inputs or references in a formula and using this we can build two kinds of reactive constructs, so called expressions and functions.

Reactive expressions are a powerful way to declaratively express complex reactive "formulas" without having to learn a large new API or operate inside a restricted evaluation context (we will unpack what exactly that means a bit later). If we need to express logic using pure Python we can easily fall back to declaring a reactive function using `pn.bind`.

`pn.bind` allows a programmer to indicate that a certain widget or *Parameter* should be used as the argument to a function or method that returns something displayable, after which Panel will *automatically* invoke that function or method when the corresponding *Parameter* changes. The programmer defines and configures widgets explicitly, laying them out with the reactive functions into an app (or even a set of separate Jupyter notebook cells) where each output is updated whenever the corresponding *Parameter* changes.

## Pros:

+ Clear mapping from widgets to the arguments of the function.
+ Explicit layout of each of the different components.
+ Doesn't typically require modifying existing visualization code.

## Cons:

+ Compared to the Declarative API approach, the resulting GUI code encodes details about the underlying computation and thus must be updated whenever the underlying non-GUI code arguments or options change.

## Explanation

In this model, we can use an existing plotting function, declare each widget explicitly to match what that function accepts, and then bind a widget to each of the arguments that we want to be interactive. The `pn.bind` function works much like [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) in that it binds regular arguments and keyword arguments to a function. `partial` can only bind specific, static arguments like `5`, but `pn.bind` can also bind *Parameters*, widgets, and other dynamic functions with declared dependencies to the arguments, ensuring when the function is called the current values of the *Parameters* are passed to the function. Functions bound with `pn.bind` are then reactive, updating whenever the widget or *Parameter* values change.

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

Notice how here we were able to bind widget values to the existing method `autompg.hvplot.scatter()` without changing that code, which is typical -- reactive API GUI code typically encodes detailed knowledge of the underlying domain code (e.g. explicitly listing out the columns from the data frame), but not vice versa.

If you are writing code specifically for building an app, and do not wish to keep domain and GUI code separate even in one direction, the functionality of `pn.bind` is also available as a decorator `@pn.depends`:

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

This alternative way of specifying the same app lets you declare the dependency between a function argument and a widget (or *Parameter*) from the start, which can be clearer if you know the function will always and only be used in a GUI. Otherwise, the `pn.bind` version is greatly preferred, because it allows you to keep the Panel-specific code separate (even in a different Python module or file) from the underlying analysis and plotting code so that you can invoke the underlying code whether or not you have installed Panel.
