# ColorMap
---
```python
import panel as pn
pn.extension()
```

The `ColorMap` widget allows selecting a `value` from a dictionary containing color palettes. The widget is similar to a [`Select` widget](./Select) except it allows only valid color palettes, i.e. lists of hex or named colors or matplotlib colormaps.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`options`** (list or dict): A list or dictionary of options to select from
* **`ncols`** (int, default=1): Number of columns.
* **`swatch_height`** (int, default=20): Height of colormap swatch.
* **`swatch_width`** (int, default=100): Width of colormap swatch.
* **`value`** (list[str]): The current value; must be one of the option values
* **`value_name`** (str): The name of the selected colormap.

##### Display

* **`disabled`** (boolean): Whether the widget is editable
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The `options` of a `ColorMap` must be a dictionary containing a list of colors specified as hex values, named colors or `rgba()` CSS color specifications. You may provide either the concrete colormap as the `value` or the name of the colormap in the dictionary using the `value_name`:

```python
cmaps = {
    'Reds': ['lightpink', 'red', 'darkred'],
    'Blues': ['rgba(0, 0, 255, 1)', 'rgba(0, 0, 170, 1)', 'rgba(0, 0, 85, 1)'],
    'Greens': ['#00ff00', '#00aa00', '#004400']
}

color_map = pn.widgets.ColorMap(options=cmaps, value_name='Reds', width=200, margin=(0, 0, 100, 0))

color_map
```

When rendering many colormaps you can enable `ncols` and control the size of the color swatches using the `swatch_width` and `swatch_height` options:

```python
import colorcet as cc

pn.widgets.ColorMap(options=cc.palette, ncols=3, swatch_width=100, margin=(0, 0, 200, 0))
```

The widget also supports matplotlib colormaps:

```python
from matplotlib.cm import Reds, Blues, Greens

pn.widgets.ColorMap(options={'Reds': Reds, 'Blues': Blues, 'Greens': Greens}, margin=(0, 0, 100, 0))
```

### Controls

The `ColorMap` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(color_map.controls(jslink=True), color_map)
```

---
