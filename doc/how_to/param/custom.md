# Declare Custom Widgets

This guide addresses how to extend Param based UIs with custom widgets.

```{admonition} Prerequisites
1. The [How to > Generate Widgets from Parameters](./uis.md) guide demonstrates the default case of automatically generating widgets.
```

---

## Custom type

`Param Parameters` can automatically be turned into widgets because Panel maintains a mapping between `Parameter` types and widget types. However, sometimes the default widget does not provide the most convenient UI and we want to provide an explicit hint to Panel to tell it how to render a `Parameter`. Using the `widgets` keyword we can declare a mapping between the parameter name and the type of widget that is desired (as long as the widget type supports the types of values held by the parameter type).

As an example, we can map a string and a number Selector to a `RadioButtonGroup` and `DiscretePlayer` respectively.

```{pyodide}
import panel as pn
import param

pn.extension()

class CustomExample(param.Parameterized):
    """An example Parameterized class"""

    select_string = param.Selector(objects=["red", "yellow", "green"])
    autocomplete_string = param.Selector(default='', objects=["red", "yellow", "green"], check_on_set=False)
    select_number = param.Selector(objects=[0, 1, 10, 100])


pn.Param(CustomExample.param, widgets={
    'select_string': pn.widgets.RadioButtonGroup,
    'autocomplete_string': pn.widgets.AutocompleteInput,
    'select_number': pn.widgets.DiscretePlayer}
)
```

Also, it's possible to pass arguments to the widget in order to customize it. Instead of passing the widget, pass a dictionary with the desired options. Use the ``widget_type`` keyword to map the widget.

Taking up the previous example.

```{pyodide}
pn.Param(CustomExample.param, widgets={
    'select_string': {'widget_type': pn.widgets.RadioButtonGroup, 'button_type': 'success'},
    'autocomplete_string': {'widget_type': pn.widgets.AutocompleteInput, 'placeholder': 'Find a color...'},
    'select_number': pn.widgets.DiscretePlayer}
)
```

However it is also possible to explicitly construct a widget from a parameter using the `.from_param` method, which makes it easy to override widget settings using keyword arguments:


```{pyodide}
pn.widgets.RadioBoxGroup.from_param(CustomExample.param.select_string, inline=True)
```

## Custom name

By default, a param Pane has a title that is derived from the class name of its `Parameterized` object. Using the ``name`` keyword we can set any title to the pane, e.g. to improve the user interface.


```{pyodide}
pn.Param(CustomExample.param, name="Custom Name")
```

## Custom Sort

You can sort the widgets alphabetically by setting `sort=True`


```{pyodide}
pn.Param(CustomExample.param, sort=True, name="Sort by Label Example")
```

You can also specify a custom sort function that takes the (parameter name, Parameter instance) as input.


```{pyodide}
def sort_func(x):
    return len(x[1].label)

pn.Param(CustomExample.param, sort=sort_func, name="Sort by Label Length Example")
```

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
