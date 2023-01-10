# Access and Set Widget Values

In addition to other parameters that govern widget behavior and appearance, Widget objects have a ``value`` parameter that can be used to access the current value state.

```{pyodide}
import panel as pn
pn.extension()

widget = pn.widgets.TextInput(name='A widget', value='A string')
widget
```

Once a widget has been initiated, we can access its value programmatically:

```{pyodide}
widget.value
```

We can also use this value parameter to set the widget value:

```{pyodide}
widget.value = '3'
```

:::{admonition} Widget Background
:class: info

Learn more about Widgets in the [Background for Components](../background/components/components_overview.md#Widgets)
:::
