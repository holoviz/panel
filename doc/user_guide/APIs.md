# APIs

Panel can be used to make a first pass at an app or dashboard in minutes, while also allowing you to fully customize the app's behavior and appearance or flexibly integrate GUI support into long-term, large-scale software projects. To accommodate these different ways of using Panel, four different APIs are available:

* **Interact functions**: Auto-generates a full UI (including widgets) given a function
* **Reactive functions**: Linking functions or methods to widgets using ``pn.bind`` or the equivalent ``pn.depends`` decorator, declaring that the function should be re-run when those widget values change
* **Parameterized class**: Declare parameters and their ranges in Parameterized classes, then get GUIs (and value checking!) for free
* **Callbacks**: Generate a UI by manually declaring callbacks that update panels or panes

Each of these APIs has its own benefits and drawbacks, so this section will go through each one in turn, while working through an example app and pointing out the benefits and drawback along the way. For a quick overview you can also review the API gallery examples, e.g. the [stocks_hvplot](../gallery/apis/stocks_hvplot.ipynb) app.

To start with let us define some imports, load the `autompg` dataset, and define a plotting function we will be reusing throughout this user guide.


```{pyodide}
import hvplot.pandas
from bokeh.sampledata.autompg import autompg

def autompg_plot(x='mpg', y='hp', color='#058805'):
    return autompg.hvplot.scatter(x, y, c=color, padding=0.1)

columns = list(autompg.columns[:-2])
```

Given values for the x and y axes and a color, this function can be used to generate an interactive plot without needing any Panel components:


```{pyodide}
autompg_plot()
```

But if we want to let a user control the axes and the color with widgets rather than writing Python code, we can use one of the Panel APIs as shown in the rest of the notebook.


```{pyodide}
import panel as pn
pn.extension()
```

## Reactive Functions

The `pn.bind` reactive programming API is very similar to the ``interact`` function but is more explicit about widget selection and layout. `pn.bind` requires the programmer to select and configure widgets explicity and to lay out components explicitly, without relying on inference of widget types and ranges and without any default layouts. Specifying those aspects explicitly provides more power and control, but does typically take a bit more code and more knowledge of widget and layout components than using `interact` does. Once widgets have been bound to a reactive function, you can lay out the bound function and the widgets in any order or combination you like, including across Jupyter notebook cells if desired.

### Pros:

+ Very clear mapping from widgets to the arguments of the function.
+ Very explicit layout of each of the different components.
+ Like `interact`, doesn't typically require modifying existing visualization code.

### Cons:

- Typically requires a bit more code than `interact`

In this model, we can use an existing plotting function just as for `interact`, but then need to declare each widget explicitly and then bind a widget to each of the arguments that we want to be interactive. The `pn.bind` function works much like [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) in that it binds regular arguments and keyword arguments to a function. `partial` can only bind specific, static arguments like `5`, but `pn.bind` can also bind parameters, widgets, and other dynamic functions with dependencies to the arguments, ensuring when the function is called the current values of the parameters are passed to the function. A bound function is then reactive, updating whenever the widget values change.

To make the concept of binding clear, let's look at a trivial example first:


```{pyodide}
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

Using `pn.bind`, we can easily build something like the `interact` app above if we explicitly make widgets for each argument, bind them to the plotting function, and lay out the result with the widgets:


```{pyodide}
x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#AA0505')

pn.Row(pn.Column('## MPG Explorer', x, y, color),
       pn.bind(autompg.hvplot.scatter, x, y, c=color))
```

Notice how here we didn't even need the `autompg_plot` function here, because `bind` works with both methods and functions, so for this particular case the reactive API works out to the same amount of code as `interact`. In practice `interact` is shorter and simpler in the case of accepting the default behavior, making it simple to get started, while `pn.bind` requires a bit more code to get started but then allows easier customization and specification.

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

## Interact Functions

The ``interact`` function will automatically generate a UI (including widgets) by inspecting the arguments of the function given to it, or by using additional hints you provide in the ``interact`` function call. If you have worked with the [``ipywidgets``](https://github.com/jupyter-widgets/ipywidgets) package you may already be familiar with this approach. (In fact, the Panel interact function is modeled on the one from ipywidgets, making it simpler to port code between the two platforms.) The basic idea is that given a function that returns some object, Panel will inspect the arguments to that function, try to infer appropriate widgets for those arguments, and then re-run that function to update the output whenever one of the widgets generates an event. For more detail on how interact creates widgets and other ways of using it, see the Panel [interact user guide](./Interact.md).  This section instead focuses on when and why to use this API, laying out its benefits and drawbacks.

The main benefit of this approach is convenience and ease of use.  You start by writing some function that returns an object, be that a plot, a dataframe, or anything else that Panel can render. Then with a single call to `pn.interact()`, you can immediately get an interactive UI, without ever instantiating any widgets or wiring up any callbacks explicitly. Unlike ipywidgets, the ``pn.interact`` call will return a Panel. This Panel can then be further modified by laying out the widgets and output separately, or combining these components with other panes. Even though `pn.interact` itself is limited in flexibility compared to the rest of Panel, you can still unpack and reconfigure the results from it to generate fairly complex GUIs in very little code.

### Pros:

+ Easy to use (or at least easy to get started!).
+ Doesn't typically require modifying existing visualization code.

### Cons:

- Most of the behavior is implicit, with magic happening by introspection, making it difficult to see how to modify the appearance or functionality of the resulting object.
- Customizing the layout requires indexing into the panel returned by `interact`.

The simplest `interact` call can be a one-liner, but here we'll show an example of intermediate complexity so that you get a good idea of what `interact` can do in practice. In this code, ``pn.interact`` infers the initial value for `x` and `y` from the `autompg_plot` function default arguments and their widget type and range from the `columns` list provided to `interact`. `interact` wouldn't normally put up a color widget because it would have no way of knowing that this string-type argument represents an RGB color, and so here we explicitly create a color-picker widget and pass that as the value for the color so that we can control the color as well. Finally, we unpack the result from `interact` and rearrange it in a different layout with a title, to create the final app. See the Panel [interact user guide](./Interact.md) for even simpler examples along with details about how to control the widgets and how to rearrange the layout.


```{pyodide}
color = pn.widgets.ColorPicker(name='Color', value='#4f4fdf')
layout = pn.interact(autompg_plot, x=columns, y=columns, color=color)

pn.Row(pn.Column('## MPG Explorer', layout[0]), layout[1])
```

## Parameterized Classes

The [Param](http://param.pyviz.org) library allows expressing the parameters of a class (or a hierarchy of classes) completely independently of a GUI implementation. Panel and other libraries can then take those parameter declarations and turn them into a GUI to control the parameters. This approach allows the parameters controlling some computation to be captured specifically and explicitly (but as abstract parameters, not as widgets). Then thanks to the ``@param.depends`` decorator (similar to `@panel.depends` but for use in Parameterized classes without any dependency on Panel), it is then possible to directly express the dependencies between the parameters and the computation defined in some method on the class, all without ever importing Panel or any other GUI library. The resulting objects can then be used in both GUI and non-GUI contexts (batch computations, scripts, servers).

The parameterized approach is a powerful way to encapsulate computation in self-contained classes, taking advantage of object-oriented programming patterns. It also makes it possible to express a problem completely independently from Panel or any other GUI code, while still getting a GUI for free as a last step. For more detail on using this approach see the [Param user guide](./Param.md).

### Pros:

+ Declarative way of expressing parameters and dependencies between parameters and computation
+ The resulting code is not tied to any particular GUI framework and can be used in other contexts as well

### Cons:

- Requires writing classes
- Less explicit about widgets to use for each parameter; can be harder to customize behavior than if widgets are instantiated explicitly

In this model we declare a subclass of ``param.Parameterized``, declare the parameters we want at the class level, make an instance of the class, and finally lay out the parameters and plot method of the class.


```{pyodide}
import param

class MPGExplorer(param.Parameterized):

    x = param.Selector(objects=columns)
    y = param.Selector(default='hp', objects=columns)
    color = param.Color(default='#0f0f0f')

    @param.depends('x', 'y', 'color') # optional in this case
    def plot(self):
        return autompg_plot(self.x, self.y, self.color)

explorer = MPGExplorer()

pn.Row(explorer.param, explorer.plot)
```

## Callbacks

The callback API in panel is the lowest-level approach, affording the greatest amount of flexibility but also quickly growing in complexity because each new interactive behavior requires additional callbacks that can interact in complex ways. Nonetheless, callbacks are important to know about, and can often be used to complement the other approaches. For instance, one specific callback could be used in addition to the more reactive approaches the other APIs provide.

For more details on defining callbacks see the [Links user guide](./Links.md).

### Pros:

+ Complete and modular control over specific events

### Cons:

- Complexity grows very quickly with the number of callbacks
- Have to handle initializing the plots separately

In this approach we once again define the widgets. Unlike in other approaches we then have to define the actual layout, to ensure that the callback we define has something that it can update or replace. In this case we use a single callback to update the plot, but in many cases multiple callbacks might be required.


```{pyodide}
x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#880588')

layout = pn.Row(
    pn.Column('## MPG Explorer', x, y, color),
    autompg_plot(x.value, y.value, color.value))

def update(event):
    layout[1].object = autompg_plot(x.value, y.value, color.value)

x.param.watch(update, 'value')
y.param.watch(update, 'value')
color.param.watch(update, 'value')

layout
```

## Summary

As we have seen, each of these four APIs allows building the same basic application. The choice of the appropriate API depends very much on the use case. To build a quick throwaway GUI the ``interact`` approach can be completely sufficient. A much more explicit, flexible, and maintainable version of that approach is to define a reactive function that is bound directly to a set of widgets using `pn.bind`. When writing libraries or other code that might be used independently of the actual GUI, a Parameterized class can be a great way to organize the code. Finally, if you need low-level control or want to complement any of the other approaches, defining explicit callbacks can be the best approach. Nearly all of the functionality of Panel can be accessed using any of the APIs, but each makes certain things much easier than others. Choosing the API is therefore a matter of considering the tradeoffs and of course also a matter of preference. If you still aren't sure after reading the above, then just go with the `pn.bind` reactive API!
