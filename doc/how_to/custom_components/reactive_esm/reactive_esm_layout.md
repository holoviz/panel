# Create Custom Layouts

In this guide we will show you how to build custom, reusable layouts using `Viewer`, `JSComponent` or `ReactComponent`.

## Layout a single Panel Component

You can layout a single `object` as follows.

:::::{tab-set}

::::{tab-item} `Viewer`

```{pyodide}
import panel as pn
from panel.custom import Child
from panel.viewable import Viewer, Layoutable

pn.extension()


class LayoutSingleObject(Viewer, Layoutable):
    object = Child(allow_refs=False)

    def __init__(self, **params):
        super().__init__(**params)

        header = """
# Temperature
## A Measurement from the Sensor
        """

        self._layout = pn.Column(
            pn.pane.Markdown(header, height=100, sizing_mode="stretch_width"),
            self._object,
            **Layoutable.param.params(),
        )

    def __panel__(self):
        return self._layout

    @pn.depends("object")
    def _object(self):
        return self.object


dial = pn.widgets.Dial(
    name="°C",
    value=37,
    format="{value}",
    colors=[(0.40, "green"), (1, "red")],
    bounds=(0, 100),
)
py_layout = LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
py_layout.servable()
```

::::

::::{tab-item} `JSComponent`

```{pyodide}
import panel as pn
from panel.custom import JSComponent, Child

pn.extension()

class LayoutSingleObject(JSComponent):
    object = Child(allow_refs=False)

    _esm = """
export function render({ model }) {
    const containerID = `id-${crypto.randomUUID()}`;;
    const div = document.createElement("div");
    div.innerHTML = `
    <div>
        <h1>Temperature</h1>
        <h2>A measurement from the sensor</h2>
        <div id="${containerID}">...</div>
    </div>`;
    const container = div.querySelector(`#${containerID}`);
    container.appendChild(model.get_child("object"))
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
    object = Child(allow_refs=False)

    _esm = """
export function render({ model }) {
    return (
        <div>
            <h1>Temperature</h1>
            <h2>A measurement from the sensor</h2>
            <div>
                {model.get_child("object")}
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

::::{tab-item} `Viewer`

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
        py_layout.object = dial
    else:
        py_layout.object = html

radio_button_group.servable()
```

::::

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

:::::
