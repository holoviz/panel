# Create Layouts With ESM Components

In this guide we will show you how to build custom layouts `JSComponent`, `ReactComponent` or `PreactComponent`.

## Layout a single Panel Component

You can layout a single Panel component as follows.

:::::{tab-set}

::::{tab-item} `JSComponent`

```{pyodide}
import panel as pn
from panel.custom import JSComponent, Child

pn.extension()

class LayoutSingleObject(JSComponent):
    object = Child()

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

::::{tab-item} `ReactComponent`

```{pyodide}
import panel as pn

from panel.custom import Child, ReactComponent

pn.extension()

class LayoutSingleObject(ReactComponent):
    object = Child()

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

::::{tab-item} `PreactComponent`

```{pyodide}
import panel as pn

from panel.custom import Child, PreactComponent

pn.extension()

class LayoutSingleObject(PreactComponent):
    object = Child()

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
preact_layout = LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
preact_layout.servable()
```

::::

:::::

Lets verify the layout will automatically update when the `object` is changed.

:::::{tab-set}

::::{tab-item} `JSComponent`

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

::::{tab-item} `ReactComponent`

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

::::{tab-item} `PreactComponent`

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
        preact_layout.object = dial
    else:
        preact_layout.object = html

radio_button_group.servable()
```

::::

:::::
