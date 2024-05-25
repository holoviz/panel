# `PreactComponent`

`PreactComponent` simplifies the creation of custom Panel components using [Preact](https://preactjs.com/).

```pyodide
import panel as pn
import param

from panel.custom import PreactComponent

pn.extension()

class CounterButton(PreactComponent):

    value = param.Integer()

    _esm = """
    export function render({ data }) {
        return html`
            <button onClick=${() => data.value += 1}>
                count is ${data.value}
            </button>
        `;
    }
    """

CounterButton().servable()
```

:::{note}

`PreactComponent` extends the [`JSComponent`](JSComponent.md) class, which allows you to create custom Panel components using JavaScript.

`PreactComponent` bears similarities to [`AnyWidget`](https://anywidget.dev/), but it is specifically optimized for use with Panel and [Preact](https://preactjs.com/).

:::

## API

### PreactComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an  [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--autoreload`, the module will automatically reload upon saving changes.
- **`_import_map`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (List[str | PurePath] | None): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

:::note

You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file its specified in.

:::

#### `render` Function

The `_esm` attribute must export the `render` function. It accepts the following parameters:

- **`data`**: Represents the non-Viewable Parameters of the component and provides methods to `.watch` for changes and `.send_event` back to Python.
- **`children`**: Represents the Viewable Parameters of the component.
- **`model`**: The Bokeh model.
- **`view`**: The Bokeh view.
- **`el`**: The HTML element that the component will be rendered into.
- **`html`**: The Preact `html` function which enables you to write JSX-like syntax in plain JavaScript. See [`htm`](https://github.com/developit/htm).

Any HTML element returned from the `render` function will be appended to the HTML element (`el`) of the component.

The `render` function is rerun if a `data` or `children` value changes.

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

from panel.custom import PreactComponent

pn.extension()

class CounterButton(PreactComponent):

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
    export function render({ data }) {
        return html`
            <button onClick=${() => data.value += 1}>
                count is ${data.value}
            </button>
        `;
    }
    """


CounterButton().servable()
```

## Send Events from JavaScript to Python

Events from JavaScript can be sent to Python using the `data.send_event` method. Define a handler in Python to manage these events.

```pyodide
import panel as pn
import param

from panel.custom import PreactComponent

pn.extension()

class EventExample(PreactComponent):

    value = param.Parameter()

    _esm = """
    export function render({ data }) {
        return html`
            <button onClick=${(e) => data.send_event('click', e)}>
                Click me
            </button>
        `;
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

from panel.custom import PreactComponent

pn.extension()

class EventExample(PreactComponent):

    value = param.String()

    _esm = """
    function send_event(data) {
        const currentDate = new Date();
        const custom_event = new CustomEvent("click", { detail: currentDate.getTime() });
        data.send_event('click', custom_event);
    }

    export function render({ data }) {
        return html`
            <button onClick=${() => send_event(data)}>
                click me
            </button>
        `;
    }
    """

    def _handle_click(self, event):
        unix_timestamp = event.data["detail"]/1000
        python_datetime = datetime.datetime.fromtimestamp(unix_timestamp)
        self.value = str(python_datetime)

button = EventExample()
pn.Column(
    button, button.param.value,
).servable()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from [`esm.sh`](https://esm.sh/).

```pyodide
import panel as pn

from panel.custom import PreactComponent

pn.extension()

class ConfettiButton(PreactComponent):
    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

    export function render() {
        return html`
            <button onClick=${e => confetti()}>
                Click Me
            </button>
        `;
    }
    """

ConfettiButton().servable()
```

Use the `_importmap` attribute for more concise module references.

```pyodide
import panel as pn

from panel.custom import PreactComponent

pn.extension()

class ConfettiButton(PreactComponent):
    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "canvas-confetti";

    export function render() {
        return html`
            <button onClick=${e => confetti()}>
                Click Me
            </button>
        `;
    }
    """

ConfettiButton().servable()
```

See [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) for more info.

## External Files

You can load JavaScript and CSS from files by providing the paths to these files.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param
import panel as pn

pn.extension()

class CounterButton(pn.PreactComponent):

    value = param.Integer()

    _esm = "counter_button.js"
    _stylesheets = [Path("counter_button.css")]

CounterButton().servable()
```

Now create the file **counter_button.js**.

```javascript
export function render({ data }) {
  return html`
    <button onClick=${() => data.value += 1}>
      count is ${data.value}
    </button>
  `;
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

- Try changing the `innerHTML` from `count is ${data.value}` to `COUNT IS ${data.value}` and observe the update.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Child

You can display Panel components by defining a `Child` parameter.

Lets start with the simplest example:

```pyodide
import panel as pn

from panel.custom import Child, PreactComponent

class Example(PreactComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return html`<button>${children.child}</button>`
    }
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```pyodide
Example(child="A **Markdown** pane!").servable()
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `class_` argument.

```pyodide
import panel as pn

from panel.custom import Child, PreactComponent

class Example(PreactComponent):

    child = Child(class_=pn.pane.Markdown)

    _esm = """
    export function render({ html, children }) {
      return html`<button>${children.child}</button>`
    }
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types:

```pyodide
import panel as pn

from panel.custom import Child, PreactComponent


class Example(PreactComponent):

    child = Child(class_=(pn.pane.Markdown, pn.pane.HTML))

    _esm = """
    export function render({ children }) {
      return html`<button>${children.child}</button>`
    }
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```pyodide
import panel as pn

from panel.custom import Children, PreactComponent


class Example(PreactComponent):

    objects = Children()

    _esm = """
    export function render({ children }) {
      return html`<button>${children.objects}</button>`
    }
    """


Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(name="Click me!"), {"text": "I'm shown as a JSON Pane"}]
).servable()
```

:::note

You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.

:::
