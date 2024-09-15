# Add reactivity to components

This guide addresses how to bind *Parameters* and bound functions on components.

:::{versionadded} 1.0.0
Bind *Parameters*, widgets and bound functions to component *Parameters*.
:::

---

The power to binding *Parameters*, widgets and interactive functions to component *Parameters* can be used with all of Panel's widgets and panes. This provides a powerful way to add interactivity to an application and update specific *Parameters* without writing callbacks.

Let's start with an using existing components to give you an idea of the power behind this. In this example we bind the value of a slider widget to the `page_size` *Parameter* of the [Tabulator](../../reference/widgets/Tabulator) widget. This will allow you to change the page size of the table with the slider:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension("tabulator")

df = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")

slider = pn.widgets.IntSlider(value=5, start=1, end=10, name='page_size')
tabulator = pn.widgets.Tabulator(df, page_size=slider, pagination="remote")

pn.Column(slider, tabulator)
```

## Binding bound function on components

```{admonition} Prerequisites
Read the [How to > Make your functions interactive](./bind_function) guide to learn how to bind functions.
```

Often times the value of a widget or *Parameter* will not map directly onto the *Parameter* you want to set. In these cases, you can write a reactive function (using `pn.bind`), which transforms the values of the inputs.

Let's say we have a function that takes a string and a number as input:

```{pyodide}
def object_creator(string, number):
    return string * number

object_creator('🐘', 5)
```

Now we can bind `IntSlider` and the `Select` widgets to the `object_creator` to create an interactive string. Once we have a reactive function we can pass it to a component, e.g. `Markdown` to render this:

```{pyodide}
slider = pn.widgets.IntSlider(value=5, start=1, end=10)
select = pn.widgets.Select(value="⭐", options=["⭐", "🐘"])

iobject = pn.bind(object_creator, select, slider)

pn.Row(slider, select, pn.pane.Markdown(iobject))
```

This approach is preferred over rendering reactive functions directly because it is more efficient and updates only the specific *Parameters* that are being changed.

If you want to update multiple *Parameters* at the same time you can pass a reactive function (or **Parameter**) as the `refs` keyword argument. The function (or **Parameter**) must return a dictionary of parameters to update, e.g. let's say you wanted to write a function that returns both


```{pyodide}
slider = pn.widgets.IntSlider(value=5, start=1, end=10, name='Number')
select = pn.widgets.RadioButtonGroup(value="⭐", options=["⭐", "🐘"], name='String', align='center')
size = pn.widgets.IntSlider(value=12, start=6, end=24, name='Size')

def refs(string, number, size):
    return {
        'object': string * number,
        'styles': {'font-size': f'{size}pt'}
    }

irefs = pn.bind(refs, select, slider, size)

pn.Row(slider, size, select, pn.pane.Markdown(refs=irefs))
```

In this way we can update both the current `object` and the `styles` **Parameter** of the `Markdown` pane simultaneously.

## Related Resources

- Learn [how to use generators with `bind`](bind_generators.md)
- Understand [Param](../../explanation/dependencies/param.md)
