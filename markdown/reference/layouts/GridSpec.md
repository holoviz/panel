# GridSpec
---
```python
import panel as pn
pn.extension()
```

The ``GridSpec`` layout is an *array like* layout that allows arranging multiple Panel objects in a grid using a simple API to assign objects to individual grid cells or to a grid span.

Other layout containers function like lists, but a `GridSpec` has an API similar to a 2D array, making it possible to use 2D assignment to populate, index, and slice the grid.

See `GridStack` for a similar layout that allows the user to resize and drag the cells.

#### Parameters:

* **``ncols``** (int): Limits the number of columns that can be assigned.
* **``nrows``** (int): Limits the number of rows that can be assigned.
* **``mode``** (str): Whether to 'warn', 'error', or simply 'override' on overlapping assignment
* **``objects``** (list): The list of objects to display in the GridSpec. Should not generally be modified directly except when replaced in its entirety.

For layout and styling-related parameters see the [Control the size](../../tutorials/basic/size.md), [Align Content](../../tutorials/basic/align.md) and [Style](../../tutorials/basic/style.md) tutorials.

___

A ``GridSpec`` can be created either with a fixed size (the default) or with responsive sizing. In both cases the ``GridSpec`` will modify the contents to ensure the objects fill the grid cells assigned to them.

To demonstrate this behavior, let us declare a fixed-size ``GridSpec`` and then assign ``Spacer`` objects with distinct colors. We populate a ``3x4`` grid with these objects and display it:

```python
gspec = pn.GridSpec(width=800, height=600)

gspec[:,   0  ] = pn.Spacer(styles=dict(background='red'))
gspec[0,   1:3] = pn.Spacer(styles=dict(background='green'))
gspec[1,   2:4] = pn.Spacer(styles=dict(background='orange'))
gspec[2,   1:4] = pn.Spacer(styles=dict(background='blue'))
gspec[0:1, 3:4] = pn.Spacer(styles=dict(background='purple'))

gspec
```

As we can see the fixed-size ``GridSpec`` fills the `800x600` pixels assigned to it and each of the Spacer objects has been resized to fill the allotted grid cells, including the empty grid cell in the center. A convenient way to get an overview of the grid without rendering it is to display the ``grid`` property, which returns an array showing which grid cells have been filled:

```python
gspec.grid
```

In addition to assigning objects to the grid we can also index the grid:

```python
gspec[2, 2]
```

And select a subregion using slicing semantics:

```python
gspec[0, 1:]
```

The behavior when replacing existing grid cells can be controlled using the ``mode`` option. By default the ``GridSpec`` will warn when assigning to one or more grid cells that are already occupied. The behavior may be changed to either error or override silently, by setting ``mode='error'`` or ``mode='override'`` respectively.

### Responsive grids

In addition to fixed-size grids, ``GridSpec`` also supports all the standard sizing modes outlined in the [Sizing how-to guide](../../how_to/layout/size.md). Responsive sizing modes allow declaring grids that rescale dynamically when the browser window is resized and when loading the app or dashboard on different devices. Just like the fixed-width mode, the ``GridSpec`` will automatically set responsive sizing modes on the grid contents to fill the space correctly. To control the maximum and minimum size of the grid, use the `max_` and `min_` `width` and `height` options.

```python
import holoviews as hv
import holoviews.plotting.bokeh

from bokeh.plotting import figure

fig = figure()
fig.scatter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 2, 1, 0, -1, -2, -3])

gspec = pn.GridSpec(sizing_mode='stretch_both', max_height=800)

gspec[0, :3] = pn.Spacer(styles=dict(background='#FF0000'))
gspec[1:3, 0] = pn.Spacer(styles=dict(background='#0000FF'))
gspec[1:3, 1:3] = fig
gspec[3:5, 0] = hv.Curve([1, 2, 3])
gspec[3:5, 1] = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
gspec[4:5, 2] = pn.Column(
    pn.widgets.FloatSlider(),
    pn.widgets.ColorPicker(),
    pn.widgets.Toggle(label='Toggle Me!'))

gspec
```

---
