# Create Custom Layouts

In this guide we will show you how to build custom, reusable layouts using `Viewer`, `JSComponent` or `ReactComponent`.

## Layout a single Panel Component

You can layout a single `object` as follows.

::::{tab-set}

:::{tab-item} `Viewer`

```{pyodide}
import panel as pn
from panel.custom import Child
from panel.viewable import Viewer, Layoutable

pn.extension()


class SingleObjectLayout(Viewer, Layoutable):
    object = Child(allow_refs=False)

    def __init__(self, **params):
        super().__init__(**params)

        header = """
# Temperature
## A Measurement from the Sensor
        """

        layoutable_params = {name: self.param[name] for name in Layoutable.param}
        self._layout = pn.Column(
            pn.pane.Markdown(header, height=100, sizing_mode="stretch_width"),
            self._object,
            **layoutable_params,
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
py_layout = SingleObjectLayout(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
py_layout.servable()
```

:::

:::{tab-item} `JSComponent`

```{pyodide}
import panel as pn
from panel.custom import JSComponent, Child

pn.extension()

class SingleObjectLayout(JSComponent):
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
js_layout = SingleObjectLayout(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
js_layout.servable()
```

:::

:::{tab-item} `ReactComponent`

```{pyodide}
import panel as pn

from panel.custom import Child, ReactComponent

pn.extension()

class SingleObjectLayout(ReactComponent):
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
react_layout = SingleObjectLayout(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
)
react_layout.servable()
```

:::

::::

Lets verify the layout will automatically update when the `object` is changed.

::::{tab-set}

:::{tab-item} `Viewer`

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

:::

:::{tab-item} `JSComponent`

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

:::

:::{tab-item} `ReactComponent`

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

:::

::::

## Layout a List of Objects

A Panel `Column` or `Row` works as a list of objects. It is *list-like*. In this section will show you how to create your own *list-like* layout using Panels `NamedListLike` class.

::::{tab-set}

:::{tab-item} `Viewer`

```{pyodide}
import panel as pn
from panel.viewable import Viewer, Layoutable
from panel.custom import Children
from panel.layout.base import NamedListLike

pn.extension()


class ListLikeLayout(NamedListLike, Layoutable, Viewer):
    objects = Children()

    def __init__(self, *args, **params):
        super().__init__(*args, **params)

        layoutable_params = {name: self.param[name] for name in Layoutable.param}
        self._layout = pn.Column(
            **layoutable_params,
        )
        self._objects()

    def __panel__(self):
        return self._layout

    @pn.depends("objects", watch=True)
    def _objects(self):
        objects = []
        for object in self.objects:
            objects.append(object)
            objects.append(
                pn.pane.HTML(
                    styles={"width": "calc(100% - 15px)", "border-top": "3px dotted #bbb"},
                    height=10,
                )
            )

        self._layout[:] = objects


ListLikeLayout(
    "I love beat boxing",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "Yes I do!",
    styles={"border": "2px solid lightgray"},
).servable()
```

You must list `NamedListLike, Layoutable, Viewer` in exactly that order when you define the class! Other combinations might not work.

:::

:::{tab-item} `JSComponent`

```{pyodide}
import panel as pn
import param
from panel.custom import JSComponent
from panel.layout.base import NamedListLike

pn.extension()


class ListLikeLayout(NamedListLike, JSComponent):
    objects = param.List()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      let objects = model.get_child("objects")

      objects.forEach((object, index) => {
        div.appendChild(object);

        // If it's not the last object, add a divider
        if (index < objects.length - 1) {
            const divider = document.createElement("div");
            divider.className = "divider";
            div.appendChild(divider);
        }
        });
      return div
    }"""

    _stylesheets = [
        """
.divider {border-top: 3px dotted #bbb};
"""
    ]


ListLikeLayout(
    "I love beat boxing",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "Yes I do!",
    styles={"border": "2px solid lightgray"},
).servable()
```

You must list `NamedListLike, JSComponent` in exactly that order when you define the class! The other
way around `JSComponent, NamedListLike` will not work.

:::

:::{tab-item} `ReactComponent`

```{pyodide}
import panel as pn

from panel.custom import Children, ReactComponent

class Example(ReactComponent):

    objects = Children()

    _esm = """
    export function render({ model }) {
        let objects = model.get_child("objects")
        return (
            <div>
                {objects.map((object, index) => (
                    <React.Fragment key={index}>
                        {object}
                        {index < objects.length - 1 && <div className="divider"></div>}
                    </React.Fragment>
                ))}
            </div>
        );
    }"""


Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(name="Click me!"), {"text": "I'm shown as a JSON Pane"}]
).servable()
```

:::

::::

:::{note}
You must list `ListLike, ReactComponent` in exactly that order when you define the class! The other way around `ReactComponent, ListLike` will not work.
:::

You can now use `[...]` indexing and the `.append`, `.insert`, `pop`, ... methods that you would expect.
