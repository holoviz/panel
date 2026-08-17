# FloatInput
---
```python
import panel as pn

pn.extension()
```

The ``FloatInput`` widget allows selecting a floating point value using a spinbox. It behaves like a slider except that lower and upper bounds are optional and a specific value can be entered. Value can be changed using keyboard (up, down, page up, page down), mouse wheel and arrow buttons.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (float | None): The current value. Updates on `<enter>`, when the widget looses focus, or arrow icons or keyboard up arrow, down arrow, PgUp, or PgDown keys pressed. Can return None if all digits are deleted.
* **``value_throttled``** (float | None): Behaves identically to ``value`` for this widget, except is read only.
* **``step``** (float): The step added or subtracted to the current value on each click
* **``start``** (float): Optional minimum allowable value
* **``end``** (float): Optional maximum allowable value
* **``format``** (str): Optional format to convert the float value in string, see : http://numbrojs.com/old-format.html
* **``page_step_multiplier``** (int): Defines the multiplication factor applied to step when the page up and page down keys are pressed.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
float_input = pn.widgets.FloatInput(label='FloatInput', value=5., step=1e-1, start=0, end=1000)

float_input
```

``FloatInput.value`` returns a float value:

```python
float_input.value
```

### Controls

The `FloatSpinner` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(float_input.controls(jslink=True), float_input)
```

---
