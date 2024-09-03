# Create Custom Layouts using ESM Components

In this guide, we will demonstrate how to build custom, reusable layouts using [`JSComponent`](../../reference/panes/JSComponent.md), [`ReactComponent`](../../reference/panes/ReactComponent.md) or [`AnyWidgetComponent`](../../reference/panes/AnyWidgetComponent.md).

## Layout Two Objects

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

    export function render({ model }) {
      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';

      const split0 = document.createElement('div');
      splitDiv.appendChild(split0);

      const split1 = document.createElement('div');
      splitDiv.appendChild(split1);

      const split = Split([split0, split1])

      model.on('remove', () => split.destroy())

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
        value="Right",
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
          {model.get_child("left")}
          {model.get_child("right")}
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
        value="Right",
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

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
import panel as pn

from panel.custom import Child, AnyWidgetComponent

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


class SplitAnyWidget(AnyWidgetComponent):

    left = Child()
    right = Child()

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    function render({ model, el }) {
      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';

      const split0 = document.createElement('div');
      splitDiv.appendChild(split0);

      const split1 = document.createElement('div');
      splitDiv.appendChild(split1);

      const split = Split([split0, split1])

      model.on('remove', () => split.destroy())

      split0.append(model.get_child("left"))
      split1.append(model.get_child("right"))

      el.appendChild(splitDiv)
    }

    export default {render}
    """

    _stylesheets = [CSS]


pn.extension("codeeditor")

split_anywidget = SplitAnyWidget(
    left=pn.widgets.CodeEditor(
        value="Left!",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    right=pn.widgets.CodeEditor(
        value="Right",
        sizing_mode="stretch_both",
        margin=0,
        theme="monokai",
        language="python",
    ),
    height=500,
    sizing_mode="stretch_width",
)
split_anywidget.servable()
```

::::

Let's verify that the layout will automatically update when the `object` is changed.

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

:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
split_anywidget.right=pn.pane.Markdown("Hi. I'm a `Markdown` pane replacing the `CodeEditor` widget!", sizing_mode="stretch_both")
```
:::

::::

Now, let's change it back:

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
split_js.right=pn.widgets.CodeEditor(
    value="Right",
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
    value="Right",
    sizing_mode="stretch_both",
    margin=0,
    theme="monokai",
    language="python",
)
```
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
split_anywidget.right=pn.widgets.CodeEditor(
    value="Right",
    sizing_mode="stretch_both",
    margin=0,
    theme="monokai",
    language="python",
)
```
:::

::::

Now, let's change it back:

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
split_js.right=pn.widgets.CodeEditor(
    value="Right",
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
    value="Right",
    sizing_mode="stretch_both",
    margin=0,
    theme="monokai",
    language="python",
)
```
:::

::::

## Layout a List of Objects

A Panel `Column` or `Row` works as a list of objects. It is *list-like*. In this section, we will show you how to create your own *list-like* layout using Panel's `NamedListLike` class.

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import JSComponent

from panel.layout.base import ListLike

CSS = """
.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}
.gutter.gutter-vertical {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAFAQMAAABo7865AAAABlBMVEVHcEzMzMzyAv2sAAAAAXRSTlMAQObYZgAAABBJREFUeF5jOAMEEAIEEFwAn3kMwcB6I2AAAAAASUVORK5CYII=');
    cursor: row-resize;
}
"""


class GridJS(ListLike, JSComponent):

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    export function render({ model}) {
      const objects = model.get_child("objects")

      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';
      splitDiv.style.height = `calc(100% - ${(objects.length - 1) * 10}px)`;

      let splits = [];

      objects.forEach((object, index) => {
        const split = document.createElement('div');
        splits.push(split)

        splitDiv.appendChild(split);
        split.appendChild(object);
      })

      Split(splits, {direction: 'vertical'})

      return splitDiv
    }"""

    _stylesheets = [CSS]


pn.extension("codeeditor")

grid_js = GridJS(
    pn.widgets.CodeEditor(
        value="I love beatboxing\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    pn.panel(
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
        sizing_mode="stretch_width",
        height=100,
    ),
    pn.widgets.CodeEditor(
        value="Yes, I do!\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    styles={"border": "2px solid lightgray"},
    height=800,
    width=500,
    sizing_mode="fixed",
).servable()
```

You must list `ListLike, JSComponent` in exactly that order when you define the class! Reversing the order to `JSComponent, ListLike` will not work.
:::

:::{tab-item} `ReactComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import ReactComponent
from panel.layout.base import ListLike

CSS = """
.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}
.gutter.gutter-vertical {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAFAQMAAABo7865AAAABlBMVEVHcEzMzMzyAv2sAAAAAXRSTlMAQObYZgAAABBJREFUeF5jOAMEEAIEEFwAn3kMwcB6I2AAAAAASUVORK5CYII=');


 cursor: row-resize;
}
"""


class GridReact(ListLike, ReactComponent):

    _esm = """
    import Split from 'https://esm.sh/react-split@2.0.14'

    export function render({ model}) {
      const objects = model.get_child("objects")
      const calculatedHeight = `calc( 100% - ${(objects.length - 1) * 10}px )`;

      return (
        <Split
            className="split"
            direction="vertical"
            style={{ height: "100%" }}
        >{...objects}</Split>
      )
    }"""

    _stylesheets = [CSS]


pn.extension("codeeditor")

grid_react = GridReact(
    pn.widgets.CodeEditor(
        value="I love beatboxing\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    pn.panel(
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
        sizing_mode="stretch_width",
        height=100,
    ),
    pn.widgets.CodeEditor(
        value="Yes, I do!\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    styles={"border": "2px solid lightgray"},
    height=800,
    width=500,
    sizing_mode="fixed",
)
grid_react.servable()
```

You must list `ListLike, ReactComponent` in exactly that order when you define the class! Reversing the order to `ReactComponent, ListLike` will not work.
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import AnyWidgetComponent

from panel.layout.base import ListLike

CSS = """
.gutter {
    background-color: #eee;
    background-repeat: no-repeat;
    background-position: 50%;
}
.gutter.gutter-vertical {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAFAQMAAABo7865AAAABlBMVEVHcEzMzMzyAv2sAAAAAXRSTlMAQObYZgAAABBJREFUeF5jOAMEEAIEEFwAn3kMwcB6I2AAAAAASUVORK5CYII=');
    cursor: row-resize;
}
"""


class GridAnyWidget(ListLike, AnyWidgetComponent):

    _esm = """
    import Split from 'https://esm.sh/split.js@1.6.5'

    function render({ model, el}) {
      const objects = model.get_child("objects")

      const splitDiv = document.createElement('div');
      splitDiv.className = 'split';
      splitDiv.style.height = `calc(100% - ${(objects.length - 1) * 10}px)`;

      let splits = [];

      objects.forEach((object, index) => {
        const split = document.createElement('div');
        splits.push(split)

        splitDiv.appendChild(split);
        split.appendChild(object);
      })

      Split(splits, {direction: 'vertical'})

      el.appendChild(splitDiv);
    }
    export default {render}
    """

    _stylesheets = [CSS]


pn.extension("codeeditor")

grid_anywidget = GridAnyWidget(
    pn.widgets.CodeEditor(
        value="I love beatboxing\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    pn.panel(
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
        sizing_mode="stretch_width",
        height=100,
    ),
    pn.widgets.CodeEditor(
        value="Yes, I do!\n" * 10, theme="monokai", sizing_mode="stretch_both"
    ),
    styles={"border": "2px solid lightgray"},
    height=800,
    width=500,
    sizing_mode="fixed",
).servable()
```

You must list `ListLike, AnyWidgetComponent` in exactly that order when you define the class! Reversing the order to `AnyWidgetComponent, ListLike` will not work.
:::

::::

You can now use `[...]` indexing and methods like `.append`, `.insert`, `pop`, etc., as you would expect:

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
grid_js.append(
    pn.widgets.CodeEditor(
        value="Another one bites the dust\n" * 10,
        theme="monokai",
        sizing_mode="stretch_both",
    )
)
```
:::

:::{tab-item} `ReactComponent`
```{pyodide}
grid_react.append(
    pn.widgets.CodeEditor(
        value="Another one bites the dust\n" * 10,
        theme="monokai",
        sizing_mode="stretch_both",
    )
)
```
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
grid_anywidget.append(
    pn.widgets.CodeEditor(
        value="Another one bites the dust\n" * 10,
        theme="monokai",
        sizing_mode="stretch_both",
    )
)
```
:::

::::

Let's remove it again:

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
grid_js.pop(-1)
```
:::

:::{tab-item} `ReactComponent`
```{pyodide}
grid_react.pop(-1)
```
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
grid_anywidget.pop(-1)
```
:::

::::
