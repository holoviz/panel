# Create Custom Layouts

In this guide we will show you how to build custom, reusable layouts using [`JSComponent`](../../reference/panes/JSComponent.md) or [`ReactComponent`](../../reference/panes/ReactComponent.md).

Please note that you currently cannot create layouts using the [`AnyWidgetComponent`](../../reference/panes/AnyWidgetComponent.md) because the underlying [`AnyWidget`](https://anywidget.dev/) API does not support this.

## Layout two objects

This example will show you how to create a *split* layout containing two objects. We will be using the [Split.js](https://split.js.org/) library.

::::{tab-set}

:::{tab-item} `JSComponent`

```{pyodide}
import panel as pn

from panel.custom import Child, JSComponent

CSS = """
.split {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
}

.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}

.gutter.gutter-horizontal {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAeCAYAAADkftS9AAAAIklEQVQoU2M4c+bMfxAGAgYYmwGrIIiDjrELjpo5aiZeMwF+yNnOs5KSvgAAAABJRU5ErkJggg==');
    cursor: col-resize;
}
"""


class SplitJS(JSComponent):

    left = Child()
    right = Child()

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    const splitDiv = document.createElement('div');
    splitDiv.className = 'split';

    const split0 = document.createElement('div');
    splitDiv.appendChild(split0);

    let split1 = document.createElement('div');
    splitDiv.appendChild(split1);

    Split([split0, split1])

    export function render({ model }) {
        split0.append(model.get_child("left"))
        split1.append(model.get_child("right"))
      return splitDiv
    }"""

    _stylesheets = [CSS]


pn.extension("codeeditor")

split_js = SplitJS(
    left=pn.widgets.CodeEditor(
        value="Left!",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    right=pn.widgets.CodeEditor(
        value="right",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    height=500,
    sizing_mode="stretch_width",
)
split_js.servable()
```

:::

:::{tab-item} `ReactComponent`

```{pyodide}
import panel as pn

from panel.custom import Child, ReactComponent

CSS = """
.split {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
}

.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}

.gutter.gutter-horizontal {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAeCAYAAADkftS9AAAAIklEQVQoU2M4c+bMfxAGAgYYmwGrIIiDjrELjpo5aiZeMwF+yNnOs5KSvgAAAABJRU5ErkJggg==');
    cursor: col-resize;
}
"""


class SplitReact(ReactComponent):

    left = Child()
    right = Child()

    _esm = """
    import Split from 'https://esm.sh/react-split@2.0.14'

    export function render({ model }) {
        return (
            <Split className="split">
                <div>{model.get_child("left")}</div>
                <div>{model.get_child("right")}</div>
            </Split>
        )
    }
    """

    _stylesheets = [CSS]


pn.extension("codeeditor")

split_react = SplitReact(
    left=pn.widgets.CodeEditor(
        value="Left!",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    right=pn.widgets.CodeEditor(
        value="right",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    height=500,
    sizing_mode="stretch_width",
)
split_react.servable()
```

:::

::::

Lets verify the layout will automatically update when the `object` is changed.

::::{tab-set}

:::{tab-item} `JSComponent`

```{pyodide}
split_js.right=pn.pane.Markdown("Hi. I'm a `Markdown` pane replacing the `CodeEditor` widget!", sizing_mode="stretch_both")
```

:::

:::{tab-item} `ReactComponent`

```{pyodide}
split_react.right=pn.pane.Markdown("Hi. I'm a `Markdown` pane replacing the `CodeEditor` widget!", sizing_mode="stretch_both")
```

:::

Lets change it back:

::::

::::{tab-set}

:::{tab-item} `JSComponent`

```{pyodide}
split_js.right=pn.widgets.CodeEditor(
    value="right",
    sizing_mode="stretch_both",
    margin=0,
    theme="monokai",
    language="python",
)
```

:::

:::{tab-item} `ReactComponent`

```{pyodide}
split_react.right=pn.widgets.CodeEditor(
    value="right",
    sizing_mode="stretch_both",
    margin=0,
    theme="monokai",
    language="python",
)
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
