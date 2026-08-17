# PyComponent
---
```python
import panel as pn
import param

pn.extension()
```

A `PyComponent`, unlike a `Viewer` class inherits the entire API of Panel components, including all layout and styling related parameters. It doesn't just imitate a Panel component, it actually **is** one and therefore is a good option to build some composite widget made up of other widgets, a layout with some special behavior or a pane that renders some type of object in a way that is useful but does not require novel functionality.

```python
from panel.custom import PyComponent
from panel.widgets import WidgetBase 

class CounterButton(PyComponent, WidgetBase):

    value = param.Integer(default=0)

    def __panel__(self):
        return pn.widgets.Button(
            label=self._button_name, on_click=self._on_click
        )

    def _on_click(self, event):
        self.value += 1

    @param.depends("value")
    def _button_name(self):
        return f"count is {self.value}"

CounterButton()
```

## API

### Attributes

The `PyComponent` class inherits the entire Panel `Viewable` API including all sizing, layout and styling related parameters such as `width`, `height`, `sizing_mode` etc.

### Methods

- **`__panel__`**: Must be implemented. Should return the Panel component or object to be displayed. Will be lazily evaluated and cached on render.
- **`servable`**: This method serves the component using Panel's built-in server when running `panel serve ...`.
- **`show`**: Displays the component in a new browser tab when running `python ...`.

## Usage

### Styling with CSS

You can style the component by styling the component(s) returned by `__panel__` using their `styles` or `stylesheets` attributes.

```python
class StyledCounterButton(PyComponent):

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

    def _on_click(self, event):
        self.value += 1

    @param.depends("value")
    def _button_name(self):
        return f"Clicked {self.value} times"

    def __panel__(self):
        return pn.widgets.Button(
            label=self._button_name,
            on_click=self._on_click,
            stylesheets=self._stylesheets
        )

StyledCounterButton().servable()
```

See the [Apply CSS](../../how_to/styling/apply_css.md) guide for more information on styling Panel components.

## Displaying A Single Child

You can display Panel components (`Viewable`s) by defining a `Child` parameter.

Let's start with the simplest example:

```python
from panel.custom import Child

class SingleChild(PyComponent):

    object = Child()

    def __panel__(self):
      return pn.Column("A Single Child", self.param.object.rx())

single_child = SingleChild(object=pn.pane.Markdown("A **Markdown** pane!"))

single_child.servable()
```

Calling `self.param.object.rx()` creates a reactive expression which updates when the `object` parameter is updated.

Let's replace the `object` with a `Button`:

```python
single_child.object = pn.widgets.Button(label="Click me")
```

Let's change it back

```python
single_child.object = pn.pane.Markdown("A **Markdown** pane!")
```

If you provide a non-`Viewable` child it will automatically be converted to a `Viewable` by `pn.panel`:

```python
SingleChild(object="A **Markdown** pane!").servable()
```

If you want to allow a certain type of Panel components only, you can specify the specific type in the `class_` argument.

```python
class SingleChild(PyComponent):

    object = Child(class_=pn.pane.Markdown)

    def __panel__(self):
        return pn.Column("A Single Child", self.param.object.rx())

SingleChild(object=pn.pane.Markdown("A **Markdown** pane!")).servable()
```

The `class_` argument also supports a tuple of types:

```python
    object = Child(class_=(pn.pane.Markdown, pn.widgets.Button))
```

## Displaying a List of Children

You can also display a `List` of `Viewable` objects using the `Children` parameter type:

```python
from panel.custom import Children

class MultipleChildren(PyComponent):

    objects = Children()

    def __panel__(self):
        return pn.Column(objects=self.param['objects'], styles={"background": "silver"})

MultipleChildren(
    objects=[
        pn.panel("A **Markdown** pane!"),
        pn.widgets.Button(label="Click me!"),
        {"text": "I'm shown as a JSON Pane"},
    ]
).servable()

```

:::note
You can change the `item_type` to a specific subtype of `Viewable` or a tuple of `Viewable` subtypes.
:::

## References

### Tutorials

- [Reusable Components](../../tutorials/intermediate/reusable_components.md)

### How-To Guides

- [Combine Existing Widgets](../../how_to/custom_components/python/create_custom_widget.md)

---
