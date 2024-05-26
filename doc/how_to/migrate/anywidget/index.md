# Converting from AnyWidget to Panel

This guide addresses how to convert [AnyWidget](https://anywidget.dev/) widgets to custom Panel widgets.

Please note that AnyWidget widgets are [`ipywidgets`](https://ipywidgets.readthedocs.io/en/stable/) and can be used directly in Panel via the [`IpyWidgets`](../../reference/panes/IPyWidget.ipynb) pane and the `Traitlets` `@observe` API without a conversion. We recommend trying this option first. If it does not work for your use case, please consider contributing to the existing `AnyWidget` before converting it to a Panel widget.

Some reasons you might still want to convert an `AnyWidget` to a custom Panel widget are:

- Familiar and Optimized API: This enables your and your users to use the familiar `Param` parameter API for which Panel is optimized.
- Customization: You might want to use the `AnyWidget` as a starting point and customize it to your exact needs.
- Efficiency: You users avoid loading  `AnyWidget`/`ipywidgets` JavaScript libraries which ANECDOTALLY is not insignificant. Your users also avoid the overhead of converting between `Param/Panel/Bokeh` and `Traitlets`/`AnyWidget`/`ipywidgets` objects: ANECDOTALLY, Panel (i.e., Bokeh) utilizes faster serialization and deserialization methods and formats. IS THIS TRUE, PHILIPP? ALSO, WHEN USING THE ANYWIDGET ON THE BOKEH SERVER? DO WE HAVE NUMBERS FOR THIS?

## Conversion Steps

The high-level steps needed for converting `AnyWidgets` components to Panel components are described in the section below.

### Convert Python Code

#### Step 1: Base Class Conversion

Convert from the `AnyWidget` base class to the Panel [`JSComponent`](../../reference/panes/JSComponent.md) base class. If the `_esm` script is based on [React](https://react.dev/), use the [`ReactComponent`](../../reference/panes/ReactComponent.md). For [Preact](https://preactjs.com/), use the [`PreactComponent`](../../reference/panes/JSComponent.md).

#### Step 2: Attribute Conversion

Convert from `AnyWidget`'s [Traitlets](https://traitlets.readthedocs.io/en/stable/) based attributes to Panel's [Param](https://param.holoviz.org) based parameters.

Convert the attributes below:

| `AnyWidget` | Comment                        | `Panel`        | Comment                                                          |
| ----------- | ------------------------------ | -------------- | ---------------------------------------------------------------- |
| `_esm`      | JavaScript string or Path      | `_esm`         | JavaScript string or Path                                        |
| `_css`      | CSS string or Path             | `_stylesheets` | List of CSS strings or Paths                                     |
| NA          | Not Available                  | `_import_map`  | [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) |

### Convert JavaScript Code

#### Step 3: Export Conversion

Convert the functions below:

| `AnyWidget` | Comment                                              | `JSComponent` | Comment                                                          |
| ----------- | ---------------------------------------------------- | ------------- | ---------------------------------------------------------------- |
| `initialize`| Has access to `model`.<br>Can return *end of life* callback. | NA            | Not Available                                                    |
| `render`    | Has access to `model` and `el`.<br>Can return *end of life* callback. | `render`     | Has access to `data`, `children`, `model`, `el`, and `view`.<br>Can return an `html` element to be appended to `el`. |

In the `_esm` script, convert the `default` export required by `AnyWidget` to one or more *named exports* required by Panel.

Please note that the `AnyWidget` `model` is split across Panels `data`, `children` and `model`. Their methods are also different reflecting differences between Traitlets and Panel/ Bokeh JavaScript models:

| AnyWidget | Panel/ Bokeh |
| --------- | ----- |
| `model.get('some_value')` | `data.some_value`|
| `model.save('some_value', 1)`<br>`model.save_changes()` | `data.some_value=1`|
| `model.on("change:some_value", () => {...})` | `data.watch(() => {...}), 'some_value')` |

### Convert React Code

#### Step 4: Drop JavaScript Tooling

Drop the local JavaScript tooling required by `AnyWidget`. Panel replaces this with automatic transpiling in the browser by [Sucrase](https://sucrase.io/).

#### Step 5: Convert `useModelState` to `state`

The `ReactComponent` `_esm` script works similarly to the `JSComponent` `_esm` script with the following differences:

| `AnyWidget` | Comment                                      | `ReactComponent` | Comment                                      |
| ----------- | -------------------------------------------- | ------------- | -------------------------------------------- |
| `render`    | Can use imports from `react` and `@anywidget/react` modules like `useState` and `useModelState` | `render`      | Can use hooks like `useState` from the `React` object<br><br>Has access to model `state`. |

## Examples

### Basic `CounterWidget`

#### AnyWidget `CounterWidget`

```python
import anywidget
import traitlets

class CounterWidget(anywidget.AnyWidget):

    value = traitlets.Int(0).tag(sync=True)

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
```

#### Panel `CounterWidget`

```{pyodide}
import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class CounterButton(JSComponent):

    value = param.Integer()

    _esm = """
    export function render({ data }) {
        let count = () => data.value;
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${count()}`;
        btn.addEventListener("click", () => {
            data.value += 1
        });
        data.watch(() => {
            btn.innerHTML = `count is ${data.value}`;
          }, 'value')
        return btn
    }
    """

# Display the component
CounterButton().servable()
```

:::{note}

With Panel you may replace the lines `export function render({ data })` and `return btn` with the lines `export function render({ data, el })` and `el.appendChild(btn)`, if you want to minimize the number of changes.

:::

### React Counter Widget

#### AnyWidget React `CounterWidget`

To be determined (TBD).

#### Panel React `CounterWidget`

```{pyodide}
import panel as pn
import param

from panel.custom import ReactComponent

pn.extension()

class CounterButton(ReactComponent):

    value = param.Integer()

    _esm = """
    function App(props) {
        const [value, setValue] = props.state.value;
        return (
            <button onClick={e => setValue(value+1)}>
            count is {value}
            </button>
        );
    }

    export function render({state}) {
        return <App state={state}/>;
    }
    """

# Display the component
CounterButton().servable()
```

### Mario Button

Check out our [Custom Components Tutorial](../../../tutorials/expert/custom_components.md) to see a converted version of the [ipymario](https://github.com/manzt/ipymario) widget.

[![Mario Button](https://assets.holoviz.org/panel/tutorials/ipymario.gif)](../../../tutorials/expert/custom_components.md)

## References

### Tutorials

- [Build Custom Components](../../../how_to/custom_components/reactive_esm/reactive_esm_layout.md)

### How-To Guides

- [Convert `AnyWidget` widgets](../../../how_to/migrate/anywidget/index.md)

### Reference Guides

- [`JSComponent`](../../../reference/panes/JSComponent.md)
- [`ReactComponent`](../../../reference/panes/ReactComponent.md)
- [`PreactComponent`](../../../reference/panes/PreactComponent.md)

With these skills, you are now equipped to pioneer and push the boundaries of what can be achieved with Panel. Happy coding!
