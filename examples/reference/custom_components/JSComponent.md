# `JSComponent`

`JSComponent` simplifies the creation of custom Panel components using JavaScript.

```pyodide
import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class CounterButton(JSComponent):

    value = param.Integer()

    _esm = """
    export function render({ model }) {
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${model.value}`;
      btn.addEventListener("click", () => {
        model.value += 1
      });
      model.watch(() => {
        btn.innerHTML = `count is ${model.value}`;
      }, 'value')
      return btn
    }
    """

CounterButton().servable()
```

:::{note}

`JSComponent` was introduced in June 2024 as a successor to `ReactiveHTML`.

`JSComponent` bears similarities to [`AnyWidget`](https://anywidget.dev/), but it is specifically optimized for use with Panel.

If you are looking to create custom components using Python and Panel component only, check out [`Viewer`](Viewer.md).

:::

## API

### JSComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an  [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--autoreload`, the module will automatically reload upon saving changes.
- **`_importmap`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (optional list of strings): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

:::note

You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file its specified in.

:::

#### `render` Function

The `_esm` attribute must export the `render` function. It accepts the following parameters:

- **`model`**: Represents the Parameters of the component and provides methods to `.watch` for changes, render child elements using `.get_child`, and `.send_event` back to Python.
- **`view`**: The Bokeh view.
- **`el`**: The HTML element that the component will be rendered into.

Any HTML element returned from the `render` function will be appended to the HTML element (`el`) of the component but you may also manually append to and manipulate the `el`.

The `render` function will be rerun when any rendered child is replaced.

#### Other Lifecycle Methods

DUMMY CONTENT. PLEASE HELP ME DESCRIBE THIS.

- `initialize`: Runs once per widget instance at model initialization, facilitating setup for event handlers or state.
- `teardown`: Cleans up resources or processes when a widget instance is being removed.

## Usage

### Styling with CSS

Include CSS within the `_stylesheets` attribute to style the component. The CSS is injected directly into the component's HTML.

```pyodide
import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class StyledCounterButton(JSComponent):

    value = param.Integer()

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

    _esm = """
    export function render({ model }) {
      const btn = document.createElement("button");
      btn.innerHTML = `count is ${model.value}`;
      btn.addEventListener("click", () => {
        model.value += 1
      });
      model.watch(() => {
        btn.innerHTML = `count is ${model.value}`;
      }, 'value')
      return btn
    }
    """

StyledCounterButton().servable()
```

## Send Events from JavaScript to Python

Events from JavaScript can be sent to Python using the `model.send_event` method. Define a *handler* in Python to manage these events. A *handler* is a method on the form `_handle_<name-of-event>(self, event)`:

```pyodide
import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class EventExample(JSComponent):

    value = param.Parameter()

    _esm = """
    export function render({ model }) {
      const btn = document.createElement('button')
      btn.innerHTML = `Click Me`
      btn.onclick = (event) => model.send_event('click', event)
      return btn
    }
    """

    def _handle_click(self, event):
        self.value = str(event.__dict__)

button = EventExample()
pn.Column(
    button, pn.widgets.TextAreaInput(value=button.param.value, height=200),
).servable()
```

You can also define and send your own custom events:

```pyodide
import datetime

import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class CustomEventExample(JSComponent):

    value = param.String()

    _esm = """
    export function render({ model }) {
      const btn = document.createElement('button')
      btn.innerHTML = `Click Me`;
      btn.onclick = (event) => {
        const currentDate = new Date();
        const custom_event = new CustomEvent("click", { detail: currentDate.getTime() });
        model.send_event('click', custom_event)
      }
      return btn
    }
    """

    def _handle_click(self, event):
        unix_timestamp = event.data["detail"]/1000
        python_datetime = datetime.datetime.fromtimestamp(unix_timestamp)
        self.value = str(python_datetime)

button = CustomEventExample()
pn.Column(
    button, button.param.value,
).servable()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from [`esm.sh`](https://esm.sh/).

```pyodide
import panel as pn
from panel.custom import JSComponent

pn.extension()

class ConfettiButton(JSComponent):

    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

    export function render() {
      let btn = document.createElement("button");
      btn.innerHTML = "Click Me";
      btn.addEventListener("click", () => {
        confetti()
      });
      return btn
    }
    """

ConfettiButton().servable()
```

Use the `_import_map` attribute for more concise module references.

```pyodide
import panel as pn

from panel.custom import JSComponent

pn.extension()

class ConfettiButton(JSComponent):
    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "canvas-confetti";

    export function render() {
      let btn = document.createElement("button");
      btn.innerHTML = `Click Me`;
      btn.addEventListener("click", () => {
        confetti()
	  });
      return btn
    }
    """

ConfettiButton().servable()
```

See [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) for more info about the import map format.

## External Files

You can load JavaScript and CSS from files by providing the paths to these files.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param
import panel as pn

from panel.custom import JSComponent

pn.extension()

class CounterButton(JSComponent):

    value = param.Integer()

    _esm = Path("counter_button.js")
    _stylesheets = [Path("counter_button.css")]

CounterButton().servable()
```

Now create the file **counter_button.js**.

```javascript
export function render({ model }) {
  let btn = document.createElement("button");
  btn.innerHTML = `count is ${model.value}`;
  btn.addEventListener("click", () => {
    model.value += 1;
  });
  model.watch(() => {
    btn.innerHTML = `count is ${model.value}`;
  }, 'value');
  return btn;
}
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

- Try changing the `innerHTML` from `count is ${model.value}` to `COUNT IS ${model.value}` and observe the update. Note you must update `innerHTML` in two places.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Child

You can display Panel components (`Viewable`s) by defining a `Child` parameter.

Lets start with the simplest example:

```pyodide
import panel as pn

from panel.custom import Child, JSComponent

class Example(JSComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```pyodide
Example(child="A **Markdown** pane!").servable()
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `class_` argument.

```pyodide
import panel as pn

from panel.custom import Child, JSComponent

class Example(JSComponent):

    child = Child(class_=pn.pane.Markdown)

    _esm = """
    export function render({ children }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types:

```pyodide
import panel as pn

from panel.custom import Child, JSComponent

class Example(JSComponent):

    child = Child(class_=(pn.pane.Markdown, pn.pane.HTML))

    _esm = """
    export function render({ children }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```pyodide
import panel as pn

from panel.custom import Children, JSComponent

pn.extension()

class Example(JSComponent):

    objects = Children()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      div.append(...model.get_child("objects"))
      return div
    }"""


Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(name="Click me!"), {"text": "I'm shown as a JSON Pane"}]
).servable()
```

:::note

You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.

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
