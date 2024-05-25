# Migrating from AnyWidget to Panel

This guide addresses how to migrate from [AnyWidget](https://anywidget.dev/) to Panel custom components. You might want to do this to create a Panel-native component that works better with Panel or is further customized to your needs.

:::note
Note that AnyWidget widgets are [`ipywidgets`](https://ipywidgets.readthedocs.io/en/stable/) and can be used directly in Panel via the [`IpyWidgets`](../../reference/panes/IPyWidget.ipynb) pane without a migration.
:::

## Migration Steps

The high-level steps needed for migrating from `AnyWidgets` components to Panel components are described in the section below.

### Migrate Python Code

#### Step 1: Base Class Migration

Migrate from the `AnyWidget` base class to the Panel [`JSComponent`](../../reference/panes/JSComponent.md) base class. If the `_esm` script is based on React, use the [`ReactComponent`](../../reference/panes/ReactComponent.md). For Preact, use the [`PreactComponent`](../../reference/panes/JSComponent.md).

#### Step 2: Attribute Migration

Migrate from `AnyWidget`'s [Traitlets](https://traitlets.readthedocs.io/en/stable/) based attributes to Panel's [Param](https://param.holoviz.org) based parameters.

Migrate the attributes below:

| `AnyWidget` | Comment                        | `Panel`        | Comment                                                          |
| ----------- | ------------------------------ | -------------- | ---------------------------------------------------------------- |
| `_esm`      | JavaScript string or Path      | `_esm`         | JavaScript string or Path                                        |
| `_css`      | CSS string or Path             | `_stylesheets` | List of CSS strings or Paths                                     |
| NA          | Not Available                  | `_import_map`  | [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap) |

### Migrate JavaScript Code

#### Step 3: Export Migration

Migrate the functions below:

| `AnyWidget` | Comment                                              | `JSComponent` | Comment                                                          |
| ----------- | ---------------------------------------------------- | ------------- | ---------------------------------------------------------------- |
| `initialize`| Has access to `model`.<br>Can return *end of life* callback. | NA            | Not Available                                                    |
| `render`    | Has access to `model` and `el`.<br>Can return *end of life* callback. | `render`     | Has access to `data`, `children`, `model`, `el`, and `view`.<br>Can return an `html` element to be appended to `el`. |

In the `_esm` script, migrate the `default` export required by `AnyWidget` to one or more named exports required by Panel.

### Migrate React Code

#### Step 4: Drop JavaScript Tooling

Drop the local JavaScript tooling required by `AnyWidget`. Panel replaces this with automatic transpiling in the browser by [Sucrase](https://sucrase.io/).

#### Step 5: Migrate `useModelState` to `state`

The `ReactComponent` `_esm` script works similarly to the `JSComponent` `_esm` script with the following differences:

| `AnyWidget` | Comment                                      | `ReactComponent` | Comment                                      |
| ----------- | -------------------------------------------- | ------------- | -------------------------------------------- |
| `render`    | Can use imports from `react` and `@anywidget/react` modules like `useState` and `useModelState` | `render`      | Can use imports from the `react` module like `useState`.<br><br>Has access to `state`. |

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

### Maria Chime Button

Check out our [Custom Components Tutorial](../../../tutorials/expert/custom_components.md) to see a migrated version of the [ipymaria](https://github.com/manzt/ipymario) component.

[![Mario chime button](https://private-user-images.githubusercontent.com/24403730/311924409-e8befac9-3ce5-4ffc-a9df-3b18479c809a.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTY2MTg1OTMsIm5iZiI6MTcxNjYxODI5MywicGF0aCI6Ii8yNDQwMzczMC8zMTE5MjQ0MDktZThiZWZhYzktM2NlNS00ZmZjLWE5ZGYtM2IxODQ3OWM4MDlhLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTI1VDA2MjQ1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWFjOWEwNWE4YTI1MTAxNzA3ZWIyMWMyMmVhZThhOTE0ZjFjMDI3NWJjNTQ1YzI2YTZhNGM5M2UwMGY1NDBiMmYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.VPirrIBLCuIi1OYsuGeHbEtIfV6bavkUHNUkyrvj1_Q)](../../../tutorials/expert/custom_components.md)
