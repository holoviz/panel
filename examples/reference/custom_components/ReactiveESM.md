# `ReactiveESM`

`ReactiveESM` makes it easy to create custom Panel components using JavaScript.

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
            data.value+=1
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

`ReactiveESM` was introduced June 2024 to be the successor of `ReactiveHTML`.

`ReactiveESM` is very similar to [`AnyWidget`](https://anywidget.dev/), but `ReactiveESM` is optimized for usage with Panel.

:::

## Api

### ReactiveESM Attributes

* **`_esm`** (str | PurePath): An [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules) string or a path pointing to a [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). If you are developing in a notebook or with `--autoreload` the file will automatically be reloaded when saved. The ECMAScript module should export a `render` function.
* **`_import_map`** (dict): An [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) allows you to control how module specifiers are resolved.
* **`_stylesheets`** (optional list of strings): An Optional  list of CSS strings.

#### `render` Function

The `render` function can accept the following arguments:

- **`children`**: DON'T KNOW HOW TO EXPLAIN
- **`data`**: The `data` element corresponds to the custom components Python Parameters and provides methods to `.watch` for parameter changes and `.send_event` back to Python.
- **`el`**: The main html element of the component. Append elements to this element to display them. IS THIS OBSOLETE AS YOU SHOULD BE RETURNING THE ELEMENT TO RENDER?
- **`html`**: The `html` function enables JSX-like syntax in plain JavaScript without a transpiler. See [`htm`](https://github.com/developit/htm). IS THIS OBSOLETE?
- **`model`**: The Bokeh model. DON'T KNOW HOW TO EXPLAIN
- **`view`**: The Bokeh view. DON'T KNOW HOW TO EXPLAIN

The `render` function should return the html element to display.

#### Lifecycle Methods

The `render` function is run for each independent instance of the component. Besided the `render` function you can also export

- `initialize`: Is executed once per widget instance, during model initialization. It has access to model to setup non-view event handlers or state to share across views. ANYWIDGET NEEDS THIS.
- `after_layout`: DO WE STILL NEED SOMETHING LIKE THAT TO RESIZE OR REDRAW?
- `teardown`: DO WE NEED SOME EVENT TO CLEAN UP?

## Usage

### CSS

You can include CSS in the `_stylesheets` attribute. The CSS will be injected into the component.

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
            border: 0px solid black;padding:10px;
            border-radius:4px;
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
            data.value+=1
        });
        data.watch(() => {
            btn.innerHTML = `count is ${data.value}`;
          }, 'value')
        return btn
    }
    """

StyledCounterButton().servable()
```

## Send Events from Javascript to Python

You can send events from JavaScript to Python using the `data.send_event` method. You can handle the event in Python by defining an `on_<event_name>` method.

```python
import panel as pn
import param

pn.extension()

class ButtonEventExample(pn.ReactiveESM):

    value = param.Parameter()

    _esm = """
    export function render({ data }) {
        const btn = document.createElement('button')
        btn.innerHTML = `Click Me`;
        btn.onclick = (event) => data.send_event('click', event)
        return btn
    }
    """

    def on_click(self, event):
        self.value=str(event.__dict__)

button = ButtonEventExample()
pn.Column(
    button, pn.widgets.TextAreaInput(value=button.param.value, height=200),
).servable()
```

## Dependency Imports

JavaScript dependencies can be imported directly via a fully qualified URL for example from [`esm.sh`](https://esm.sh/).

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

ConfettiButton()
```

We can use the `_import_map` attribute to user shorter module names when importing

```python
import panel as pn

pn.extension()

class ConfettiButton(pn.ReactiveESM):
    _import_map = {
        "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
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

## External Files

You can also load the JavaScript from an external file by providing a path to the `_esm` attribute.

Create the file **counter_button.py**.

```python
from pathlib import Path

import param

import panel as pn

pn.extension()


class CounterButton(pn.ReactiveESM):

    value = param.Integer()

    _esm = Path("counter_button.js")


CounterButton().servable()
```

Now create the file **counter_button.js**.

```javascript
export function render({ data }) {
    let btn = document.createElement("button");
    btn.innerHTML = `count is ${data.value}`;
    btn.addEventListener("click", () => {
        data.value+=1
    });
    data.watch(() => {
        btn.innerHTML = `count is ${data.value}`;
      }, 'value')
    return btn
}
```

Serve the app with `pane serve counter_button.py --autoreload`.

Now you can edit the JavaScript file and the changes will be automatically reloaded. Try changing the `innerHTML` to `Count is ${data.value}` and see how it updates.

## React with JSX

If you want to use [React](https://react.dev/) with [JSX](https://react.dev/learn/writing-markup-with-jsx) instead of plain JavaScript as above this is also possible.

```python
import panel as pn
import param

pn.extension()

class ReactInputExample(pn.ReactiveESM):

    value = param.String()

    _esm = """
    function App(props) {
        const [value, setValue ] = props.state.value
        return (
        <div>
            <input
            id="input"
            value={value}
            onChange={e => setValue(e.target.value)}
            />
        </div>
        );
    }

    export function render({ state }) {
        return <App state={state}/>;
    }
    """

ReactInputExample(value="Hello World").servable()
```
