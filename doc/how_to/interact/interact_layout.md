# Customize Layout with Interact

This guide addresses how to autogenerate widgets for function arguments with Panel `interact`.

First, let's create a function and call `interact` to return a Panel containing the widgets and the display output.

```{pyodide}
import panel as pn
pn.extension() # for notebook

def f(x, y, z):
    return x, y, z

layout = pn.interact(f, x=True, y=10, z='text')

layout
```

Now, by indexing into this Panel we can lay out the objects precisely how we want.

```{pyodide}
pn.Row(pn.Column('First Column', layout[0][0], layout[0][1], width=200),
       pn.Column('Second Column', layout[0][2], width=200),
       pn.Column('Returns', layout[1]),
      )
```

We can always print the Panel contents to check the indexing:

```{pyodide}
layout.pprint()
```
