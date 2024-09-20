# Use abbreviations to generate widgets

This guide addresses how to use abbreviations to create widgets with Panel `interact`.

```{admonition} Prerequisites
1. The [How to > Generate Widgets for Function Arguments](interact_basics) guide provides an overview of how to generate widgets for function arguments with Panel interact.
```

___

At the most basic level, `interact` autogenerates UI controls for function arguments, and then calls the function with those arguments when you manipulate the controls interactively.

To use `interact`, you need to define a function that you want to explore. Here is a function that return its argument.

```{pyodide}
import panel as pn
from panel import widgets

pn.extension() # for notebook

def f(x):
    return x
```

When you pass this function to `interact` along with `x=10`, a slider is generated and bound to the function parameter, such that when you interact with the widget, the function is called.

```{pyodide}
pn.interact(f, x=10)
```

When you pass an integer-valued keyword argument of `10` (`x=10`) to `interact`, it generates an integer-valued slider control with a range of `[-10,+3*10]`. In this case, `10` is an *abbreviation* for an actual slider widget:

```{pyodide}
slider_widget = widgets.IntSlider(start=-10,end=30,step=1,value=10)
```

In fact, we can get the same result if we pass this `IntSlider` as the keyword argument for `x`:

```{pyodide}
pn.interact(f, x=slider_widget)
```

This examples clarifies how `interact` processes its keyword arguments:

1. If the keyword argument is a `Widget` instance with a `value` attribute, that widget is used. Any widget with a `value` attribute can be used, even custom ones.
2. Otherwise, the value is treated as a *widget abbreviation* that is converted to a widget before it is used.

The following table gives an overview of different widget abbreviations:

<table class="table table-condensed table-bordered">
  <tr><td><strong>Keyword argument</strong></td><td><strong>Widget</strong></td></tr>
  <tr><td>True or False</td><td>Checkbox</td></tr>
  <tr><td>'Hi there'</td><td>Text</td></tr>
  <tr><td>value or (min,max,[step,[value]]) if integers are passed</td><td>IntSlider</td></tr>
  <tr><td>value or (min,max,[step,[value]]) if floats are passed</td><td>FloatSlider</td></tr>
  <tr><td>['orange','apple'] or {'one':1,'two':2}</td><td>Dropdown</td></tr>
</table>
Note that a dropdown is used if a list or a dict is given (signifying discrete choices), and a slider is used if a tuple is given (signifying a range).

You have seen how the IntSlider widget works above. Here, more details about the different abbreviations for sliders and dropdowns are given.

If a 2-tuple of integers is passed `(min,max)`, an integer-valued slider is produced with those minimum and maximum values (inclusively). In this case, the default step size of `1` is used.


```{pyodide}
pn.interact(f, x=(0, 4))
```

If a 3-tuple of integers is passed `(min,max,step)`, the step size can also be set.


```{pyodide}
pn.interact(f, x=(0, 8, 2))
```

A float-valued slider is produced if the elements of the tuples are floats. Here the minimum is `0.0`, the maximum is `10.0` and step size is `0.1` (the default).


```{pyodide}
pn.interact(f, x=(0.0, 10.0))
```

The step size can be changed by passing a third element in the tuple.


```{pyodide}
pn.interact(f, x=(0.0, 10.0, 0.01))
```

For both integer and float-valued sliders, you can pick the initial value of the widget by supplying a default keyword argument when you define the underlying Python function. Here we set the initial value of a float slider to `5.5`.


```{pyodide}
@pn.interact(x=(0.0, 20.0, 0.5))
def h(x=5.5):
    return x

h
```

You can also set the initial value by passing a fourth element in the tuple.


```{pyodide}
pn.interact(f, x=(0.0, 20.0, 0.5, 5.5))
```

Use `None` as the third element to just set min, max, and value.


```{pyodide}
pn.interact(f, x=(0.0, 20.0, None, 5.5))
```

Dropdown menus are constructed by passing a list of strings. In this case, the strings are both used as the names in the dropdown menu UI and passed to the underlying Python function.


```{pyodide}
pn.interact(f, x=['apples', 'oranges'])
```

When working with numeric data ``interact`` will automatically add a discrete slider:


```{pyodide}
pn.interact(f, x=dict([('one', 10), ('two', 20)]))
```

## Related Resources
