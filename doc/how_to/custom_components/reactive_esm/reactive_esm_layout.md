# Create Layouts With ReactiveESM

In this guide we will show you how to build custom layouts using HTML and `ReactiveESM`.

## Layout a single Panel Component

You can layout a single Panel component as follows.

:::::{tab-set}

::::{tab-item} JavaScript

```{pyodide}
import param
import panel as pn

pn.extension()

class LayoutSingleObject(pn.ReactiveESM):
    object = param.ClassSelector(class_=pn.viewable.Viewable, allow_refs=False)

    _esm = """
import { v4 } from 'https://esm.sh/uuid';

export function render({ children }) {
    const containerID = `id-${v4()}`;
    const div = document.createElement("div");
    div.innerHTML = `
    <div>
        <h1>Temperature</h1>
        <h2>A measurement from the sensor</h2>
        <div id="${containerID}">...</div>
    </div>`;
    const container = div.querySelector(`#${containerID}`);
    container.appendChild(children.object)
    return div;
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

::::

::::{tab-item} `html`

```{pyodide}
import param

import panel as pn

pn.extension()


class LayoutSingleObject(pn.ReactiveESM):
    object = param.ClassSelector(class_=pn.viewable.Viewable, allow_refs=False)

    _esm = """
export function render({ children, html }) {
    return html`
        <div>
            <h1>Temperature</h1>
            <h2>A measurement from the sensor</h2>
            <div>
                ${children.object}
            </div>
        </div>`;
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

::::

::::{tab-item} React

```{pyodide}
import param
import panel as pn

pn.extension()

class LayoutSingleObject(pn.ReactiveESM):
    object = param.ClassSelector(class_=pn.viewable.Viewable, allow_refs=False)

    _esm = """
export function render({ children }) {
    return (
        <div>
            <h1>Temperature</h1>
            <h2>A measurement from the sensor</h2>
            <div>
                {children.object}
            </div>
        </div>
    );
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

::::

:::::
