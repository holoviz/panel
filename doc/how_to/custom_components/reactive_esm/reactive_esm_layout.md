# Create Layouts With ReactiveESM

In this guide we will show you how to build custom layouts using HTML and `ReactiveESM`.

## Layout a single parameter

You can layout a single object as follows.

```{pyodide}
import panel as pn
import param

pn.extension()

class LayoutSingleObject(pn.reactiveESM):
    object = param.Parameter(allow_refs=False)

    _template = """
    <div>
        <h1>Temperature</h1>
        <h2>A measurement from the sensor</h2>
        <div id="object">${object}</div>
    </div>
"""

dial = pn.widgets.Dial(
    name="°C",
    value=37,
    format="{value}",
    colors=[(0.40, "green"), (1, "red")],
    bounds=(0, 100),
)
LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
).servable()
```

:::{note}
