# Number
---
```python
import panel as pn

pn.extension()
```

The ``Number`` is a value indicator providing a visual representation of a value, which may be colored according to provided thresholds.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``colors``** (list): Color thresholds for the Number indicator, specified as a tuple of the absolute thresholds and the color to switch to.
* **``default_color``** (str, default='black'): The color of the Number indicator if no `colors` are provided
* **``format``** (str, default='{value}'): A formatter string which accepts a {value}.
* **``font_size``** (str, default='54pt'): The size of number itself.
* **``nan_format``** str(str, default='-'): How to format nan values.
* **``title_size``** (str, default='18pt'): The size of number title.
* **``value``** (int or float): The value of the number indicator.

___

The `Number` indicator can be used to indicate a simple number and formatted as needed:

```python
pn.indicators.Number(label='Failure Rate', value=10, format='{value}%')
```

If we want to specify specific thresholds at which the indicator changes color:

```python
number = pn.indicators.Number(
    label='Failure Rate', value=72, format='{value}%',
    colors=[(33, 'green'), (66, 'gold'), (100, 'red')]
)

pn.Row(number.clone(value=10), number.clone(value=42), number.clone(value=93))
```

---
