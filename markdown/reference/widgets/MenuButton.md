# MenuButton
---
```python
import panel as pn
pn.extension()
```

The ``MenuButton`` widget allows specifying a list of menu items to select from, triggering events when a menu item is clicked. Unlike other widgets, it does not have a ``value`` parameter. Instead it has a ``clicked`` parameter that can be watched to trigger events and which reports the last clicked menu item.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``clicked``** (str): The last clicked menu item
* **``items``** (list(tuple or str or None):  Menu items in the dropdown. Allows strings, tuples of the form (title, value) or Nones to separate groups of items.
* **``split``** (boolean): Whether to add separate dropdown area to button.

##### Display

* **`variant`** (str): The button style, either ``'solid'`` or ``'outline'``.
* **``color``** (str): A button theme; should be one of ``'default'`` (white), ``'primary'`` (blue), ``'success'`` (green), ``'info'`` (yellow), ``'light'`` (light), or ``'danger'`` (red)
* **`icon`** (str): An icon to render to the left of the button label. Either an SVG or an icon name which is loaded from [tabler-icons.io](https://tabler-icons.io)/.
* **`icon_size`** (str): Size of the icon as a string, e.g. 12px or 1em.
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The `MenuButton` is defined by the name of the button and a *list of items* corresponding to the menu items.

The items can be single string values or as below tuples of string values. By separating items by `None` we can group them into sections:

```python
menu_items = [('Option A', 'a'), ('Option B', 'b'), ('Option C', 'c'), None, ('Help', 'help')]

menu_button = pn.widgets.MenuButton(label='Dropdown', items=menu_items, color='primary')

pn.Column(menu_button, height=200)
```

The ``clicked`` parameter will report the last menu item that was clicked:

```python
menu_button.clicked
```

You can `bind` to the `clicked` parameter

```python
def handle_selection(clicked):
    return f'You clicked menu item: "{clicked}"'

pn.Column(
    menu_button,
    pn.bind(handle_selection, menu_button.param.clicked),
    height=200
)
```

The ``on_click`` method can trigger a function when a menu item is clicked:

```python
text = pn.widgets.TextInput(value='Ready')

def b(event):
    text.value = f'You clicked menu item: "{event.new}"'
    
menu_button.on_click(b)

pn.Row(menu_button, text, height=200)
```

### Styles

The style of the `MenuButton` can be set by selecting one of the available `color` values and the `variant` values:

```python
colors = ('default', 'primary', 'success', 'warning', 'danger', 'light')
variants = ("solid", "outline")

pn.Row(
    *(pn.Column(*(pn.widgets.MenuButton(label=color, color=color, variant=variant, items=menu_items) for color in colors))
    for variant in variants)
)
```

### Split Menu

Additionally we can move the dropdown indicator into a separate area using the split option:

```python
split_menu_button = pn.widgets.MenuButton(label='Split Menu', split=True, items=menu_items, color="primary")
pn.Column(split_menu_button, pn.bind(handle_selection, split_menu_button.param.clicked), height=200)
```

If the button itself is clicked in `split` mode, the `clicked` property will report the value of the `name` parameter, i.e. in this case clicking it will set the `clicked` parameter to `'Split Menu'`.

### Icons

The ``MenuButton`` name and its `items` may contain Unicode characters and emojis, providing a convenient way to define common graphical buttons.

For the button it self, you can use more advanced icons by providing an svg `icon` value or a named `icon` loaded from [tabler-icons.io](https://tabler-icons.io):

```python
file_items = ["\U0001F4BE Save", "🚪 Exit"]
help_items = ["⚖️ License", None, "\U0001F6C8 About"]
pn.Column(pn.Row(
    pn.widgets.MenuButton(label="File", icon="file", items=file_items, width=75, color="light"),
    pn.widgets.MenuButton(label="🧏🏻‍♂️ Help", items=help_items, width=100, color="light"),
    styles={"border-bottom": "1px solid black"}
    ), height=200, 
)
```

### Controls

The `MenuButton` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(menu_button.controls, menu_button)
```

---
