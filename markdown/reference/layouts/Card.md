# Card
---
```python
import panel as pn
pn.extension()
```

The ``Card`` layout allows arranging multiple Panel objects in a collapsible, vertical container with a header bar. It has a list-like API with methods for interactively updating and modifying the layout, including ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__`` (for replacing the card's contents).

`Card` components are very helpful for laying out components in a grid in a complex dashboard to make clear visual separations between different sections. The ability to collapse them can also be very useful to save space on a page with a lot of components.

#### Parameters:

* **``collapsed``** (bool): Whether the `Card` is collapsed.
* **``collapsible``** (bool): Whether the `Card` can be expanded and collapsed.
* **``header``** (Viewable): A Panel component to display in the header bar of the Card.
* **``hide_header``** (bool): Whether to hide the `Card` header.
* **``objects``** (list): The list of objects to display in the Card, which will be formatted like a `Column`. Should not generally be modified directly except when replaced in its entirety.
* **``title``** (str): The title to display in the header bar if no explicit `header` is defined.

Styling related parameters:

* **``active_header_background``** (str): The background color of the header when the `Card` is expanded.
* **``background``** (str): The background color of the content area.
* **``header_color``** (str): The color of the header text.
* **``button_css_classes``** (list[str]): The list of CSS classes to apply to the collapse button.
* **``css_classes``** (list[str]): The list of CSS classes to apply to the main area.
* **``header_background``** (str): The background color of the header.
* **``header_css_classes``** (list[str]): The list of CSS classes to apply to the header.

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

___

A ``Card`` layout can either be instantiated as empty and populated after the fact, or by using a list of objects provided on instantiation as positional arguments. If the objects are not already Panel components they will each be converted to one using the ``pn.panel`` conversion method. Unlike the `Row` and `Column` layouts, a `Card` has an explicit `title` that will be shown in the header bar alongside the collapse button (if the `collapsible` parameter is enabled):

```python
w1 = pn.widgets.TextInput(label='Text:')
w2 = pn.widgets.FloatSlider(label='Slider')

card = pn.Card(w1, w2, title='Card', styles={'background': 'WhiteSmoke'})
card
```

The contents of the ``Card.objects`` list should never be modified individually, because Panel cannot detect when items in that list have changed internally, and will thus fail to update any already-rendered views of those objects. Instead, use the provided methods for adding and removing items from the list.  The only change that is safe to make directly to ``Card.objects`` is to replace the list of ``objects`` entirely.  As a simple example of using the methods, we might add an additional widget to the card using the append method:

```python
w3 = pn.widgets.Select(options=['A', 'B', 'C'])
card.append(w3)
```

On a live server or in a notebook the `card` displayed after the previous code cell (above) will dynamically expand in size to accommodate all three widgets and the title. To see the effect in a statically rendered page, we will display the column a second time:

```python
card
```

Whether the `Card` is collapsed or not can be controlled from Python and Javascript:

```python
print(card.collapsed)
card.collapsed = True
```

### Header

Instead of using a `title`, a `Card` may also be given an explicit `header` that can contain any component, e.g. in this case the Panel logo:

```python
logo = 'https://panel.holoviz.org/_static/logo_horizontal.png'

red   = pn.Spacer(styles=dict(background='red'), height=50)
green = pn.Spacer(styles=dict(background='green'), height=50)
blue  = pn.Spacer(styles=dict(background='blue'), height=50)

pn.Card(
    red, green, blue,
    header_background='#2f2f2f',
    header_color='white',
    header=pn.panel(logo, height=40),
    width=300,
)
```

It is also possible to render a `Card` entirely without a header:

```python
pn.Card(
    pn.indicators.Number(value=42, default_color='white', label='Completion', format='{value}%'),
    styles={'background': 'lightgray'},
    hide_header=True,
    width=160
)
```

### Layout

In general a ``Card`` does not have to be given an explicit ``width``, ``height``, or ``sizing_mode``, allowing it to adapt to the size of its contents. However in certain cases it can be useful to declare a fixed-size layout, which its responsively sized contents will then fill, making it possible to achieve equal spacing between multiple objects:

```python
red   = pn.Spacer(styles=dict(background='red'), sizing_mode='stretch_both')
green = pn.Spacer(styles=dict(background='green'), sizing_mode='stretch_both')
blue  = pn.Spacer(styles=dict(background='blue'), sizing_mode='stretch_both')

pn.Card(red, green, blue, height=300, width=200, title='Fixed size')
```

When no fixed size is specified the column will expand to accommodate the sizing behavior of its contents:

```python
from bokeh.plotting import figure

p1 = figure(height=250, sizing_mode='stretch_width', margin=5)
p2 = figure(height=250, sizing_mode='stretch_width', margin=5)

p1.line([1, 2, 3], [1, 2, 3])
p2.scatter([1, 2, 3], [1, 2, 3])

pn.Card(p1, pn.layout.Divider(), p2, title="Responsive", sizing_mode='stretch_width')
```

---
