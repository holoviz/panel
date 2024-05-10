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
export function render({ children }) {
    const containerID = `id-${crypto.randomUUID()}`;;
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
js_layout = LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
js_layout.servable()
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
            <div ref=${ref => ref && ref.appendChild(children.object)}>
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
html_layout = LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
html_layout.servable()
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
react_layout = LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
react_layout.servable()
```

::::

:::::

Lets verify the layout will automatically update when the `object` is changed.

:::::{tab-set}

::::{tab-item} JavaScript

```{pyodide}
html = pn.pane.Markdown("A **markdown** pane!", name="Markdown")
radio_button_group = pn.widgets.RadioButtonGroup(
    options=["Dial", "Markdown"],
    value="Dial",
    name="Select the object to display",
    button_type="success", button_style="outline"
)

@pn.depends(radio_button_group, watch=True)
def update(value):
    if value == "Dial":
        js_layout.object = dial
    else:
        js_layout.object = html

radio_button_group.servable()
```

::::

::::{tab-item} `html`

```{pyodide}
html = pn.pane.Markdown("A **markdown** pane!", name="Markdown")
radio_button_group = pn.widgets.RadioButtonGroup(
    options=["Dial", "Markdown"],
    value="Dial",
    name="Select the object to display",
    button_type="success", button_style="outline"
)

@pn.depends(radio_button_group, watch=True)
def update(value):
    if value == "Dial":
        html_layout.object = dial
    else:
        html_layout.object = html

radio_button_group.servable()
```

::::

::::{tab-item} React

```{pyodide}
html = pn.pane.Markdown("A **markdown** pane!", name="Markdown")
radio_button_group = pn.widgets.RadioButtonGroup(
    options=["Dial", "Markdown"],
    value="Dial",
    name="Select the object to display",
    button_type="success", button_style="outline"
)

@pn.depends(radio_button_group, watch=True)
def update(value):
    if value == "Dial":
        react_layout.object = dial
    else:
        react_layout.object = html

radio_button_group.servable()
```

::::

:::::
