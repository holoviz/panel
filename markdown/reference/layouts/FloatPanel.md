# FloatPanel
---
```python
import panel as pn
pn.extension('floatpanel')
```

The `FloatPanel` layout provides a draggable container which can be placed inside its parent or be completely free floating. It is built on-top of [jsPanel](https://jspanel.de/) and is highly customizable. It has a list-like API with methods to `append`, `extend`, `clear`, `insert`, `pop`, `remove` and `__setitem__`, which make it possible to interactively update and modify the layout. Components inside it are laid out like a `Column`.

#### Parameters:

* **`contained`** (boolean): Whether the component is contained within the parent container or completely free floating.
* **`config`** (dict): Additional [jsPanel configuration](https://jspanel.de/#options/overview) with precedence over parameter values.
* **`objects`** (list): The list of objects to display in the Column, should not generally be modified directly except when replaced in its entirety.
* **`position`**: The initial position if the container is free-floating.
* **`offsetx`** (int): Horizontal offset in pixels.
* **`offsety`** (int): Vertical offset in pixels.
* **`theme`** (str): The theme can be one of:
    - Built-ins: 'default', 'primary', 'secondary', 'info',
      'success', 'warning', 'danger', 'light', 'dark' and 'none'
    - HEX, RGB and HSL color values like '#123456' Any
      standardized color name like 'forestgreen' and color names
      from the Material Design Color System like 'purple900'
    - Additionally a theme string may include one of the modifiers
      'filled', 'filledlight', 'filleddark' or 'fillcolor'
      separated from the theme color by a space like 'primary
* **`status`** (str): Current status on the Panel, can be one of "normalized", "maximized", "minimized", "smallified", "smallifiedmax" or "closed" .

___

A `FloatPanel` layout can either be instantiated as empty and populated after the fact or using a list of objects provided as positional arguments. If the objects are not already panel components they will each be converted to one using the `pn.panel` conversion method.

When laying out the `FloatPanel` it can either be `contained` in another container:

```python
w1 = pn.widgets.TextInput(label='Text:')
w2 = pn.widgets.FloatSlider(label='Slider')

floatpanel = pn.layout.FloatPanel(w1, w2, name='Basic FloatPanel', margin=20)

pn.Column('**Example: Basic `FloatPanel`**', floatpanel, height=250)
```

Alternatively we can make the `FloatPanel` free floating:

```python
pn.layout.FloatPanel("Try dragging me around.", name="Free Floating FloatPanel", contained=False, position='center')
```

### Configuration

As mentioned the `FloatPanel` is highly customizable via the `config` parameter. As an example lets remove the *close* button.

```python
config = {"headerControls": {"close": "remove"}}

pn.Column(
    "Example: `FloatPanel` without *close button*",
    pn.layout.FloatPanel("You can't close me!", name='FloatPanel without close button', margin=20, config=config),
    height=200,
)
```

For more configuration options check out the excellent [jsPanel docs](https://jspanel.de/).

### Controls

The `FloatPanel` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
floatpanel = pn.layout.FloatPanel(w1, w2, name='FloatPanel with Controls', margin=20)

pn.Row(floatpanel.controls(jslink=True), floatpanel)
```

---
