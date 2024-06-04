# `AnyWidgetComponent`

Panel's `AnyWidgetComponent` class simplifies the creation of custom Panel components using the [`AnyWidget`](https://anywidget.dev/) JavaScript API.

```pyodide
import panel as pn
import param

from panel.custom import AnyWidgetComponent

pn.extension()

class CounterButton(AnyWidgetComponent):

    value = param.Integer()

    _esm = """
    function render({ model, el }) {
      let count = () => model.get("value");
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${count()}`;
      btn.addEventListener("click", () => {
        model.set("value", count() + 1);
        model.save_changes();
      });
      model.on("change:value", () => {
        btn.innerHTML = `count is ${count()}`;
      });
      el.appendChild(btn);
    }
    export default { render };
    """

CounterButton().servable()
```

:::{note}
Panel's `AnyWidgetComponent` supports using the [`AnyWidget`](https://anywidget.dev/) API on the JavaScript side and the [`param`](https://param.holoviz.org/) parameters API on the Python side.

Compared to Panel's [`JSComponent`](JSComponent.md) and [`ReactComponent`](ReactComponent.md) classes, the `AnyWidgetComponent` does not support creating panes that display a single Panel child object or layouts that display multiple Panel child objects.
:::

## API

### AnyWidgetComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `default` object or function that returns an object. The object should contain a `render` function and optionally an `initialize` function. In a development environment such as a notebook or when using `--autoreload`, the module will automatically reload upon saving changes.
- **`_importmap`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (optional list of strings): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

:::note

You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file it is referenced in.

:::

#### `render` Function

The `_esm` `default` object must contain a `render` function. It accepts the following parameters:

- **`model`**: Represents the parameters of the component and provides methods to `.get` values, `.set` values, and `.save_changes`.
- **`el`**: The parent HTML element to append HTML elements to.

For more detail, see [`AnyWidget`](https://anywidget.dev/).

## Usage

### Styling with CSS

Include CSS within the `_stylesheets` attribute to style the component. The CSS is injected directly into the component's HTML.

```pyodide
import panel as pn
import param

from panel.custom import AnyWidgetComponent

pn.extension()

class StyledCounterButton(AnyWidgetComponent):

    value = param.Integer()

    _esm = """
    function render({ model, el }) {
      let count = () => model.get("value");
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${count()}`;
      btn.addEventListener("click", () => {
        model.set("value", count() + 1);
        model.save_changes();
      });
      model.on("change:value", () => {
        btn.innerHTML = `count is ${count()}`;
      });
      el.appendChild(btn);
    }
    export default { render };
    """

    _stylesheets = [
        """
        button {
            background: #0072B5;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
        }
        button:hover {
            background: #4099da;
        }
        """
    ]

StyledCounterButton().servable()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from [`esm.sh`](https://esm.sh/).

```pyodide
import panel as pn
from panel.custom import AnyWidgetComponent

pn.extension()

class ConfettiButton(AnyWidgetComponent):

    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

    function render({ el }) {
      let btn = document.createElement("button");
      btn.innerHTML = "Click Me";
      btn.addEventListener("click", () => {
        confetti();
      });
      el.appendChild(btn);
    }
    export default { render }
    """

ConfettiButton().servable()
```

Use the `_import_map` attribute for more concise module references.

```pydodide
import panel as pn
from panel.custom import AnyWidgetComponent

pn.extension()

class ConfettiButton(AnyWidgetComponent):

    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "canvas-confetti";

    function render({ el }) {
      let btn = document.createElement("button");
      btn.innerHTML = "Click Me";
      btn.addEventListener("click", () => {
        confetti();
      });
      el.appendChild(btn);
    }
    export default { render }
    """

ConfettiButton().servable()
```

See the [import map documentation](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) for more information about the import map format.

## External Files

You can load JavaScript and CSS from files by providing the paths to these files.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param
import panel as pn

from panel.custom import AnyWidgetComponent

pn.extension()

class CounterButton(AnyWidgetComponent):

    value = param.Integer()

    _esm = Path("counter_button.js")
    _stylesheets = [Path("counter_button.css")]

CounterButton().servable()
```

Now create the file **counter_button.js**.

```javascript
function render({ model, el }) {
    let value = () => model.get("value");
    let btn = document.createElement("button");
    btn.innerHTML = `count is ${value()}`;
    btn.addEventListener("click", () => {
      model.set('value', value() + 1);
      model.save_changes();
    });
    model.on("change:value", () => {
        btn.innerHTML = `count is ${value()}`;
    });
    el.appendChild(btn);
}
export default { render }
```

Now create the file **counter_button.css**.

```css
button {
    background: #0072B5;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 4px;
}
button:hover {
    background: #4099da;
}
```

Serve the app with `panel serve counter_button.py --autoreload`.

You can now edit the JavaScript or CSS file, and the changes will be automatically reloaded.

- Try changing the `innerHTML` from `count is ${value()}` to `COUNT IS ${value()}` and observe the update. Note you must update `innerHTML` in two places.
- Try changing the background color from `#0072B5` to `#008080`.

## React

You can use React with `AnyWidget` as shown below.

```pydodide
import panel as pn
import param

from panel.custom import AnyWidgetComponent

pn.extension()

class CounterButton(AnyWidgetComponent):

    value = param.Integer()

    _importmap = {
        "imports": {
            "@anywidget/react": "https://esm.sh/@anywidget/react",
            "react": "https://esm.sh/react@18.2.0",
        }
    }

    _esm = """
    import * as React from "react"; /* mandatory import */
    import { createRender, useModelState } from "@anywidget/react";

    const render = createRender(() => {
      const [value, setValue] = useModelState("value");
      return (
        <button onClick={() => setValue(value + 1)}>
          count is {value}
        </button>
      );
    });
    export default { render }
    """

CounterButton().servable()
```

:::{note}
You will notice that Panel's `AnyWidgetComponent` can be used with React and [JSX](https://react.dev/learn/writing-markup-with-jsx) without any build tools. Instead of build tools, Panel uses [Sucrase](https://sucrase.io/) to transpile the JSX code to JavaScript on the client side.
:::

## References

### Tutorials

- [Build Custom Components](../../../how_to/custom_components/reactive_esm/reactive_esm_layout.md)

### How-To Guides

- [Convert `AnyWidget` widgets](../../../how_to/migrate/anywidget/index.md)

### Reference Guides

- [`AnyWidgetComponent`](../../../reference/panes/AnyWidgetComponent.md)
- [`JSComponent`](../../../reference/panes/JSComponent.md)
- [`ReactComponent`](../../../reference/panes/ReactComponent.md)
