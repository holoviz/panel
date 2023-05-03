# Make your functions interactive

This guide addresses how to make your functions interactive by binding them to widgets. This is done with the use of `pn.bind`, which binds a function or method to the value of a widget.

---

## Bind your functions to widgets
Making a function interactive is easy to do in Panel. First, you need a function, then create widgets, and finally,  bind the widgets to the function.

First, let's create a function; this function takes an argument `number` and will return a string of stars equal to the number:

```{pyodide}
def star_creator(number):
    return "⭐" * number

star_creator(5)
```

The second step is to create the widget. Here, we have chosen the `pn.widgets.IntSlider` with a value of 5 and can have values between 1 and 10.


```{pyodide}
import panel as pn

pn.extension()

slider = pn.widgets.IntSlider(value=5, start=1, end=10)
slider
```

You can then bind the widget to the function and create an interactive function using `pn.bind`.


```{pyodide}
interactive_star_creator = pn.bind(star_creator, slider)
```

The final step is to make a layout of the widget and the interactive function. Here `pn.Column` is chosen, but another layout could also have been used.


```{pyodide}
pn.Column(slider, interactive_star_creator)
```

## Related Resources
