# Toggle
---
```python
import panel as pn
pn.extension()
```

The ``Toggle`` widget allows toggling a single condition between ``True``/``False`` states. The ```Checkbox```, ```Toggle```, and ```Switch``` widgets are interchangeable.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (boolean): Whether the button is toggled or not

##### Display

* **`variant`** (str): The button style, either 'solid' or 'outline'.
* **``color``** (str): A button theme should be one of ``'default'`` (white), ``'primary'`` (blue), ``'success'`` (green), ``'info'`` (yellow), or ``'danger'`` (red)
* **`icon`** (str): An icon to render to the left of the button label. Either an SVG or an icon name which is loaded from [tabler-icons.io](https://tabler-icons.io)/.
* **`icon_size`** (str): Size of the icon as a string, e.g. 12px or 1em.
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
toggle = pn.widgets.Toggle(label='Toggle', color='success')

toggle
```

``Toggle.value`` is either True or False depending on whether the button is toggled:

```python
toggle.value
```

### Styles

The style of the `Toggle` can be set by selecting one of the available `color` values and the `variant` values:

```python
colors = ('default', 'primary', 'success', 'warning', 'danger', 'light')
variants = ("solid", "outline")

pn.Row(
    *(pn.Column(*(pn.widgets.Toggle(label=color, color=color, variant=variant) for color in colors))
    for variant in variants)
)
```

### Icons

The `Toggle` name string may contain Unicode and Emoji characters, providing a convenient way to define common graphical buttons.

```python
backward = pn.widgets.Toggle(label='\u25c0', width=50)
forward = pn.widgets.Toggle(label='\u25b6', width=50)
search = pn.widgets.Button(label='🔍', width=100)
play = pn.widgets.Toggle(label="▶️ Play", width=100)
pause = pn.widgets.Toggle(label="Pause ⏸️", width=100)

pn.Row(backward, forward, search, play, pause)
```

However you can also provide an explicit `icon`, either as a named icon loaded from [tabler-icons.io](https://tabler-icons.io)/:

```python
pn.widgets.Toggle(icon='2fa', color='light', icon_size='2em')
```

or as an explicit SVG:

```python
shuffle_icon = """
<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-arrows-shuffle" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M18 4l3 3l-3 3" />
  <path d="M18 20l3 -3l-3 -3" />
  <path d="M3 7h3a5 5 0 0 1 5 5a5 5 0 0 0 5 5h5" />
  <path d="M21 7h-5a4.978 4.978 0 0 0 -3 1m-4 8a4.984 4.984 0 0 1 -3 1h-3" />
</svg>
"""

pn.widgets.Toggle(icon=shuffle_icon, color='success', label='Shuffle', icon_size='2em')
```

### Controls

The `Toggle` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(toggle.controls(jslink=True), toggle)
```

---
