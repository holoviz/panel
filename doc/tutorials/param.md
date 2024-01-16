# Reactive Parameters

:::{note} Tutorial 1. **Reactive Parameters**
:icon: false

Panel and other projects in the HoloViz ecosystem all build on Param. Param provides a framework to add validation, documentation and interactivity to a project. It is similar to more modern projects such as Pydantic but focuses primarily on providing APIs that make it easy to express complex dependencies, reactivity and UI interactions.

Here we won't focus on how Param works but instead try to get you to understand the fundamentals that will allow you to effectively use Panel, express interactivity and reactivity in idiomatic ways and lastly how to structure your code to make it easily reusable and avoid callback hell.

By the end of this section you should:

- Have a clear understanding of the difference between the Parameter value and the Parameter object
- Use Parameter objects, bound functions and expressions as proxies or references for their current value
- Write Parameterized classes that encapsulate multiple components
:::

```{pyodide}
import time

import param
import panel as pn

pn.extension('tabulator')
```

## What is a Parameter?

Parameters are objects that express the semantics of a value of an attribute on an object, e.g. the `value` of `Widget`, i.e. whether it is a number or a string. Generally Parameters are broader than Python types because they deal with semantics not the specific representation of a value. A `Parameter` object also acts as a reference to the underlying value, which is incredibly useful when trying to add interactivity to a UI.

Let's look at a parameter definition, in this case for the Panel `TextInput` widget `value` parameter:

```python
class TextInput(Widget):

    ...

    value = param.String(default='', allow_None=True, doc="""
        Initial or entered text value updated when <enter> key is pressed.""")
```

A `Parameter` must be defined inside a class and that class must be a subclass of `Parameterized`. We can also see that it is of type `param.String`, defines a default of `''` and allows `None` value. It also has a docstring which gives us information about it.

To inspect all the parameters on a `Parameterized` class we can view the `repr` of the `.param` namespace:

```{pyodide}
pn.widgets.TextInput.param
```

### Accessing parameter values

Let's start by working with a `TextInput` widget:

```{pyodide}
text_input = pn.widgets.TextInput(value='A string!')

text_input
```

We can access the current value of the widget:

```{pyodide}
text_input.value
```

But we can also access the `Parameter` instance that acts as a proxy or reference for value:

```{pyodide}
text_input.param.value
```

Why and how to use such a reference is something we will discover a little bit later on.

### Setting parameter values

We can also set it to a new value:

```{pyodide}
text_input.value = 'Hello World!'
```

If we want to set multiple parameter values at once we should do so via the `.param.update` method. This ensures that anything that watches for changes on the parameters is only triggered once:

```{pyodide}
text_input.param.update(value='Updated!', width=85);
```

We can also use the `.param.update` method as a context manager to set a value temporarily:

```{pyodide}
with text_input.param.update(value='Temporary'):
    time.sleep(1)
```

### Validation

The primary purpose of parameters is to perform validation, e.g. if I try to assign an invalid value to a parameter, we will get an error:

```{pyodide}
import traceback as tb

try:
    text_input.value = 3.14
except ValueError as e:
    tb.print_exc()
```

## Parameters as references

Above we mentioned that `Parameter` objects can act as proxies or references for the underlying Parameter value. This is a powerful feature when trying to declare interactivity. Let us see what we mean by that with a simple example again based on the `TextInput` widget:

```{pyodide}
text_in = pn.widgets.TextInput(value='Hello world!')

text_out = pn.pane.Markdown(text_in.param.value)

pn.Column(text_in, text_out)
```

Note how we were able to pass the `value` parameter to the `Markdown` pane. If you attempt to type into the `TextInput` you'll notice that this is now automatically reflected by the Markdown output.

This also works when using it for other parameters, e.g. we can add a switch to toggle the visibility of some component:

```{pyodide}
visible = pn.widgets.Switch(value=True)

pn.Row(visible, pn.pane.Markdown('Hello World!', visible=visible))
```

Many parameters that accept a container such as a `dictionary` or `list` can also resolve references when they are nested, e.g. if we declare a `styles` dictionary one of the values can be a widget:

```{pyodide}
color = pn.widgets.ColorPicker(value='red')

md = pn.pane.Markdown('Some Text!', styles={'color': color})

pn.Row(color, md)
```

Notice that we passed in the widget object directly instead of the `.param.value`. This is possible because widgets are treated as a proxy of their `value` parameter just like a `Parameter` is treated as a proxy for current value.

## Transforming parameters

Often a widget or parameter value will not map directly to the output you want, e.g. let's say we wanted to add some formatting around the text before we render it or you might want to apply a whole pipeline of transformations to your data before it is displayed. Ordinarily you would have to restructure your code to achieve this but with Param you can write reactive expressions. Using `param.rx` (or .rx() on Parameter objects) you can wrap ordinary objects and/or parameters in a proxy that acts like the underlying object. Importantly the reactive expressions will also resolve other references passed to it.

Let's create a reactive format string and will in the value based on the input from a widget:

```{pyodide}
text_input = pn.widgets.TextInput(value='World')

text = pn.rx('**Hello {}!**').format(text_input)

md = pn.pane.Markdown(text)

pn.Row(text_input, md)
```

This is especially powerful when working with data where we might want to build a complex pipeline and add controls to the different stages. Let's load a `DataFrame` and make it reactive:

```{pyodide}
import pandas as pd

data_url = 'https://datasets.holoviz.org/windturbines/v1/windturbines.parq'

df = pd.read_parquet(data_url)

dfrx = pn.rx(df)

slider = pn.widgets.IntSlider(start=1, end=10)

df.head(2)
```

As you can see it acts just like the underlying DataFrame, allowing you to call methods on it and rendering like normal.

Now let's get a little more complex and write a whole pipeline that selects the desired columns, samples a number of random rows, and then applies some custom styling highlighting the rows with the highest value:

```{pyodide}
import numpy as np

cols  = pn.widgets.MultiChoice(
    options=df.columns.to_list(), value=['p_name', 't_state', 't_county', 'p_year', 'p_cap'], height=300
)
nrows = pn.widgets.IntSlider(start=5, end=20, step=5, value=15, name='Samples')
style = pn.rx('color: white; background-color: {color}')
color = pn.widgets.ColorPicker(value='darkblue', name='Highlight color')

def highlight_max(s, props=''):
    if s.dtype.kind not in 'f':
        return np.full_like(s, False)
    return np.where(s == np.nanmax(s.values), props, '')

styled_df = dfrx[cols].sample(nrows).style.apply(highlight_max, props=style.format(color=color), axis=0)

pn.pane.DataFrame(styled_df)
```

As you can see the Pandas code is identical to what you might have written if you were working with a regular DataFrame but you can now use widgets and even complex expressions as inputs.

### Exercise

Write a small app where you can scale the `font-size` of a `Markdown` pane with another widget, e.g. an `IntSlider`. The `font-size` can be set using the `styles` parameter.

:::{note} Hint
:class: dropdown

The `styles` parameter only accepts dictionaries of **strings** but `IntSlider` returns `int` types.
:::

## Writing Parameterized Classes

One last thing we should learn about working with Param in Panel is writing classes. This is useful for a number of reasons:

1. Organizing complex pieces of code and functionality
2. Writing reusable components made up of multiple Panel objects

A Parameterized class has to inherit from `param.Parameterized` and should declare one or more parameters. Here we will start building a `DataExplorer` by declaring two parameters:

1. `data`: Accepts a DataFrame
2. `page_size`: Controls the page size

```{pyodide}
import pandas as pd

class DataExplorer(param.Parameterized):

    data = param.DataFrame(doc="Stores a DataFrame to explore")

    page_size = param.Integer(default=10, doc="Number of rows per page.", bounds=(1, 20))

explorer = DataExplorer(data=df, page_size=5)
```

This explorer doesn't do anything yet so let's learn how we can turn the UI agnostic parameter declarations into a UI. For that purpose we will learn about `pn.Param`.

`pn.Param` allows mapping parameter declarations to widgets that allow editing the parameter value. There is a default mapping from `Parameter` type to the appropriate type but as long as the input matches this can be overridden.

Let's start with a simplest case:

```{pyodide}
pn.Param(explorer.param, widgets={'page_size': pn.widgets.IntInput})
```

Notice that each parameter was mapped to a widget appropriate for editing its value, i.e. the `data` was mapped to a `Tabulator` widget and the `page_size` was mapped to an `IntInput` widget.

If you try playing with the `page_size` widget you will notice that it doesn't actually do anything.

So next let's explicitly map the parameter to a widget using the `Widget.from_param` method. This will also let us provide additional options, e.g. to provide `start` and `end` values for the slider and layout options for the table.

```{pyodide}
pn.Column(
    pn.widgets.IntSlider.from_param(explorer.param.page_size, start=5, end=25, step=5),
    pn.widgets.Tabulator.from_param(explorer.param.data, page_size=explorer.param.page_size, sizing_mode='stretch_width')
)
```

The whole point of using classes is to encapsulate the logic on it, so let's do that. For that we can use a slight extension of the `Parameterized` class that makes the object behave as if it was a regular Panel object. The `Viewer` class does exactly that, all you have to do is implement the `__panel__` method:

```{pyodide}
from panel.viewable import Viewer

class DataExplorer(Viewer):

    data = param.DataFrame(doc="Stores a DataFrame to explore")

    page_size = param.Integer(default=10, doc="Number of rows per page.", bounds=(1, None))

    def __panel__(self):
        return pn.Column(
            pn.widgets.IntSlider.from_param(self.param.page_size, start=5, end=25, step=5),
            pn.widgets.Tabulator.from_param(self.param.data, page_size=self.param.page_size, sizing_mode='stretch_width')
        )

DataExplorer(data=df)
```

### Exercise

Extend the `DataExplorer` class by adding parameters to control the `theme` and toggling the `show_index` option
