# `PreactComponent`

`PreactComponent` simplifies the creation of custom Panel components using [Preact](https://preactjs.com/).

```python
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

`ReactComponent` extends the [`JSComponent`](JSComponent.md) class, which allows you to create custom Panel components using JavaScript.

`PreactComponent` bears similarities to [`AnyWidget`](https://anywidget.dev/), but it is specifically optimized for use with Panel and Preact.

:::

## API

### PreactComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an  [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--autoreload`, the module will automatically reload upon saving changes.
- **`_import_map`** (dict): This dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (optional list of strings): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

#### `render` Function

The `_esm` attribute must export the `render` function. It accepts the following parameters:

- **`data`**: Represents the non-Viewable Parameters of the component and provides methods to `.watch` for changes and `.send_event` back to Python.
- **`children`**: Represents the Viewable Parameters of the component and provides methods to `.watch` for changes. The `render` function is rerun if a child changes.
- **`model`**: The Bokeh model.
- **`view`**: The Bokeh view.
- **`el`**: The HTML element that the component will be rendered into.
- **`html`**: The Preact `html` function which enables you to write JSX-like syntax in plain JavaScript. See [`htm`](https://github.com/developit/htm). The `html` function is rerun if any `data` parameter changes.

Any HTML element returned from the `render` function will be appended to the HTML element (`el`) of the component.

#### Other Lifecycle Methods

DUMMY CONTENT. PLEASE HELP ME DESCRIBE THIS.

- `initialize`: Runs once per widget instance at model initialization, facilitating setup for event handlers or state.
- `teardown`: Cleans up resources or processes when a widget instance is being removed.

## Usage

### Styling with CSS

Include CSS within the `_stylesheets` attribute to style the component. The CSS is injected directly into the component's HTML.

```python
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

```python
import panel as pn
import param

from panel.custom import PreactComponent

pn.extension()

class EventExample(PreactComponent):

    value = param.Parameter()

    _esm = """
    export function render({ data }) {
        const btn = document.createElement('button')
        btn.innerHTML = `Click Me`
        btn.onclick = (event) => data.send_event('click', event)
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

```python
import panel as pn
import param

from panel.custom import PreactComponent

pn.extension()

class CustomEventExample(PreactComponent):

    value = param.Parameter()

    _esm = """
    function send_event(data) {
        const currentDate = new Date();
        const custom_event = new CustomEvent("click", { detail: currentDate.getTime() });
        data.send_event('click', custom_event);
    }

    function App(props) {
        return html`
            <button onClick=${() => send_event(props.data)}>
                Click me
            </button>
        `;
    }

    export function render({ data }) {
        return html`<App data=${data} />`
    }
    """

def _handle_click(self, event):
    self.value = str(event.__dict__)

button = CustomEventExample()
pn.Column(
    button, pn.widgets.TextAreaInput(value=button.param.value, height=200),
).servable()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from [`esm.sh`](https://esm.sh/).

```python
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

```python
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

    _esm = Path("counter_button.js")
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

## Displaying A Single Panel Component

You can display Panel components by defining `ClassSelector` parameters with the `class_` set to subtype of `_Viewable` or tuple of subtypes of `_Viewable`s.

Lets start with the simplest example

```python
import panel as pn
import param

from panel.custom PreactComponent


class Example(PreactComponent):

    child = param.ClassSelector(class_=pn.viewable.Viewable)

    _esm = """
    export function render({ children }) {
      return html`
        <button ref=${ref => ref && ref.appendChild(children.child)}>
        </button>
    `}
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `_class` argument.

```python
import panel as pn
import param

from panel.custom PreactComponent


class Example(PreactComponent):

    child = param.ClassSelector(class_=pn.viewable.Markdown)

    _esm = """
    export function render({ html, children }) {
      return html`
        <button ref=${ref => ref && ref.appendChild(children.child)}>
        </button>
    `}
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types

DOES NOT WORK YET! PLEASE FIX.

```python
import param
import panel as pn

from panel.custom PreactComponent


class Example(PreactComponent):

    child = param.ClassSelector(class_=(pn.pane.Markdown, pn.pane.HTML))

    _esm = """
    export function render({ html, children }) {
      return html`
        <button ref=${ref => ref && ref.appendChild(children.child)}>
        </button>
    `}
    """

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

## Displaying a List of Panel Components

You can also display a `List` of `Viewable` `objects`.

```python
import param
import panel as pn

from panel.custom PreactComponent


class Example(PreactComponent):

    objects = param.List(item_type=pn.viewable.Viewable)

    _esm = """
    export function render({ html, children }) {
      return html`
        <div ref=${ref => ref && children.objects.map( (child, index) => ref.appendChild(child))}>
        </div>
    `
    }"""


Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(name="Click me!")]
).servable()
```

:::note

You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.

:::
