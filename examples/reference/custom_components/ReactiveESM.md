# `ReactiveESM`

`ReactiveESM` simplifies the creation of custom Panel components using JavaScript.

```python
import panel as pn
import param

pn.extension()

class CounterButton(pn.ReactiveESM):

    value = param.Integer()

    _esm = """
    export function render({ data }) {
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${data.value}`;
        btn.addEventListener("click", () => {
            data.value += 1
        });
        data.watch(() => {
            btn.innerHTML = `count is ${data.value}`;
          }, 'value')
        return btn
    }
    """

CounterButton().servable()
```

:::{note}

`ReactiveESM` was introduced in June 2024 as the successor to `ReactiveHTML`.

`ReactiveESM` bears similarities to [`AnyWidget`](https://anywidget.dev/), but it is specifically optimized for use with Panel.

:::

## API

### ReactiveESM Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an  [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--autoreload`, the module will automatically reload upon saving changes.
- **`_import_map`** (dict): This dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (optional list of strings): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

#### `render` Function

The `_esm` attribute most export the `render` function. It accepts the following parameters:

- **`data`**: Represents the non-Viewable Parameters of the component and provides methods to `.watch` for changes and `.send_event` back to Python.
- **`children`**: Represents the Viewable Parameters of the component and provides methods to `.watch` for changes.
- **`model`**: Corresponds to the Bokeh model.
- **`view`**: Corresponds to the Bokeh view.
- **`el`**: The parent HTML element to append child elements to.

When not using React and JSX, the `render` function also supports:

- **`html`**: The Preact `html` function which enables you to write JSX-like syntax in plain JavaScript. See [`htm`](https://github.com/developit/htm).

When using React and JSX, the `render` function also supports:

- **`state`**: Manages state similar to React's [`useState`](https://www.w3schools.com/react/react_usestate.asp) hook.

Any HTML element returned from the `render` function will be appended to the parent HTML element (`el`) of the component.

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

pn.extension()

class StyledCounterButton(pn.ReactiveESM):

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
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${data.value}`;
        btn.addEventListener("click", () => {
            data.value += 1
        });
        data.watch(() => {
            btn.innerHTML = `count is ${data.value}`;
          }, 'value')
        return btn
    }
    """

StyledCounterButton().servable()
```

## Send Events from JavaScript to Python

Events from JavaScript can be sent to Python using the `data.send_event` method. Define a handler in Python to manage these events.

```python
import panel as pn
import param

pn.extension()

class ButtonEventExample(pn.ReactiveESM):

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

button = ButtonEventExample()
pn.Column(
    button, pn.widgets.TextAreaInput(value=button.param.value, height=200),
).servable()
```

You can also define and send your own custom events:

```python
import panel as pn
import param
import datetime

pn.extension()

class ButtonEventExample(pn.ReactiveESM):

    value = param.String()

    _esm = """
    export function render({ data }) {
        const btn = document.createElement('button')
        btn.innerHTML = `Click Me`;
        btn.onclick = (event) => {
            const currentDate = new Date();
            const custom_event = new CustomEvent("click", { detail: currentDate.getTime() });
            data.send_event('click', custom_event)
            }
        return btn
    }
    """

    def on_click(self, event):
        unix_timestamp = event.data["detail"]/1000
        python_datetime = datetime.datetime.fromtimestamp(unix_timestamp)
        self.value = str(python_datetime)

button = ButtonEventExample()
pn.Column(
    button, button.param.value,
).servable()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from [`esm.sh`](https://esm.sh/).

```python
import panel as pn

pn.extension()

class ConfettiButton(pn.ReactiveESM):

    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

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

Use the `_import_map` attribute for more concise module references.

```python
import panel as pn

pn.extension()

class ConfettiButton(pn.ReactiveESM):
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

## External Files

You can load JavaScript and CSS from files by providing the paths to these files.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param
import panel as pn

pn.extension()

class CounterButton(pn.ReactiveESM):

    value = param.Integer()

    _esm = Path("counter_button.js")
    _stylesheets = [Path("counter_button.css")]

CounterButton().servable()
```

Now create the file **counter_button.js**.

```javascript
export function render({ data }) {
    let btn = document.createElement("button");
    btn.innerHTML = `count is ${data.value}`;
    btn.addEventListener("click", () => {
        data.value += 1;
    });
    data.watch(() => {
        btn.innerHTML = `count is ${data.value}`;
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

- Try changing the `innerHTML` from `count is ${data.value}` to `Count is ${data.value}` and observe the update.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Panel Component

You can display Panel components by defining `ClassSelector` parameters with the `class_` set to subtype of `_Viewable` or tuple of subtypes of `_Viewable`s.

Lets start with the simplest example

```python
import param
import panel as pn
from panel import ReactiveESM

class Example(ReactiveESM):

    child = param.ClassSelector(class_=pn.viewable.Viewable)

    _esm = """
    export function render({ children }) {
      const button = document.createElement("button");
      button.appendChild(children.child)
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `_class` argument.

```python
import param
import panel as pn
from panel import ReactiveESM

class Example(ReactiveESM):

    child = param.ClassSelector(class_=pn.pane.Markdown)

    _esm = """
    export function render({ children }) {
      const button = document.createElement("button");
      button.appendChild(children.child)
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types

```python
import param
import panel as pn
from panel import ReactiveESM

class Example(ReactiveESM):

    child = param.ClassSelector(class_=(pn.pane.Markdown, pn.pane.HTML))

    _esm = """
    export function render({ children }) {
      const button = document.createElement("button");
      button.appendChild(children.child)
      return button
    }"""

Example(child=pn.panel("A **Markdown** pane!")).servable()
```

## Displaying a List of Panel Components

You can also use display a `List` of `Viewable` `objects`.

```python
import param
import panel as pn
from panel import ReactiveESM

class Example(ReactiveESM):

    objects = param.List(item_type=pn.viewable.Viewable)

    _esm = """
    export function render({ children }) {
      const div = document.createElement('div')
      div.append(...children.objects)
      return div
    }"""


Example(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(name="Click me!")]
).servable()
```

:::note

You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.

:::

## React with JSX

To use [React](https://react.dev/) with [JSX](https://react.dev/learn/writing-markup-with-jsx) instead of plain JavaScript, follow this approach:

```python
import panel as pn
import param

pn.extension()

class ReactTextInput(pn.ReactiveESM):

    value = param.String()

    _esm = """
    function App(props) {
        const [value, setValue] = props.state.value;
        return (
            <div>
                <input
                id="input"
                value={value}
                onChange={e => setValue(e.target.value)}
                style={{margin: "10px"}}
                />
            </div>
        );
    }

    export function render({state}) {
        return <App state={state}/>;
    }
    """

text_input = ReactTextInput(value="Hello World")

pn.Column(text_input, text_input.param.value).servable()
```

## JSX-like syntax with `html`

If you prefer to not use React but would still like to have an easy way to create a nested DOM element easily you can use the `html` argument of the `render` function.

```python
import panel as pn
import param

pn.extension()

class JSTextInput(pn.ReactiveESM):

    value = param.String()

    _esm = """
    export function render({data, html}) {
        return (html`
            <div>
                <input
                    id="input"
                    value=${data.value}
                    onChange=${e => data.value=e.target.value}
                    style=${{margin: "10px"}}
                />
            </div>
        `)
    }
    """

text_input = JSTextInput(value="Hello World")

pn.Column(text_input, text_input.param.value).servable()
```

When the `data.value` changes the `html` element will be rerendered.
