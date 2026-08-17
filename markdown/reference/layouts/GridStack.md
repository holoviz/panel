# GridStack
---
```python
import panel as pn

from panel.layout.gridstack import GridStack

pn.extension('gridstack')
```

The ``GridStack`` layout allows arranging multiple Panel objects in a grid using a simple API to assign objects to individual grid cells or to a grid span. Other layout containers function like lists, but a `GridSpec` has an API similar to a 2D array, making it possible to use 2D assignment to populate, index, and slice the grid.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``allow_resize``** (bool): Whether to allow resizing grid cells.
* **``allow_drag``** (bool): Whether to allow dragging grid cells.
* **``ncols``** (int): Allows specifying a fixed number of columns (otherwise grid expands to match assigned objects)
* **``nrows``** (int): Allows specifying a fixed number of rows (otherwise grid expands to match assigned objects)
* **``mode``** (str): Whether to 'warn', 'error', or simply 'override' on overlapping assignment
* **``objects``** (list): The list of objects to display in the GridSpec. Should not generally be modified directly except when replaced in its entirety.

___

A ``GridStack`` can be created either with a fixed size (the default) or with responsive sizing. In both cases the ``GridSpec`` will modify the contents to ensure the objects fill the grid cells assigned to them.

To demonstrate this behavior, let us declare a responsively sized ``GridStack`` and then assign ``Spacer`` objects with distinct colors. We populate a ``6x12`` grid with these objects and display it:

```python
gstack = GridStack(sizing_mode='stretch_both', min_height=600)

gstack[ : , 0: 3] = pn.Spacer(styles=dict(background='red'))
gstack[0:2, 3: 9] = pn.Spacer(styles=dict(background='green'))
gstack[2:4, 6:12] = pn.Spacer(styles=dict(background='orange'))
gstack[4:6, 3:12] = pn.Spacer(styles=dict(background='blue'))
gstack[0:2, 9:12] = pn.Spacer(styles=dict(background='purple'))

gstack
```

As we can see the fixed-size ``GridStack`` fills the `800x600` pixels assigned to it and each of the Spacer objects has been resized to fill the allotted grid cells, including the empty grid cell in the center. A convenient way to get an overview of the grid without rendering it is to display the ``grid`` property, which returns an array showing which grid cells have been filled:

```python
gstack.grid
```

In addition to assigning objects to the grid we can also index the grid:

```python
pn.Row(gstack[2, 2], width=400, height=400)
```

And select a subregion using slicing semantics:

```python
gstack[0, 3:]
```

The behavior when replacing existing grid cells can be controlled using the ``mode`` option. By default the ``GridStack`` will warn when assigning to one or more grid cells that are already occupied. The behavior may be changed to either error or override silently, by setting ``mode='error'`` or ``mode='override'`` respectively.

### Fixed size grids

We can also set explicit `width` and `height` values on a `GridStack`. Just like in the responsive mode, the ``GridStack`` will automatically set the appropriate sizing values on the grid contents to fill the space correctly. This means that when we resize a component and the state is synced with Python the new size is computed there and only then is the display updated:

```python
import holoviews as hv
import holoviews.plotting.bokeh

from bokeh.plotting import figure

fig = figure()
fig.scatter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 2, 1, 0, -1, -2, -3])

gstack = GridStack(width=800, height=600)

gstack[0, :3] = pn.Spacer(styles=dict(background='#FF0000'))
gstack[1:3, 0] = pn.Spacer(styles=dict(background='#0000FF'))
gstack[1:3, 1:3] = fig
gstack[3:5, 0] = hv.Curve([1, 2, 3])
gstack[3:5, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
gstack[3:5, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(label='Toggle Me!')
)

gstack
```

---
