# Align Components

This guide addresses how to customize the alignment between components.

---

The `align` parameter controls how components align vertically and horizontally. It supports 'start', 'center', and 'end' values and can be set for both horizontal and vertical directions at once or for each separately by passing in a tuple of the form `(horizontal, vertical)`.

One common use-case where alignment is important is when placing multiple items with different heights in a `Row`. Let's create a big button and align a slider to the center of the button using `align=center`:

```{pyodide}
import panel as pn
pn.extension() # for notebook

button = pn.widgets.Button(name='Test', height=100)
slider = pn.widgets.IntSlider(align='center')

pn.Row(button, slider, styles={'background': 'lightgrey'})
```

Now, let's look at aligning components in a grid with an instance of passing in `(horizontal, vertical)`:

```{pyodide}
pn.GridBox(
    pn.widgets.Button(name='Test', height=100),
    pn.widgets.IntSlider(align='center'),
    pn.widgets.TextInput(name='Test', height=100, width=100, align=('center')),
    pn.widgets.TextInput(width=150, align=('start', 'end')),
    ncols=2,
    styles={'background': 'lightgrey'}
)
```

---

## Related Resources
