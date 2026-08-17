# AnyWidgetComponent
---
```python
import panel as pn

pn.extension()
```

Panel's `AnyWidgetComponent` class simplifies the creation of custom Panel components using the [AnyWidget Front End Module (AFM) specification](https://anywidget.dev/en/afm/) maintained by `AnyWidget`.

This allows the Panel, Jupyter and other communities to collaborate and share JavaScript code for widgets.

```python
import param
import panel as pn
from panel.custom import AnyWidgetComponent

pn.extension()

class CounterWidget(AnyWidgetComponent):
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
    value = param.Integer()

CounterWidget().servable()
```

## API

### AnyWidgetComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `default` object or function that returns an object. The object should contain a `render` function and optionally an `initialize` function. In a development environment such as a notebook or when using `--dev` flag, the module will automatically reload upon saving changes.
- **`_importmap`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (list[str] | list[PurePath]): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments. It works similarly to the `AnyWidget` `_css` attribute.

:::note
You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file it is referenced in.
:::

#### `render` Function

The `_esm` `default` object must contain a `render` function. It accepts the following parameters:

- **`model`**: Represents the parameters of the component and provides methods to `.get` values, `.set` values, and `.save_changes`. In addition to the AnyWidgets methods, Panel uniquely provides the `get_child` method to enable rendering of child models.
- **`el`**: The parent HTML element to which HTML elements are appended.

For more details, see `AnyWidget`.

## Usage

### Styling with CSS

Include CSS within the `_stylesheets` attribute to style the component. The CSS is injected directly into the component's HTML.

```python
import param
import panel as pn

from panel.custom import AnyWidgetComponent

pn.extension()

class CounterWidget(AnyWidgetComponent):
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
        button { color: white; font-size: 1.75rem; background-color: #ea580c; padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; }
        button:hover { background-color: #9a3412; }
        """
    ]
    value = param.Integer()

CounterWidget().servable()
```

### Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from `esm.sh`.

```python
import panel as pn

from panel.custom import AnyWidgetComponent

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

Use the `_importmap` attribute for more concise module references.

```python
import panel as pn

from panel.custom import AnyWidgetComponent

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

### External Files

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

- Try changing the `innerHTML` from `count is ${value()}` to `COUNT IS ${value()}` and observe the update. Note that you must update `innerHTML` in two places.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Child

You can display Python objects by defining a `Child` parameter. Please note that this feature is **currently not supported by `AnyWidget`**.

Lets start with the simplest example:

```python
import panel as pn

from panel.custom import AnyWidgetComponent, Child

pn.extension()

class Example(AnyWidgetComponent):

    child = Child()

    _esm = """
    function render({ model, el }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      el.appendChild(button);
    }

    export default { render };
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```python
Example(child="A **Markdown** pane!").servable()
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `class_` argument.

```python
import panel as pn

from panel.custom import AnyWidgetComponent, Child

class Example(AnyWidgetComponent):

    child = Child(class_=pn.pane.Markdown)

    _esm = """
    function render({ model, el }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      el.appendChild(button);
    }

    export default { render };
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types:

```python
    child = Child(class_=(pn.pane.Markdown, pn.pane.HTML))
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```python
import panel as pn

from panel.custom import AnyWidgetComponent, Children

pn.extension()

class Example(AnyWidgetComponent):

    objects = Children()

    _esm = """
    function render({ model, el }) {
      const div = document.createElement('div')
      div.append(...model.get_child("objects"))
      el.appendChild(div);
    }

    export default { render };
    """

Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(label="Click me!"), {"text": "I'm shown as a JSON Pane"}]
).servable()
```

:::note
You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.
:::

### React

You can use React with `AnyWidget` as shown below.

```python
import panel as pn
import param

from panel.custom import AnyWidgetComponent

class CounterButton(AnyWidgetComponent):

    value = param.Integer()

    _importmap = {
        "imports": {
            "@anywidget/react": "https://esm.sh/@anywidget/react?deps=react@18.2.0,react-dom@18.2.0",
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

## References

### Tutorials

- [Build Custom Components](../../how_to/custom_components/esm/custom_layout.md)

### How-To Guides

- [Convert `AnyWidget` widgets](../../how_to/migrate/anywidget/index.md)

### Reference Guides

- `AnyWidgetComponent`
- `JSComponent`
- `ReactComponent`

---
