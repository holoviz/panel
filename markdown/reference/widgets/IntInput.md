# IntInput
---
```python
import panel as pn

pn.extension()
```

The ``IntInput`` widget allows selecting an integer value using a spinbox. It behaves like a slider except that lower and upper bounds are optional and a specific value can be entered. Value can be changed using keyboard (up, down, page up, page down), mouse wheel and arrow buttons.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (int): The current value. Updates when ever the value changes.
* **``value_throttled``** (int): The current value. Updates only on `<enter>` or when the widget looses focus.
* **``step``** (int): The step added or subtracted to the current value on each click
* **``start``** (int): Optional minimum allowable value
* **``end``** (int): Optional maximum allowable value
* **``format``** (str): Optional format to convert the float value in string, see : http://numbrojs.com/old-format.html
* **``page_step_multiplier``** (int): Defines the multiplication factor applied to step when the page up and page down keys are pressed.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
int_input = pn.widgets.IntInput(label='IntInput', value=5, step=2, start=0, end=1000)

int_input
```

``IntInput.value`` returns an integer value:

```python
int_input.value
```

### Controls

The `IntInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(int_input.controls(jslink=True), int_input)
```

---
