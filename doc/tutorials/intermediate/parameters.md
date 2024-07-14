# Reactive Parameters

Welcome to the world of reactive parameters in Panel! In this section, we'll delve into the powerful capabilities offered by Parameters in the [HoloViz](https://holoviz.org/) ecosystem.

## Understanding Parameters

Panel and other projects in the [HoloViz](https://holoviz.org/) ecosystem build on the foundation provided by [Param](https://param.holoviz.org/). Param offers a robust framework for adding validation, documentation, and interactivity to projects. Similar to projects like [Pydantic](https://docs.pydantic.dev/latest/) in some aspects, but Param focuses on providing APIs that simplify the expression of complex dependencies, reactivity, and UI interactions.

In this section, we won't delve into the inner workings of Param but rather focus on understanding the fundamentals. By the end of this section, we will:

- Understand the difference between the Parameter value and the Parameter object.
- Know how to use Parameter objects, bound functions, and reactive expressions as proxies or references for their current value.

```{pyodide}
import panel as pn

pn.extension('tabulator')
```

## Exploring Parameters

Parameters serve as objects expressing the semantics of a value of an attribute on an object, encompassing not only Python types but also broader semantics.

Let's define a simple `Parameterized` class with a `value` Parameter:

```{pyodide}
import param

class Text(param.Parameterized):
    value = param.String(default='', allow_None=True, doc="The text value")
```

Now, let's create an instance and examine its current value:

```{pyodide}
text = Text(value="Are you a Python programmer? If so, you need Param!")

text.value
```

We can also inspect its Parameter *instance*:

```{pyodide}
text.param.value
```

## The Utility of Parameters

Parameters act as references to underlying values, making them invaluable for enhancing UI interactivity.

Parameters imbue validation, documentation, and interactivity into Panel, with most Panel components built as `Parameterized` classes with Parameters.

For instance, consider the `value` Parameter of the Panel `TextInput` widget:

```python
class TextInput(pn.widgets.Widget):
    ...

    value = param.String(default='', allow_None=True, doc="""
        Initial or entered text value updated when <enter> key is pressed.""")
```

To explore all parameters on a `Parameterized` class, we inspect the `.param` namespace:

```{pyodide}
pn.widgets.TextInput.param
```

## Utilizing Parameters

Let's now delve into practical usage scenarios.

### Accessing Parameter Values

Consider working with a `TextInput` widget:

```{pyodide}
text_input = pn.widgets.TextInput(value='A string!')

text_input
```

We can access its current value:

```{pyodide}
text_input.value
```

Additionally, we can access the `Parameter` instance, acting as a proxy or reference for the value:

```{pyodide}
text_input.param.value
```

### Setting Parameter Values

We can set it to a new value:

```{pyodide}
text_input.value = 'Hello World!'
```

For setting multiple parameter values, use the `.param.update` method:

```{pyodide}
text_input.param.update(value='Updated!', width=85);
```

Or use it as a context manager for temporary value setting:

```{pyodide}
from time import sleep

with text_input.param.update(value='Temporary'):
    sleep(1)
```

### Validation

Parameters perform validation, raising errors for invalid assignments:

```{pyodide}
import traceback as tb

try:
    text_input.value = 3.14
except ValueError as e:
    tb.print_exc()
```

## Parameters as References

Parameters serve as proxies for underlying Parameter values, facilitating interactive declarations.

Consider a simple example using the `TextInput` widget:

```{pyodide}
import panel as pn

pn.extension()

text_in = pn.widgets.TextInput(value='Hello world!')

text_out = pn.pane.Markdown(text_in.param.value)

pn.Column(text_in, text_out).servable()
```

Observe how changes in `TextInput` are automatically reflected in the Markdown output.

This also works when using it for other parameters, e.g. we can add a switch to toggle the visibility of some component:

```{pyodide}
visible = pn.widgets.Switch(value=True)

pn.Row(visible, pn.pane.Markdown('Hello World!', visible=visible)).servable()
```

Many parameters that accept a container such as a `dictionary` or `list` can also resolve references when they are nested, e.g. if we declare a `styles` dictionary one of the values can be a widget:

```{pyodide}
color = pn.widgets.ColorPicker(value='red')

md = pn.pane.Markdown('Some Text!', styles={'color': color})

pn.Row(color, md).servable()
```

Notice that we passed in the widget object directly instead of the `.param.value`. This is possible because widgets are treated as a proxy of their `value` parameter just like a `Parameter` is treated as a proxy for current value.

## Transforming Parameters

Transforming parameters allows for complex value processing pipelines, offering immense flexibility.

For instance, we can create a reactive format string, filling in values based on widget input:

```{pyodide}
import panel as pn

pn.extension()

text_input = pn.widgets.TextInput(value='World')

text = pn.rx('**Hello {}!**').format(text_input)

md = pn.pane.Markdown(text)

pn.Row(text_input, md).servable()
```

Similarly, we can make a DataFrame reactive:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'

df = pn.cache(pd.read_csv)(data_url)

dfrx = pn.rx(df)

dfrx.head(2)
```

Please explore the potential by replacing `2` with an instance of an `IntSlider`.

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'

df = pn.cache(pd.read_csv)(data_url)

dfrx = pn.rx(df)

slider = pn.widgets.IntSlider(value=2, start=1, end=10)
pn.panel(dfrx.head(slider)).servable()
```

:::

Now let's get a little more complex and write a whole pipeline that selects the desired columns, samples a number of random rows, and then applies some custom styling highlighting the rows with the highest value:

```{pyodide}
import pandas as pd
import panel as pn
import numpy as np

pn.extension()

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'
df = pn.cache(pd.read_csv)(data_url)

dfrx = pn.rx(df)

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

pn.pane.DataFrame(styled_df).servable()
```

As you can see, the Pandas code is identical to what you might have written if you were working with a regular DataFrame. However, now you can use widgets and even complex expressions as inputs.

Try replacing `pn.pane.DataFrame` with `pn.panel` to display an interactive component with widgets.

:::{dropdown} Solution

```{pyodide}
import pandas as pd
import panel as pn
import numpy as np

pn.extension()

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'
df = pn.cache(pd.read_csv)(data_url)

dfrx = pn.rx(df)

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

pn.panel(styled_df).servable()
```

:::

### Exercise: Scale the Font Size

Write a small app where you can scale the `font-size` of a `Markdown` pane with another widget, e.g. an `IntSlider`. The `font-size` can be set using the `styles` parameter.

:::{hint}

- The `styles` parameter only accepts dictionaries of **strings** but `IntSlider` returns `int` types.
- The `font-size` value should be a string value in pixels, eg. `"15px"` is a valid `font-size`.

:::

:::{dropdown} Solution 1: Reactive String Formatting

```{pyodide}
import panel as pn

pn.extension()

intslider = pn.widgets.IntSlider(value=10, start=5, end=100, step=10, name="Font Size")

styles_rx = {"font-size": pn.rx("{value}px").format(value=intslider)}
markdown = pn.pane.Markdown("We love dataviz!", styles=styles_rx)
pn.Column(intslider, markdown).servable()
```

:::

:::{dropdown} Solution 2: Reactive Function

```{pyodide}
import panel as pn

pn.extension()

intslider = pn.widgets.IntSlider(value=10, start=5, end=100, step=10, name="Font Size")

def styles(font_size):
    return {"font-size": f"{font_size}px"}

styles_rx = pn.rx(styles)(intslider)
markdown = pn.pane.Markdown("We love dataviz!", styles=styles_rx)
pn.Column(intslider, markdown).servable()
```

:::

::::{dropdown} Solution 3: Bound Function

```{pyodide}
import panel as pn

pn.extension()

intslider = pn.widgets.IntSlider(value=10, start=5, end=100, step=10, name="Font Size")

def styles(font_size):
    return {"font-size": f"{font_size}px"}

styles_bn = pn.bind(styles, font_size=intslider)
markdown = pn.pane.Markdown("We love dataviz!", styles=styles_bn)
pn.Column(intslider, markdown).servable()
```

:::{note}

`pn.bind` is the predecessor of `pn.rx`. We recommend using `pn.rx` over `pn.bind` as it's much more flexible and efficient. We include this example because you will find lots of examples in the Panel documentation and in the Panel community using `pn.bind`.

:::

::::

## Recommended Reading

To harness the full potential of [Param](https://param.holoviz.org/) and Reactive Parameters in Panel, we recommend studying the [Param User Guide](https://param.holoviz.org/user_guide/index.html) and the [`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.md).

## Recap

[Param](https://param.holoviz.org) serves as the backbone of Panel, providing a robust framework for adding validation, documentation, and interactivity. By grasping the fundamentals discussed here, you'll be well-equipped to leverage Panel's interactivity and reactivity effectively.

Now, we should be able to:

- Clearly understand the distinction between Parameter values and Parameter objects.
- Use Parameter objects, bound functions, and expressions as proxies or references for their current value.

## Resources

### Explanation

- [Panels APIs](../../explanation/api/index.md)

### How-To

- [Make your component interactive](../../how_to/interactivity/index.md)

### Component Gallery

- [ReactiveExpr](../../reference/panes/ReactiveExpr.md)
