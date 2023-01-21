# ``Interact`` with Functions

The `interact` approach provides a very simple way to autogenerate widgets linked to function arguments.

First, let's declare a simple function.

```{pyodide}
import panel as pn
pn.extension() # for notebook

def f(a, b, c, d):
    return a, b, c, d
```

Next, let's call `interact` with the function and it's arguments. The values of the arguments will be inspected to infer an appropriate set of widgets to autogenerate. Changing any of the resulting widgets will cause the function to be re-run, updating the displayed output.

```{pyodide}
pn.interact(f, a=True, b=10, c=(-10, 10, 0.1, 5.4), d='text')
```

Alternatively, this `interact` approach can be used as a decorator:

```{pyodide}
@pn.interact(a=True, b=10, c=(-10, 10, 0.1, 5.4), d='text')
def f(a, b, c, d):
    return a, b, c, d
f
```

## Further Resources

- Read [Background > Interact with Functions] for context.
- See [How-to > Autogenerate Widgets for Functions] for solutions.
- Consult [Reference > panel.interact] for technical details.
