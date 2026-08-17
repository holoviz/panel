# WidgetBox
---
```python
import panel as pn
pn.extension()
```

The ``WidgetBox`` layout allows arranging multiple panel objects in a vertical container. It is largely identical to the ``Column`` layout but has some default styling that makes widgets be clearly grouped together visually. It has a list-like API with methods to ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__``, which make it possible to interactively update and modify the layout.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``objects``** (list): The list of objects to display in the WidgetBox. Should not generally be modified directly except when replaced in its entirety.
* **``disabled``** (boolean, default=False): Allow to disable all the widgets displayed in the WidgetBox.

___

A ``WidgetBox`` layout can either be instantiated as empty and populated after the fact or using a list of objects provided as positional arguments. If the objects are not already panel components they will each be converted to one using the ``pn.panel`` conversion method.

```python
w1 = pn.widgets.TextInput(label='Text:')
w2 = pn.widgets.FloatSlider(label='Slider')

box = pn.WidgetBox('# WidgetBox', w1, w2)
box
```

In general it is preferred to modify layouts only through the provided methods and avoid modifying the ``objects`` parameter directly. The one exception is when replacing the list of ``objects`` entirely, otherwise it is recommended to use the methods on the ``WidgetBox`` itself to ensure that the rendered views of the ``WidgetBox`` are rerendered in response to the change. As a simple example we might add an additional widget to the ``box`` using the append method:

```python
w3 = pn.widgets.Select(options=['A', 'B', 'C'])
box.append(w3)
```

On a live server or in a notebook the `box` above will dynamically expand in size to accommodate all three widgets and the title. To see the effect in a statically rendered page, we will display the box a second time:

```python
box
```

In general a ``WidgetBox`` does not have to be given a ``width``, ``height`` or ``sizing_mode``, allowing it to adapt to the size of its contents.

---
