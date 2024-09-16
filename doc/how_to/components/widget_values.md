# Access and Set Widget Values

This guide addresses how to access and set widget values.

---

In addition to other parameters that govern widget behavior and appearance, Widget objects have a ``value`` parameter that can be used to access the current value state.


Let's first create a `TextInput` widget:

```{pyodide}
import panel as pn
pn.extension() # for notebook

widget = pn.widgets.TextInput(name='A widget', value='A string')
widget
```

Now we can programmatically access its value:

```{pyodide}
widget.value
```

We can also use this value parameter to set the widget value:

```{pyodide}
widget.value = '3'
```

---

## Related Resources

- Learn more about Panes in [Explanation > Components](../../explanation/components/components_overview#panes).
