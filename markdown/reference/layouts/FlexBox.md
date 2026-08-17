# FlexBox
---
```python
import panel as pn
pn.extension()
```

The ``FlexBox`` is a list-like layout (unlike ``GridSpec``) that wraps objects into a CSS flex container. It has a list-like API with methods to ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__``, which make it possible to interactively update and modify the layout and exposes all the CSS options for controlling the behavior and layout of the flex box.

For a detailed introduction to CSS flex boxes, see [this guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``align_content``** (str): Defines how a flex container's lines align when there is extra space in the cross-axis. One of 'normal', 'flex-start', 'flex-end', 'center', 'space-between', 'space-around', 'space-evenly', 'stretch', 'start', 'end', 'baseline', 'first baseline' and 'last baseline'.
* **``align_items``** (str): Defines the default behavior for how flex items are laid out along the cross axis on the current line. Same options as `align_content`.
* **``flex_direction``** (str): This establishes the main-axis, thus defining the direction flex items are placed in the flex container. One of 'row', 'row-reverse', 'column', 'column-reverse'.
* **``flex_wrap``** (str): Whether and how to wrap items in the flex container. One of 'nowrap', 'wrap', 'wrap-reverse'.
* **``gap``** (str): Defines the spacing between flex items, supporting various units (px, em, rem, %, vw/vh)
* **``justify_content``** (str): Defines the alignment along the main axis. One of 'flex-start', 'flex-end', 'center', 'space-between', 'space-around', 'space-evenly', 'start', 'end', 'left', 'right'.
* **``objects``** (list): The list of objects to display in the WidgetBox. Should not generally be modified directly except when replaced in its entirety.

___

A ``FlexBox`` layout can either be instantiated as empty and populated after the fact or using a list of objects provided as positional arguments. If the objects are not already panel components they will each be converted to one using the ``pn.panel`` conversion method. By default the `FlexBox` has a `flex_direction='row'` and uses `flex_wrap='wrap'`, which means items will flow in a row-wise manner

```python
import random

rcolor = lambda: "#%06x" % random.randint(0, 0xFFFFFF)

box = pn.FlexBox(*[pn.pane.HTML(str(i), styles=dict(background=rcolor()), width=100, height=100) for i in range(24)])
box
```

We can flip the direction by setting the `flex_direction` parameter to `'column'`:

```python
column_box = box.clone(flex_direction='column', height=450)
column_box
```

The other options including `align_content`, `align_items`, and `justify_content` control how items are spaced on the page, e.g. `align_content` declares how to distribute items along the cross-axis (i.e. along the row direction for a column based flexbox):

```python
column_box.clone(align_content='space-evenly')
```

In general it is preferred to modify layouts only through the provided methods and avoid modifying the ``objects`` parameter directly. The one exception is when replacing the list of ``objects`` entirely, otherwise it is recommended to use the methods on the ``FlexBox`` itself to ensure that the rendered views of the ``FlexBox`` are rerendered in response to the change. As a simple example we might assign a new item to the ``box`` using a setitem operation:

```python
color = pn.pane.HTML(str(5), styles=dict(background=rcolor()), width=100, height=100)
column_box[5] = color
```

To see the effect in a statically rendered page, we will display the box a second time:

```python
column_box
```

In general a ``FlexBox`` does not have to be given a ``width``, ``height`` or ``sizing_mode``, allowing it to adapt to the size of its contents.

## References

### Tutorials

- [Advanced Layouts](../../tutorials/intermediate/advanced_layouts.md)

---
