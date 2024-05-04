# `ReactiveESM`

`ReactiveESM` makes it easy to create custom Panel components using JavaScript.

```python
import panel as pn
import param

pn.extension()

class CounterButton(pn.ReactiveESM):

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

CounterButton().servable()
```

:::{note}

`ReactiveESM` was introduced June 2024 as the expected successor of `ReactiveHTML`.

`ReactiveESM` is very similar to [`AnyWidget`](https://anywidget.dev/), but `ReactiveESM` is optimized for usage with Panel.

:::

## Api

### Attributes

* **`_esm`** (str | PurePath): An [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules) string or a path pointing to a [ECMAScript module](https://nodejs.org/api/esm.html#modules-ecmascript-modules). If you are developing in a notebook or with `--autoreload` the file will automatically be reloaded when saved. The ECMAScript module should define a `render` function.
* **`_import_map`** (dict): An [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) allows you to control how module specifiers are resolved.
* **`_stylesheets`** (optional list of strings): An Optional  list of CSS strings.


### Render Function

The `render` function can accept the following arguments:

- **`children`**: DON'T KNOW HOW TO EXPLAIN
- **`data`**: The data element corresponds to the custom component Python Parameters and provides methods to `.watch` for parameter changes and `send_event`.
- **`el`**: The element to render into
- **`html`**: The `html` function enables JSX-like syntax in plain JavaScript without a transpiler. See [`htm`](https://github.com/developit/htm).
- **`model`**: The Bokeh model. DON'T KNOW HOW TO EXPLAIN
- **`view`**: The Bokeh view. DON'T KNOW HOW TO EXPLAIN

The `render` function should return the html element to display.

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

## React

If you want to use React instead of plain JavaScript as above this is also possible.

```python
import panel as pn
import param

pn.extension()

class ReactInputExample(pn.ReactiveESM):

    text = param.String()

    _esm = """
    function App(props) {
        const [text, setText ] = props.state.text
        return (
        <div>
            <input
            id="input"
            value={text}
            onChange={e => setText(e.target.value)}
            />
        </div>
        );
    }

    export function render({ state }) {
        return <App state={state}/>;
    }
    """

ReactInputExample().servable()
```
