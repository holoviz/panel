# Core Concepts

Getting started with Panel is pretty straightforward, open your editor, IDE or notebook environment, declare a few Panel components as `servable` (we will discover what that means soon), then launch the script or notebook file with:

```bash
panel serve your_script.py --autoreload --show
```

Once you run that command Panel will launch a server that will serve your app, open a tab in your default browser (`--show`) and update the application whenever you update the code (`--autoreload`).

## Development flow

Depending on whether you are using a classical editor/IDE or a notebook environment we recommend two slightly different approaches to working. Both are suited to quick iteration but provide quite different modes of working.

### Notebook

In a notebook you can quickly iterate on individual components of your application because Panel components render inline. To get started in a notebook simply `import panel` and initialize the extension (this loads Panel and any optional extensions you might want to use in your application).

```python
import panel as pn
pn.extension('altair', 'tabulator')
```

Now you are ready to go, all Panel components will render themselves. In other words, when you put a Panel component at the end of a cell it will render as part of the output of that cell. By changing the code in your cell and re-running it you can quickly iterate and build the individual units that will make up your final application. This way of working has many benefits because you can work on each component in your application individually without having to re-run your entire application each time.

:::{admonition} Tip
:class: success

When working in JupyterLab you will see a little Panel icon (<img src="/_static/favicon.ico" alt="Panel Icon" width="20px"/>) in your toolbar. This will let you preview the application you are building quickly and easily.
:::

### Editor/IDE

The experience when working in an editor or IDE is slightly different. Whenever you save your application script the server will reload your application. This has benefits too, since it let's you quickly see how your whole application fits together.

## Control flow

Now let's get into how Panel actually works. Panel is built on a library called [Param](https://param.holoviz.org/), this controls how information flows through your application. When a parameter changes, e.g. the value of a slider updates or when you update the value manually in code, events are triggered that you can respond to. Panel provides a number of high-level and lower-level approaches for setting up interactivity in response to updates in parameters. Understanding some of the basic concepts behind param is essential to getting a hang of Panel.

Let's start simple and answer the question "what is param?"

- Param is a framework that lets Python classes have attributes with defaults, type/value validation and callbacks when a value changes.
- Param is similar to other frameworks like [Python dataclasses](https://docs.python.org/3/library/dataclasses.html), [pydantic](https://pydantic-docs.helpmanual.io/) and [traitlets](https://traitlets.readthedocs.io/en/stable/)

One of the main things to understand about param in the context of its use in Panel is the distinction between the parameter **value** and the parameter **object**. The **value** represents the current value of a parameter at a particular point in time, while the **object** holds metadata about the parameter but also acts as a **reference** to the parameters value across time. In many cases you can pass a parameter **object** and Panel will automatically resolve the current value **and** reactively update when that parameter changes. Let's take a widget as an example:

```python
text = pn.widgets.TextInput()

text.value # 👈 this reflects the current value
text.param.value # 👈 can be used as a reference to the live value
```


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

Sometimes an object has multiple possible representations to pick from. In these cases you can explicitly construct construct the desired `Pane` type, e.g. here are a few representations of a `DataFrame`:

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

So far we have only learned how to display data, to actually add it to your application you need to mark it as `servable`. To mark an object as servable adds it to the current template, something we will get into later. You can either mark multiple objects as servable which will add it to the page sequentially or you can use layouts to arrange objects explicitly.

```python
df_pane.servable()
```

:::{admonition} Note
:class: info

In the notebook the `.servable()` method is effectively a no-op. This means you can add it the components you want to add to the rendered app but also see it rendered inline. This makes it possible to build components sequentially in a notebook while simultaneously building an application to be served.
:::

## Widgets

To build an interactive application you will want to add widget components (such as `TextInput`, `FloatSlider` or `Checkbox`) to your application and then bind them to an interactive function. As an example let's create a slider:

```{pyodide}
import panel as pn
x = pn.widgets.IntSlider(name='x', start=0, end=100)

def square(x):
    return f'{x} squared is {x**2}'

pn.Row(pn.bind(square, x))
```

The `pn.bind` function let's us bind widgets (and parameter **objects**) to a function that returns an object to be displayed. Once bound the function can be added to a layout or rendered directly using `pn.panel` and `.servable()`. In this way you can express reactivity between widgets and output very easily.


:::{admonition} Reminder
:class: info

Remember how we talked about the difference between a parameter **value** and a parameter **object**. In the previous example the widget itself is effectively an alias for the parameter object, i.e. the binding operation is exactly equivalent to `pn.bind(square, x.param.value)`. This is true for all widgets, the widget itself is an alias for the widgets `value` parameter.
:::


In certain cases reactivity isn't what is needed, e.g. if you want very fine grained control over specific parameters. To achieve this we have to dig a bit further into Param functionality, specifically we need to learn about watching parameters. To `watch` a parameter means to declare a callback that fires when the parameter value changes. As an example let's rewrite the example above using a watcher:

```{pyodide}
import panel as pn
x = pn.widgets.IntSlider(name='x', start=0, end=100)
square = pn.panel(f'{x.value} squared is {x.value**2}')

def update_square(event):
    square.object = f'{x.value} squared is {x.value**2}'

x.param.watch(update_square, 'value')

pn.Row(x, square)
```

The first thing you will not is how much more verbose this is, which should make you appreciate the power of expressing reactivity using parameter binding. At the same time this is also more explicit however, and also provides more control over very specific, fine-grained updates.

## Templates

Once you have started to build an application you will probably want to make it look nicer, this is where templates come in. Whenever you mark an object as `.servable` you are inserting it into a template. By default Panel uses a completely blank template but it is very simple to change that, by setting `pn.config.template` you can enable different templates. Here you will have a few options based on different frameworks, including `'bootstrap'`, `'material'` and `'fast'`.

```python
pn.config.template = 'fast'
```


:::{admonition} Note
:class: info

The `pn.config` object provides a range of options that will allow you to configure your application, however as a shortcut you may also provide options for the `config` object as keywords to the `pn.extension`. In other words `pn.extension(template='fast')` is equivalent to `pn.config.template = 'fast'`. This provides a clean way to set multiple config options at once.
:::

Once you have configured a template you can control where to render your components using the `target` argument of the `.servable()` method. Most templates have multiple targets including 'main', 'sidebar', 'header' and 'modal'. As an example you might want to render your widgets into the sidebar and your plots into the main area:

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

pn.Column(
    '# Sine curve',
    pn.bind(plot, freq, ampl),
).servable(target='main')
```

## Exploring further

For a quick reference of different Panel functionality refer to the [overview](../user_guide/Overview.md). If you want a more detailed description of different ways of using Panel, each appropriate for different applications see the following materials:

- [APIs](../user_guide/APIs.rst): An overview of the different APIs offered by Panel.
- [Parameters](../user_guide/Param.rst): Capturing parameters and their links to actions declaratively

Just pick the style that seems most appropriate for the task you want to do, then study that section of the user guide. Regardless of which approach you take, you'll want to learn more about Panel's panes and layouts:

- [Components](../user_guide/Components.rst): An overview of the core components of Panel including Panes, Widgets and Layouts
- [Customization](../user_guide/Customization.rst): How to set styles and sizes of Panel components
- [Display & Export](../user_guide/Display_and_Export.rst): An overview on how to display and export Panel components and apps.
- [Server Configuration](../user_guide/Server_Configuration.md): An overview on how to configure applications and dashboards for deployment.
- [Templates](../user_guide/Templates.rst): Composing one or more Panel objects into a template with full control over layout and styling.
