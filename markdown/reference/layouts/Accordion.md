# Accordion
---
```python
import panel as pn
pn.extension()
```

``Accordion`` layouts are a type of ``Card`` layout that allows switching between multiple objects by clicking on the corresponding card header. The labels for each card may be defined explicitly as part of a tuple, and otherwise default to the ``name`` parameter of the card's contents. Like ``Column`` and ``Row``, ``Tabs`` has a list-like API that allows interactively updating and modifying the cards using methods ``append``, ``extend``, ``clear``, ``insert``, ``pop``, ``remove`` and ``__setitem__`` (to replace the contents).

#### Parameters:

* **``active``** (list, default=[]): The indexes of the currently displayed cards. Updates when a card is expanded or collapsed and may also be set to programmatically control which cards are shown.
* **``objects``** (list): The list of objects to display in the Column. Should not generally be modified directly except when replaced in its entirety.
* **``toggle``** (bool): Whether to toggle between the available cards, activating only one at a time (if True), or (if False) whether to allow multiple cards to be expanded simultaneously.

Styling-related parameters:

* **``active_header_background``** (str): The background color of the header when the `Card` is expanded.
* **``header_color``** (str): The color of the header text.
* **``header_background``** (str): The background color of the header.

For further layout and styling-related parameters see the [Control the size](../../tutorials/basic/size.md), [Align Content](../../tutorials/basic/align.md) and [Style](../../tutorials/basic/style.md) tutorials.

___

## Accordion

An ``Accordion`` layout can either be instantiated as empty and populated after the fact, or by using a list of objects provided on instantiation as positional arguments. If the objects are not already Panel components they will each be converted to one using the ``pn.panel`` conversion method. Unlike other panel types, ``Accordion`` also accepts tuples to specify the title of each tab; if no name is supplied explicitly the name of the underlying object will be used.

```python
from bokeh.plotting import figure

p1 = figure(width=300, height=300, name='Scatter', margin=5)
p1.scatter([0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 2, 1, 0])

p2 = figure(width=300, height=300, name='Line', margin=5)
p2.line([0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 2, 1, 0])

accordion = pn.Accordion(('Scatter', p1), p2)
accordion
```

The contents of the ``Accordion.objects`` list should never be modified individually, because Panel cannot detect when items in that list have changed internally, and will thus fail to update any already-rendered views of those objects (and their card titles!). Instead, use the provided methods for adding and removing items from the list.  The only change that is safe to make directly to ``Accordion.objects`` is to replace the list of ``objects`` entirely.  As a simple example of using the methods, we might add an additional widget to the ``Accordion`` using the `append` method:

```python
p3 = figure(width=300, height=300, name='Square', margin=5)
p3.scatter([0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 2, 1, 0], marker='square', size=10)

accordion.append(p3)
```

On a live server or in a notebook the `accordion` displayed above will dynamically expand to include the new card. To see the effect in a statically rendered page, we will display the accordion a second time:

```python
accordion
```

#### ``active``

In addition to being able to modify the ``objects`` using methods we can also get and set the currently ``active`` cards as a list of integers, which will update any rendered views of the object:

```python
print(accordion.active)
accordion.active = [0, 2]
```

#### ``toggle``

When toggle is enabled only one card can be active at the same time, i.e., expanding one card will collapse the other active cards (much like a Tabs layout).

```python
accordion.clone(toggle=True, active=[0])
```

---
