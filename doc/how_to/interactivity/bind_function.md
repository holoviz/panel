# Add interactivity to a function

This guide addresses how to make your functions interactive by binding widgets to them. This is done with the use of `pn.bind`, which allows binding the value of a widget to a function or method.

---

The recommended approach to adding interactivity to your applications is by writing reactive functions or methods. To discover how to write one of these first, we need a function.

Let's start by creating a function. The function takes an argument `number` and will return a string of stars equal to the number:

```{pyodide}
def star_creator(number):
    return "⭐" * number

star_creator(5)
```

Calling a function repeatedly with different arguments is not very interactive, so as a second step we will create a widget. Here we have chosen the `pn.widgets.IntSlider` with a value of 5 and a range between 1 and 10:

```{pyodide}
import panel as pn

pn.extension()

slider = pn.widgets.IntSlider(value=5, start=1, end=10)
slider
```


To make our `star_creator` function interactive we can now bind the widget to the function and add it to a layout together with the `slider`:

```{pyodide}
interactive_star_creator = pn.bind(star_creator, slider)

pn.Column(slider, interactive_star_creator)
```

:::{note}
`pn.bind` works very similarly to Python's [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial), except that it automatically resolves the current value of any widgets, *Parameters* and other bound functions that are passed as arguments.
:::

Internally the layout will create a so called `ParamFunction` component to wrap the interactive function. This wrapper component will re-evaluate and update the output whenever the inputs to the function change.

## Related Resources

- Learn [how to use reactive functions to update components](bind_component.md)
- Learn [how to use reactive generators to generate interactive components ](bind_generators.md)
- Understand [Param](../../explanation/dependencies/param.md)
