# ReactComponent
---
```python
import panel as pn

pn.extension()
```

`ReactComponent` simplifies the creation of custom Panel components by allowing you to write standard [React](https://react.dev/) code without the need to pre-compile or requiring a deep understanding of Javascript build tooling.

```python
import panel as pn
import param

from panel.custom import ReactComponent

class CounterButton(ReactComponent):

    value = param.Integer()

    _esm = """
    export function render({model}) {
      const [value, setValue] = model.useState("value");
      return (
        <button onClick={e => setValue(value+1)}>
          count is {value}
        </button>
      )
    }
    """

CounterButton()
```

## API

### ReactComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--dev`, the module will automatically reload upon saving changes. You can use `JSX` and `TypeScript`. The `_esm` script is transpiled on the fly using [Sucrase](https://sucrase.io/). The global namespace contains a `React` object that provides access to React hooks.
- **`_importmap`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_stylesheets`** (List[str | PurePath] | None): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

:::note
You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file its specified in.
:::

#### `render` Function

The `_esm` attribute must export the `render` function. It accepts the following parameters:

- **`model`**: Represents the Parameters of the component and provides methods to add (and remove) event listeners using `.on` and `.off`, render child React components using `.get_child`, get a state hook for a parameter value using `.useState` and to `.send_event` back to Python.
- **`view`**: The Bokeh view.
- **`el`**: The HTML element that the component will be rendered into.

Any React component returned from the `render` function will be appended to the HTML element (`el`) of the component.

### State Hooks

The recommended approach to build components that depend on parameters in Python is to create [`useState` hooks](https://react.dev/reference/react/useState) by calling `model.useState('<parameter>')`. The `model.useState` method returns an array with exactly two values:

1. The current state. During the first render, it will match the initialState you have passed.
2. The set function that lets you update the state to a different value and trigger a re-render.

Using the state value in your React component will automatically re-render the component when it is updated.

### Callbacks

The `model.on` and `model.off` methods allow registering event handlers inside the render function. This includes the ability to listen to parameter changes and register lifecycle hooks.

#### Change Events

The following signatures are valid when listening to change events:

- `.on('<parameter>', callback)`: Allows registering an event handler for a single parameter.
- `.on(['<parameter>', ...], callback)`: Allows adding an event handler for multiple parameters at once.
- `.on('change:<parameter>', callback)`: The `change:` prefix allows disambiguating change events from lifecycle hooks should a parameter name and lifecycle hook overlap.

The `change:` prefix allows disambiguating change events from lifecycle hooks should a parameter name and lifecycle hook overlap.

#### Bidirectional Events

##### JS -> Python

- `.send_event('<name>', DOMEvent)`: Allows sending browser `DOMEvent` to Python and associating it with a name. An event handler can be registered by name with the `.on_event` method or by implementing a `_handle_<name>` method on the class.
- `.send_msg(data)`: Allows sending arbitrary data to Python. An event handler can be registered with the `.on_msg(callback)` method on the Python component or by implementing a `_handle_msg` method on the class.

##### Python -> JS

- `._send_event(ESMEvent, data=msg)`: Allows sending arbitrary data to the frontend, which can be observed by registering a handler with `.on('msg:custom', callback)`.

#### Lifecycle Hooks

- `.on('after_layout', callback)`: Called whenever the layout around the component is changed.
- `.on('after_render', callback)`: Called once after the component has been fully rendered.
- `.on('resize', callback)`: Called after the component has been resized.
- `.on('remove', callback)`: Called when the component view is being removed from the DOM.

The `lifecycle:` prefix allows disambiguating lifecycle hooks from change events should a parameter name and lifecycle hook overlap.

## Usage

### Styling with CSS

Include CSS within the `_stylesheets` attribute to style the component. The CSS is injected directly into the component's HTML.

```python
import panel as pn
import param

from panel.custom import ReactComponent

class CounterButton(ReactComponent):

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
      const [value, setValue] = model.useState("value");
      return (
        <button onClick={e => setValue(value+1)}>
          count is {value}
        </button>
    );
    }
    """

CounterButton()
```

## Send Events from JavaScript to Python

Events from JavaScript can be sent to Python using the `model.send_event` method. Define a handler in Python to manage these events. A *handler* is a method on the form `_handle_<name-of-event>(self, event)`:

```python
import panel as pn
import param

from panel.custom import ReactComponent

pn.extension()

class EventExample(ReactComponent):

    value = param.Parameter()

    _esm = """
    export function render({ model }) {
    return (
        <button onClick={e => model.send_event('click', e) }>
          Click me
        </button>
      );
    }
    """

    def _handle_click(self, event):
        self.value = event.data

button = EventExample()
event_json = pn.pane.JSON(button.param.value)

pn.Column(button, event_json)
```

You can also define and send arbitrary data using the `.send_msg()` API and by implementing a `_handle_msg` method on the component:

```python
import datetime

import panel as pn
import param

from panel.custom import ReactComponent

class CustomEventExample(ReactComponent):

    value = param.String()

    _esm = """
    function send_event(model) {
      const currentDate = new Date();
      model.send_msg(currentDate.getTime())
    }

    export function render({ model }) {
    return (
        <button onClick={e => send_event(model) }>
          Click me
        </button>
    );
    }
    """

    def _handle_msg(self, msg):
        unix_timestamp = msg/1000
        python_datetime = datetime.datetime.fromtimestamp(unix_timestamp)
        self.value = str(python_datetime)

button = CustomEventExample()

pn.Column(button, button.param.value)
```

## Send Events from Python to JavaScript

Equivalently, events from Python can be sent to JavaScript using the `ReactComponent._send_msg` method. To define a handler to receive these messages register a callback with `model.on('msg:custom', callback)`:

In this simple example, we send a message containing the current date and time and display it in the component (note the serializer turns our datetime object into a timestamp):

```python
import datetime

from panel.custom import ReactComponent

class PythonToJSExample(ReactComponent):

    _esm = """
    export function render({ model }) {
      const [value, setValue] = React.useState(null)

      model.on('msg:custom', (msg) => {
        setValue(new Date(msg).toLocaleString())
      })

      return {value}
    }
    """

    def send_event(self):
        self._send_msg(datetime.datetime.now())

py2js = PythonToJSExample()

py2js
```

Sending messages as events rather than state changes provides more control over state synchronization between Python and JavaScript.

```python
py2js.send_event()
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from `esm.sh`.

```python
import panel as pn

from panel.custom import ReactComponent

class ConfettiButton(ReactComponent):

    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

    export function render() {
      return (
        <button onClick={e => confetti()}>
          Click Me
        </button>
      );
    }
    """

ConfettiButton()
```

Use the `_importmap` attribute for more concise module references.

```python
import panel as pn

from panel.custom import ReactComponent

class ConfettiButton(ReactComponent):
    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "canvas-confetti";

    export function render() {
      return (
        <button onClick={(e) => confetti()}>
          Click Me
        </button>
      );
    }
    """

ConfettiButton()
```

See [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) for more info about the import map format.

## External Files

You can load JSX and CSS from files by providing the paths to these files.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param
import panel as pn

from panel.custom import ReactComponent

pn.extension()

class CounterButton(ReactComponent):

    value = param.Integer()

    _esm = "counter_button.jsx"
    _stylesheets = [Path("counter_button.css")]

CounterButton().servable()
```

Now create the file **counter_button.jsx**.

```javascript
export function render({ model }) {
  const [value, setValue] = model.useState("value");
  return (
    <button onClick={e => setValue(value+1)}>
      count is {value}
    </button>
  );
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

Serve the app with `panel serve counter_button.py --dev`.

You can now edit the JSX or CSS file, and the changes will be automatically reloaded.

- Try changing `count is {value}` to `COUNT IS {value}` and observe the update.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Child

You can display Panel components (`Viewable`s) by defining a `Child` parameter.

Lets start with the simplest example

```python
import panel as pn

from panel.custom import Child, ReactComponent

class Example(ReactComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      return <button>{model.get_child("child")}</button>
    }
    """

Example(child=pn.panel("A **Markdown** pane!"))
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```python
Example(child="A **Markdown** pane!")
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `class_` argument.

```python
import panel as pn

from panel.custom import Child, ReactComponent

class Example(ReactComponent):

    child = Child(class_=pn.pane.Markdown)

    _esm = """
    export function render({ model }) {
      return <button>{model.get_child("child")}</button>
    }
    """

Example(child=pn.panel("A **Markdown** pane!"))
```

The `class_` argument also supports a tuple of types:

```python
    child = Child(class_=(pn.pane.Markdown, pn.pane.HTML))
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```python
import panel as pn

from panel.custom import Children, ReactComponent

class Example(ReactComponent):

    objects = Children()

    _esm = """
    export function render({ model }) {
      return {model.get_child("objects")}
    }"""

Example(
    objects=[
        pn.panel("A **Markdown** pane!"),
        pn.widgets.Button(label="Click me!"),
        {"text": "I'm shown as a JSON Pane"}
    ]
)
```

:::note
You can change the `item_type` to a specific subtype of `Viewable` or a tuple of `Viewable` subtypes.
:::

## Rendering into a specific DOM element

You can render the component into a specific DOM element by providing a `root_node` to the underlying `ReactComponent` model. This allows you to render things outside of the regular DOM hierarchy.

The `root_node` should be a valid CSS selector for the DOM element you want to render into, if it doesn't exist it will be created and appended to the document body.

In this example we render the component into a div with the id `custom-root` which we then place in the upper right corner of the document.

```python
import panel as pn

from panel.custom import ReactComponent

class RootNodeExample(ReactComponent):

    _esm = """
    export function render({ model }) {
      return Hello
    }
    """

    def _get_properties(self, doc):
        props = super()._get_properties(doc)
        props["root_node"] = "#custom-root"
        return props
    
RootNodeExample()
```

## Using React Hooks

The global namespace also contains a `React` object that provides access to React hooks. Here is an example of a simple counter button using the `useState` hook:

```python
import panel as pn

from panel.custom import ReactComponent

class CounterButton(ReactComponent):

    _esm = """
    let { useState } = React;

    export function render() {
      const [value, setValue] = useState(0);
      return (
        <button onClick={e => setValue(value+1)}>
          count is {value}
        </button>
      );
    }
    """

CounterButton()
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
