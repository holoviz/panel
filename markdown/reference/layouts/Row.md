# Row
---
```python
import panel as pn
pn.extension()
```

The ``Row`` layout allows arranging multiple panel objects in a horizontal container. It has a list-like API with methods to ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__``, which make it possible to interactively update and modify the layout.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``objects``** (list): The list of objects to display in the Column, should not generally be modified directly except when replaced in its entirety.
* **``scroll``** (boolean): Enable scrollbars if the content overflows the size of the container.

___

A ``Row`` layout can either be instantiated as empty and populated after the fact or using a list of objects provided as positional arguments. If the objects are not already panel components they will each be converted to one using the ``pn.panel`` conversion method.

```python
w1 = pn.widgets.TextInput(label='Text:')
w2 = pn.widgets.FloatSlider(label='Slider')

row = pn.Row('# Row', w1, w2, styles=dict(background='WhiteSmoke'))
row
```

In general it is preferred to modify layouts only through the provided methods and avoid modifying the ``objects`` parameter directly. The one exception is when replacing the list of ``objects`` entirely, otherwise it is recommended to use the methods on the ``Row`` itself to ensure that the rendered views of the ``Column`` are rerendered in response to the change. As a simple example we might add an additional widget to the ``row`` using the append method:

```python
w3 = pn.widgets.Select(options=['A', 'B', 'C'], label='Select')
row.append(w3)
```

On a live server or in a notebook the `row` displayed above will dynamically expand in size to accommodate all three widgets and the title. To see the effect in a statically rendered page, we will display the row a second time:

```python
row
```

In general a ``Row`` does not have to be given an explicit ``width``, ``height`` or ``sizing_mode``, allowing it to adapt to the size of its contents. However in certain cases it can be useful to declare a fixed-size layout, which its responsively sized contents will then fill, making it possible to achieve equal spacing between multiple objects:

```python
pn.Row(
    pn.Spacer(styles=dict(background='red'),   sizing_mode='stretch_both'),
    pn.Spacer(styles=dict(background='green'), sizing_mode='stretch_both'),
    pn.Spacer(styles=dict(background='blue'),  sizing_mode='stretch_both'),
    height=200, width=600
)
```

When no fixed size is specified the row will expand to accommodate the sizing behavior of its contents:

```python
from bokeh.plotting import figure

p1 = figure(height=200, sizing_mode='stretch_width')
p2 = figure(height=200, sizing_mode='stretch_width')

p1.line([1, 2, 3], [1, 2, 3])
p2.scatter([1, 2, 3], [1, 2, 3])

pn.Row(p1, p2)
```

Lastly it is also possible to enable scrollbars on the `Row` container in case the content overflows the specified height and width:

```python
pn.Row(
    pn.Spacer(styles=dict(background='red'), width=200, height=200),
    pn.Spacer(styles=dict(background='green'), width=200, height=200),
    pn.Spacer(styles=dict(background='blue'), width=200, height=200),
    scroll=True, width=420
)
```

---
