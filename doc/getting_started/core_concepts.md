# {octicon}`mortar-board;2em;sd-mr-1` Core Concepts

In the last section we learned how to [build a simple app](build_app.md). A Panel app like this makes it very easy to explore any function that produces a visual result of a [supported type](https://github.com/pyviz/panel/issues/2), such as Matplotlib, Bokeh, Plotly, Altair, or various text and image types.

## Development flow

As you prepare to develop your Panel application, there are a couple initial development decisions to make about **API** and **environment**:

1. Will you be programming with a Python class-based approach, suitable for more complex apps? If not, or if you are unsure, we recommend starting with the reactive API (`pn.bind`) that you already tasted while [building a simple app](build_app.md).

:::{dropdown} Interested in a class-based approach instead?
:margin: 4
:color: muted
Checkout the same ['outlier' app built using a class-based declarative API](../explanation/api/examples/outliers_declarative.md). And to dive deeper, read the [Explanation > APIs](../explanation/apis.md) section for a discussion on each of the API options.
:::

2. Will you be developing in a [notebook](https://jupyter.org/) or in an editor environment? If you are unsure, we recommend starting in a notebook as you get familiar with Panel, but you can switch between them at any time. Let's talk a bit more about these development environment options:

### Notebook

In a notebook you can quickly iterate on individual components of your application because Panel components render inline. To get started in a notebook simply `import panel` and initialize the extension with `pn.extension()`.

```python
import panel as pn
pn.extension()
```

Now, when you put a Panel component at the end of a notebook cell it will render as part of the output of that cell. By changing the code in your cell and re-running it you can quickly iterate and build the individual units that will make up your final application. This way of working has many benefits because you can work on each component in your application individually without having to re-run your entire application each time.

<img src="https://assets.holoviz.org/panel/gifs/jupyterlab_preview.gif" style="margin-left: auto; margin-right: auto; display: block;"></img>

### Editor

If you are working in an editor, declare the Panel components that you want to display as `servable` (we will discover what that means soon), then launch the script or notebook file. For example, if you were to save the app you built in the previous page into `app.py` and declared `first_app.servable()` within the file, then on the command line you can just run:

```bash
panel serve app.py --autoreload --show
```

Once you run that command Panel will launch a server that will serve your app, open a tab in your default browser (`--show`) and update the application whenever you update the code (`--autoreload`).

<img src="https://assets.holoviz.org/panel/gifs/vscode_autoreload.gif" style="margin-left: auto; margin-right: auto; display: block;"></img>

```{note}
We recommend installing `watchfiles`, which will provide a significantly better user experience when using `--autoreload`.
```

> Checkout [How-to > Prepare to develop](../how_to/prepare_to_develop.md) for more guidance on each of the development environment options.
## Control flow

Now let's get into how Panel actually works. Panel is built on a library called [Param](https://param.holoviz.org/) that controls how information flows through your application. When a *Parameter* changes, e.g. the value of a slider updates or when you update the value manually in code, events are triggered that your app can respond to. Panel provides a number of high-level and lower-level approaches for setting up interactivity in response to updates in *Parameters*. Understanding some of the basic concepts behind Param is essential to getting the hang of Panel.

Let's start simple and answer the question "what is Param?"

- Param is a framework that lets Python classes have attributes with defaults, type/value validation and callbacks when a value changes.
- Param is similar to other frameworks like [Python dataclasses](https://docs.python.org/3/library/dataclasses.html), [pydantic](https://pydantic-docs.helpmanual.io/), and [traitlets](https://traitlets.readthedocs.io/en/stable/)

One of the most important concepts to understand in both Param and Panel is the ability to use *Parameters* as references to drive interactivity. This is often called reactivity and the most well known instance of this approach are spreadsheet applications like Excel. When you reference a particular cell in the formula of another cell, changing the original cell will automatically trigger an update in all cells that reference. The same concept applies to *Parameter* objects.

One of the main things to understand about Param in the context of its use in Panel is the distinction between the *Parameter* **value** and the *Parameter* **object**. The **value** represents the current value of a *Parameter* at a particular point in time, while the **object** holds metadata about the *Parameter* but also acts as a **reference** to the *Parameter's* value across time. In many cases you can pass a *Parameter* **object** and Panel will automatically resolve the current value **and** reactively update when that *Parameter* changes. Let's take a widget as an example:

```python
text = pn.widgets.TextInput()

text.value # 👈 the "value" Parameter of this widget reflects the current value
text.param.value # 👈 can be used as a reference to the live value
```

We will dive into this more deeply later, for now just remember that parameter objects (whether associated with widgets or not) allow you to pass around a reference to a value that automatically updates if the original value changes.

## Display and rendering

Panel aims to let you work with all your favorite Python libraries and has a system for automatically inferring how to render a particular object, whether that is a pandas `DataFrame`, matplotlib `Figure` or any other plotting object. This means that you can easily place any object you want to render into a layout (such as a `Row` or `Column`) and Panel will automatically figure out the appropriate `Pane` type to wrap it. Different `Pane` types know how to render different objects but also provide ways to update the object or even listen to events such as selection of Vega/Altair charts or Plotly plots.

For this reason, it often makes sense to get a handle on the Pane type. So if you want to wrap your `DataFrame` into a pane you can call the `panel` function and it will automatically convert it (this is exactly what a layout does internally when you give it an object to render):

```python
import pandas as pd

df = pd.DataFrame({
  'A': [1, 2, 3, 4],
  'B': [10, 20, 30, 40]
})

df_pane = pn.panel(df)
```

:::{admonition} Tip
:class: success

To inspect the type of an object simply `print` it:

```python
>>> print(pn.Row(df))
Row
    [0] DataFrame(DataFrame)
```
:::

Sometimes an object has multiple possible representations to pick from. In these cases you can explicitly construct the desired `Pane` type, e.g. here are a few representations of a `DataFrame`:

::::{tab-set}

:::{tab-item} DataFrame Pane
```python
pn.pane.DataFrame(df)
```

<table border="0" class="dataframe panel-df">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>A</th>
      <th>B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>20</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>40</td>
    </tr>
  </tbody>
</table>

:::

:::{tab-item} HTML Pane
```python
pn.pane.HTML(df)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>A</th>
      <th>B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>20</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>40</td>
    </tr>
  </tbody>
</table>
</div>

:::


:::{tab-item} Str Pane
```python
pn.pane.Str(df)
```

<pre>
   A   B
0  1  10
1  2  20
2  3  30
3  4  40
</pre>
:::

::::

:::{admonition} Learn More
:class: info

Learn more about Panes in the [Explanation for Components](../explanation/components/components_overview.md#panes)
:::

So far we have only learned how to display data, but to actually add it to your deployed application you also need to mark it as `servable`. To mark an object as servable adds it to the current template, something we will get into later. You can either mark multiple objects as servable which will add it to the page sequentially, or you can use layouts to arrange objects explicitly.

```python
df_pane.servable()
```

:::{admonition} Note
:class: info

In the notebook the `.servable()` method is effectively a no-op. This means you can add it the components you want to add to the rendered app but also see it rendered inline. This makes it possible to build components sequentially in a notebook while simultaneously building an application to be served. If you want to mark something servable but do _not_ want it rendered inline, just put a semicolon (';') after it to tell Jupyter not to render it even if it is the last item in the cell.
:::

## Widgets

To build an interactive application you will typically want to add widget components (such as `TextInput`, `FloatSlider` or `Checkbox`) to your application and then bind them to an interactive function. As an example let's create a slider:

```{pyodide}
import panel as pn

x = pn.widgets.IntSlider(name='x', start=0, end=100)

def square(x):
    return f'{x} squared is {x**2}'

pn.Row(x, pn.bind(square, x))
```

The `pn.bind` function lets us bind a widget or a *Parameter* **object** to a function that returns an item to be displayed. Once bound, the function can be added to a layout or rendered directly using `pn.panel` and `.servable()`. In this way you can express reactivity between widgets and output very easily. Even better, if you use a Panel-aware library like hvPlot, you often don't even need to write and bind a function explicitly, as hvPlot's [.interactive](https://hvplot.holoviz.org/user_guide/Interactive.html) DataFrames already create reactive pipelines by accepting widgets and parameters for most arguments and options.

:::{admonition} Reminder
:class: info

Remember how we talked about the difference between a *Parameter* **value** and a *Parameter* **object**. In the previous example the widget itself is effectively an alias for the *Parameter* object, i.e. the binding operation is exactly equivalent to `pn.bind(square, x.param.value)`. This is true for all widgets: the widget object is treated as an alias for the widget's `value` *Parameter* object. So you can generally either pass in the widget (as a convenient shorthand) or the underlying *Parameter* object.
:::

The binding approach above works, but it is quite heavy handed. Whenever the slider value changes, Panel will re-create a whole new Pane and re-render the output. If we want more fine-grained control we can instead explicitly instantiate a `Markdown` pane and pass it bound functions and *Parameters* by reference:

```{pyodide}
import panel as pn

x = pn.widgets.IntSlider(name='x', start=0, end=100)
background = pn.widgets.ColorPicker(name='Background', value='lightgray')

def square(x):
    return f'{x} squared is {x**2}'

def styles(background):
    return {'background-color': background, 'padding': '0 10px'}

pn.Column(
    x,
    background,
    pn.pane.Markdown(pn.bind(square, x), styles=pn.bind(styles, background))
)
```

To achieve the same thing using more classic callbacks we have to dig a bit further into Param functionality to learn about watching *Parameters*. To `watch` a Parameter means to declare a callback that fires when the *Parameter's* value changes. As an example let's rewrite the example above using a watcher:

```{pyodide}
import panel as pn

x = pn.widgets.IntSlider(name='x', start=0, end=100)
background = pn.widgets.ColorPicker(name='Background', value='lightgray')

square = pn.pane.Markdown(
    f'{x.value} squared is {x.value**2}',
    styles={'background-color': background.value, 'padding': '0 10px'}
)

def update_square(event):
    square.object = f'{event.new} squared is {event.new**2}'

def update_styles(event):
    square.styles = {'background-color': event.new, 'padding': '0 10px'}

x.param.watch(update_square, 'value')
background.param.watch(update_styles, 'value')

pn.Row(x, background, square)
```

The first thing you will note is how much more verbose this is, which should make you appreciate the power of expressing reactivity using *Parameter* binding instead. But if you do need this power, it's there for you!

## Templates

Once you have started to build an application, you will probably want to make it look nicer, which is where templates come in. Whenever you mark an object as `.servable` you are inserting it into a template. By default Panel uses a completely blank template, but it is very simple to select another template by setting `pn.config.template`. Here you will have a few options based on different frameworks, including `'bootstrap'`, `'material'` and `'fast'`.

```python
pn.config.template = 'fast'
```

:::{admonition} Note
:class: info

The `pn.config` object provides a range of options that will allow you to configure your application. As a shortcut, you may instead provide options for the `config` object as keywords to the `pn.extension` call. In other words `pn.extension(template='fast')` is equivalent to `pn.config.template = 'fast'`, providing a clean way to set multiple config options at once.
:::

Once you have configured a template you can control where to render your components using the `target` argument of the `.servable()` method. Most templates have multiple target areas including 'main', 'sidebar', 'header' and 'modal'. As an example you might want to render your widgets into the sidebar and your plots into the main area:

```python
import numpy as np
import matplotlib.pyplot as plt
import panel as pn

pn.extension(template='fast')

freq = pn.widgets.FloatSlider(
    name='Frequency', start=0, end=10, value=5
).servable(target='sidebar')

ampl = pn.widgets.FloatSlider(
    name='Amplitude', start=0, end=1, value=0.5
).servable(target='sidebar')

def plot(freq, ampl):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xs = np.linspace(0, 1)
    ys = np.sin(xs*freq)*ampl
    ax.plot(xs, ys)
    return fig

mpl = pn.pane.Matplotlib(
    pn.bind(plot, freq, ampl)
)

pn.Column(
    '# Sine curve', mpl
).servable(target='main')
```

<img src="../_static/images/core_concepts_app.png" style="margin-left: auto; margin-right: auto; display: block;"></img>

## Next Steps

While `Getting Started`, you have installed Panel, built a simple app, and reviewed core concepts - the basic foundations for you to start using Panel for your own work.

While working, you can find solutions to specific problems in the [How-to](../how_to/index.md) section and you can consult the [API Reference](../api/index.md) or [Component Gallery](../reference/index.rst) sections for technical specifications, descriptions, or examples.

If you want to gain clarity or deepen your understanding on particular topics, refer to the [Explanation](../explanation/index.md) section of the docs. For example, the [Explanation > APIs](../explanation/apis.md) subsection covers the benefits and drawbacks of each supported Panel API.

## Getting Help

Check out the [HoloViz Community](https://holoviz.org/community.html) page for all of the options to connect with developers and other users.
