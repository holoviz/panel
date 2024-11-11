# Fix Values with `Interact`

This guide addresses how to fix the value for certain arguments with Panel `interact`.

```{admonition} Prerequisites
1. The [How to > Generate Widgets for Function Arguments](interact_basics) guide covers how to generate widgets for function arguments with Panel interact.
```

---

First, let's declare a simple function.

```{pyodide}
import panel as pn
from panel._interact import fixed
pn.extension() # for notebook

def f(x, y):
    return x, y
```

Now, call `interact` using the `panel._interact.fixed` function to fix one of the values:

```{pyodide}
pn.interact(f, x=1, y=fixed(10))
```

## Related Resources
