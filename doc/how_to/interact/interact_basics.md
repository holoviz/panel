# Generate widgets for function arguments

This guide addresses how to generate widgets for function arguments with Panel `interact`.

---

First, let's declare a simple function that just returns the arguments:

```{pyodide}
import panel as pn
pn.extension() # for notebook

def foo(a, b, c, d, e, f):
    return f'Arguments: {a, b, c, d, e, f}'
```

Next, let's call `interact` with the function and it's arguments. The values of the arguments will be inspected to infer an appropriate set of widgets to autogenerate. After running the code block, changing any of the resulting widgets will cause the function to be re-run, updating the displayed output.

```{pyodide}
pn.interact(
    foo,
    a=True,
    b=10,
    c=(-10, 10, 0.1, 5.4),
    d='text',
    e=['apples', 'oranges'],
    f=dict([('first', 10), ('second', 20)])
)
```

We can also explicitly pass a widget as one of the values:

```{pyodide}
def create_block(c):
    return pn.pane.HTML(width=100, height=100, styles={'background': c})

color_widget = pn.widgets.ColorPicker(name='Color', value='#4f4fdf')

pn.interact(create_block, c=color_widget)
```

Alternatively, this `interact` approach can be used as a decorator:

```{pyodide}
@pn.interact(x=True, y=10)
def bar(x, y):
    return x, y
bar
```

Let's put this all together:

```{pyodide}
import panel as pn
pn.extension() # for notebook

def foo(a, b, c, d, e, f):
    return f'Arguments: {a, b, c, d, e, f}'

pn.interact(
    foo,
    a=True,
    b=10,
    c=(-10, 10, 0.1, 5.4),
    d='text',
    e=['apples', 'oranges'],
    f=dict([('first', 10), ('second', 20)])
)

def create_block(c):
    return pn.pane.HTML(width=100, height=100, styles={'background': c})

color_widget = pn.widgets.ColorPicker(name='Color', value='#4f4fdf')

pn.interact(create_block, c=color_widget)
```

## Related Resources
