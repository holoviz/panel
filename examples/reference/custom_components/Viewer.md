# `Viewer`

`Viewer` simplifies the creation of custom Panel components using Python and Panel components only.

```pyodide
import panel as pn
import param

from panel.viewable import Viewer

pn.extension()

class CounterButton(Viewer):

    value = param.Integer()

    def __init__(self, **params):
        super().__init__()

        self._layout = pn.widgets.Button(
            name=self._button_name, on_click=self._on_click, **params
        )

    def _on_click(self, event):
        self.value += 1

    @param.depends("value")
    def _button_name(self):
        return f"Clicked {self.value} times"

    def __panel__(self):
        return self._layout

CounterButton().servable()
```

:::{note}

If you are looking to create new components using JavaScript, check out [`JSComponent`](JSComponent.md), [`ReactComponent`](ReactComponent.md), or [`AnyWidgetComponent`](AnyWidgetComponent.md) instead.

:::

## API

### Attributes

None. The `Viewer` class does not have any special attributes. It is a simple `param.Parameterized` class with a few additional methods. This also means you will have to add or support parameters like `height`, `width`, `sizing_mode`, etc., yourself if needed.

### Methods

- **`__panel__`**: Must be implemented. Should return the Panel component or object to be displayed.
- **`servable`**: This method serves the component using Panel's built-in server when running `panel serve ...`.
- **`show`**: Displays the component in a new browser tab when running `python ...`.

## Usage

### Styling with CSS

You can style the component by styling the component(s) returned by `__panel__` using their `styles` or `stylesheets` attributes.

```pyodide
import panel as pn
import param

from panel.viewable import Viewer

pn.extension()


class StyledCounterButton(Viewer):

    value = param.Integer()

    _stylesheets = [
        """
        :host(.solid) .bk-btn.bk-btn-default
        {
            background: #0072B5;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
        }
        :host(.solid) .bk-btn.bk-btn-default:hover {
            background: #4099da;
        }
        """
    ]

    def __init__(self, **params):
        super().__init__()

        self._layout = pn.widgets.Button(
            name=self._button_name,
            on_click=self._on_click,
            stylesheets=self._stylesheets,
            **params,
        )

    def _on_click(self, event):
        self.value += 1

    @param.depends("value")
    def _button_name(self):
        return f"Clicked {self.value} times"

    def __panel__(self):
        return self._layout


StyledCounterButton().servable()
```

See the [Apply CSS](../../how_to/styling/apply_css.md) guide for more information on styling Panel components.

## Displaying A Single Child

You can display Panel components (`Viewable`s) by defining a `Child` parameter.

Let's start with the simplest example:

```pyodide
import panel as pn

from panel.custom import Child
from panel.viewable import Viewer

class SingleChild(Viewer):

    object = Child()

    def __panel__(self):
      return pn.Column("A Single Child", self._object)

    @pn.depends("object")
    def _object(self):
      return self.object

single_child = SingleChild(object=pn.pane.Markdown("A **Markdown** pane!"))
single_child.servable()
```

The `_object` is a workaround to enable the `_layout` to replace the `object` component dynamically.

Let's replace the `object` with a `Button`:

```pyodide
single_child.object = pn.widgets.Button(name="Click me")
```

Let's change it back

```pyodide
single_child.object = pn.pane.Markdown("A **Markdown** pane!")
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```pyodide
SingleChild(object="A **Markdown** pane!").servable()
```

If you want to allow a certain type of Panel components only, you can specify the specific type in the `class_` argument.

```pyodide
import panel as pn

from panel.custom import Child
from panel.viewable import Viewer

class SingleChild(Viewer):

    object = Child(class_=pn.pane.Markdown)

    def __panel__(self):
      return pn.Column("A Single Child", self._object)

    @pn.depends("object")
    def _object(self):
      return self.object

SingleChild(object=pn.pane.Markdown("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types:

```pyodide
import panel as pn

from panel.custom import Child
from panel.viewable import Viewer

class SingleChild(Viewer):

    object = Child(class_=(pn.pane.Markdown, pn.widgets.Button))

    def __panel__(self):
      return pn.Column("A Single Child", self._object)

    @pn.depends("object")
    def _object(self):
      return self.object

SingleChild(object=pn.pane.Markdown("A **Markdown** pane!")).servable()
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```pyodide
import panel as pn

from panel.custom import Children
from panel.viewable import Viewer


class MultipleChildren(Viewer):

    objects = Children()

    def __init__(self, **params):
        self._layout = pn.Column(styles={"background": "silver"})

        super().__init__(**params)

    def __panel__(self):
        return self._layout

    @pn.depends("objects", watch=True, on_init=True)
    def _objects(self):
        self._layout[:] = self.objects


MultipleChildren(
    objects=[
        pn.panel("A **Markdown** pane!"),
        pn.widgets.Button(name="Click me!"),
        {"text": "I'm shown as a JSON Pane"},
    ]
).servable()
```

:::note

You can change the `item_type` to a specific subtype of `Viewable` or a tuple of `Viewable` subtypes.

:::

## References

### Tutorials

- [Reusable Components](../../../tutorials/intermediate/reusable_components.md)

### How-To Guides

- [Combine Existing Widgets](../../../how_to/custom_components/custom_viewer.md)
