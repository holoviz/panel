# Create Layouts With ReactiveESM

In this guide we will show you how to build custom layouts using HTML and `ReactiveESM`.

## Layout a single parameter

You can layout a single object as follows.

```{pyodide}
import panel as pn
import param

pn.extension()

class LayoutSingleObject(pn.ReactiveESM):
    object = param.ClassSelector(class_=pn.viewable.Viewable, allow_refs=None)

    _esm = """
    export function render({ data }) {
        let div = document.createElement("div");
        div.innerHTML = `Hello`;
        return div
    }
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
