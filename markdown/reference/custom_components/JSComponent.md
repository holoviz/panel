# JSComponent
---
```python
import panel as pn

pn.extension()
```

`JSComponent` simplifies the creation of custom Panel components using JavaScript.

```python
import panel as pn
import param

from panel.custom import JSComponent

class CounterButton(JSComponent):

    value = param.Integer()

    _esm = """
    export function render({ model }) {
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${model.value}`;
      btn.addEventListener("click", () => {
        model.value += 1
      });
      model.on('value', () => {
        btn.innerHTML = `count is ${model.value}`;
      })
      return btn
    }
    """

CounterButton().servable()
```

## API

### JSComponent Attributes

- **`_esm`** (str | PurePath): This attribute accepts either a string or a path that points to an  [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). The ECMAScript module should export a `render` function which returns the HTML element to display. In a development environment such as a notebook or when using `--dev` flag, the module will automatically reload upon saving changes.
- **`_importmap`** (dict | None): This optional dictionary defines an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), allowing you to customize how module specifiers are resolved.
- **`_render_policy`** (Literal['manual', 'children']): Policy that determines when to to re-render (i.e. call the render function) the component. By default `render_policy='children'`, which triggers a full re-render when a child is updated. In `'manual'` mode updates to children have to be manually handled using `.on` callbacks.
- **`_stylesheets`** (optional list of strings): This optional attribute accepts a list of CSS strings or paths to CSS files. It supports automatic reloading in development environments.

:::note

You may specify a path to a file as a string instead of a PurePath. The path should be specified relative to the file its specified in.

:::

### `render` Function

The `_esm` attribute must export the `render` function. It accepts the following parameters:

- **`model`**: Represents the Parameters of the component and provides methods to add (and remove) event listeners using `.on` and `.off`, render child elements using `.get_child`, and to `.send_event` back to Python.
- **`view`**: The Bokeh view.
- **`el`**: The HTML element that the component will be rendered into.

Any HTML element returned from the `render` function will be appended to the HTML element (`el`) of the component but you may also manually append to and manipulate the `el` directly.

### Callbacks

The `model.on` and `model.off` methods allow registering event handlers inside the render function. This includes the ability to listen to parameter changes and register lifecycle hooks.

#### Change Events

The following signatures are valid when listening to change events:

- `.on('<parameter>', callback)`: Allows registering an event handler for a single parameter.
- `.on(['<parameter>', ...], callback)`: Allows adding an event handler for multiple parameters at once.
- `.on('change:<parameter>', callback)`: The `change:` prefix allows disambiguating change events from lifecycle hooks should a parameter name and lifecycle hook overlap.
-

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

from panel.custom import JSComponent

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
      model.on('value', () => {
        btn.innerHTML = `count is ${model.value}`;
      })
      return btn
    }
    """

StyledCounterButton().servable()
```

## Send Events from JavaScript to Python

Events from JavaScript can be sent to Python using the `model.send_event` method. Define a *handler* in Python to manage these events. A *handler* is a method on the form `_handle_<name-of-event>(self, event)`:

```python
import panel as pn
import param

from panel.custom import JSComponent

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

from panel.custom import JSComponent

class CustomEventExample(JSComponent):

    value = param.String()

    _esm = """
    export function render({ model }) {
      const btn = document.createElement('button')
      btn.innerHTML = `Click Me`;
      btn.onclick = (event) => {
        const currentDate = new Date();
        model.send_msg(currentDate.getTime())
      }
      return btn
    }
    """

    def _handle_msg(self, msg):
        unix_timestamp = msg/1000
        python_datetime = datetime.datetime.fromtimestamp(unix_timestamp)
        self.value = str(python_datetime)

button = CustomEventExample()

pn.Column(button, button.param.value)
```

## Dependency Imports

JavaScript dependencies can be directly imported via URLs, such as those from `esm.sh`.

```python
import panel as pn

from panel.custom import JSComponent

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

ConfettiButton()
```

Use the `_importmap` attribute for more concise module references.

```python
import panel as pn

from panel.custom import JSComponent

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

ConfettiButton()
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
  model.on('value', () => {
    btn.innerHTML = `count is ${model.value}`;
  });
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

Serve the app with `panel serve counter_button.py --dev`.

You can now edit the JavaScript or CSS file, and the changes will be automatically reloaded.

- Try changing the `innerHTML` from `count is ${model.value}` to `COUNT IS ${model.value}` and observe the update. Note you must update `innerHTML` in two places.
- Try changing the background color from `#0072B5` to `#008080`.

## Displaying A Single Child

You can display Panel components (`Viewable`s) by defining a `Child` parameter.

Lets start with the simplest example:

```python
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

Example(child=pn.panel("A **Markdown** pane!"))
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```python
Example(child="A **Markdown** pane!")
```

If you want to allow a certain type of Panel components only you can specify the specific type in the `class_` argument.

```python
import panel as pn

from panel.custom import Child, JSComponent

class ChildExample(JSComponent):

    child = Child(class_=pn.pane.Markdown)

    _esm = """
    export function render({ model }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      return button
    }"""

ChildExample(child=pn.panel("A **Markdown** pane!"))
```

The `class_` argument also supports a tuple of types:

```python
    child = Child(class_=(pn.pane.Markdown, pn.pane.HTML))
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```python
import panel as pn

from panel.custom import Children, JSComponent

class ChildrenExample(JSComponent):

    objects = Children()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      div.append(...model.get_child("objects"))
      return div
    }"""

ChildrenExample(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(label="Click me!"), {"text": "I'm shown as a JSON Pane"}]
)
```

:::note
You can change the `item_type` to a specific subtype of `Viewable` or a tuple of
`Viewable` subtypes.
:::

### Render Policy

By default the `render_policy='children'`, which means that when we update the children the component is re-rendered (i.e. the contents are cleared and `render` is called again). To manually handle child updates you can set `_render_policy='manual' and define a handler that will add the updated children to the DOM:

```python
class ManualExample(JSComponent):

    objects = Children()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      const render_objects = () => div.replaceChildren(...model.get_child('objects'))
      model.on('objects', render_objects)
      render_objects()
      return div
    }"""

    _render_policy = 'manual'

manual = ManualExample(
    objects=[pn.panel("A **Markdown** pane!"), pn.widgets.Button(label="Click me!")]
)

manual
```

Now when we update the `objects` parameter, containing our children, the `render_objects` handler is called instead of re-creating the entire component from scratch.

```python
manual.objects = [pn.panel("A different **Markdown** pane!"), pn.widgets.Button(label="Click me!")]
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
