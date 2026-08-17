# DiscreteSlider
---
```python
import panel as pn
pn.extension()
```

The ``DiscreteSlider`` widget allows selecting from a discrete list or dictionary of values using a slider. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the ```AutocompleteInput```, and ```Select``` widgets.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): A list or dictionary of options to select from
* **``value``** (object): The current value; must be one of the option values
* **``value_throttled ``** (object): The current value; must be one of the option values, throttled until mouseup

##### Display

* **``bar_color``** (color): Color of the slider bar as a hexadecimal RGB value
* **``direction``** (str): Whether the slider should go from left to right ('ltr') or right to left ('rtl')
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str): Whether the slider should be displayed in a 'horizontal' or 'vertical' orientation.
* **``tooltips``** (boolean): Whether to display tooltips on the slider handle

___

```python
discrete_slider = pn.widgets.DiscreteSlider(label='Discrete Slider', options=[2, 4, 8, 16, 32, 64, 128], value=32)

discrete_slider
```

Like most other widgets, ``DiscreteSlider`` has a value parameter that can be accessed or set:

```python
discrete_slider.value
```

---
