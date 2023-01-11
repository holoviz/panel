# Widgets

```{pyodide}
import panel as pn
pn.extension()
```

``Panel`` provides a wide range of widgets to provide precise control over parameter values. The widget classes use a consistent API that allows treating broad categories of widgets as interchangeable. For instance, to select a value from a list of options, you can interchangeably use a ``Select`` widget, a ``RadioButtonGroup``, or a range of other equivalent widgets.

Like all other components in ``Panel``, ``Widget`` objects will render and sync their state both in the notebook and on Bokeh server:


```{pyodide}
widget = pn.widgets.TextInput(name='A widget', value='A string')
widget
```

Changing the text value will automatically update the corresponding parameter, if you have a live running Python process:


```{pyodide}
widget.value
```

Updating the parameter value will also update the widget:


```{pyodide}
widget.value = 'ABCDEFG'
```

## Callbacks and links

To listen to a parameter change we can call ``widget.param.watch`` with the parameter to watch and a function:


```{pyodide}
widget.param.watch(print, 'value')
```

If we change the ``widget.value`` now, the resulting change event will be printed:


```{pyodide}
widget.value = 'A'
```

In combination with ``Panel`` objects, widgets make it possible to build interactive dashboards and visualizations very easily. For more detail on defining callbacks and links between widgets and other components see the [Links user guide](Links.md).

## Laying out widgets

To compose multiple widgets they can be added to a ``Row``, ``Column`` or ``Tabs`` Panel. To learn more about laying out widgets and panels, see the [customization user guide](Customization.md).


```{pyodide}
slider = pn.widgets.FloatSlider(name='Another widget', width=200)
pn.Column(widget, slider, width=200)
```

## Types of Widgets

The supported widgets can be grouped into a number of distinct categories with compatible APIs.

### Options selectors

Option selector widgets allow selecting one or more values from a list or dictionary. All widgets of this type have ``options`` and ``value`` parameters.

#### Single values

These widgets allow selecting one value from a list or dictionary of options:

* **[``AutocompleteInput``](../reference/widgets/AutocompleteInput.ipynb)**: Select a ``value`` by entering it into an auto-completing text field.
* **[``DiscretePlayer``](../reference/widgets/DiscretePlayer.ipynb)**: Displays media-player-like controls which allow playing and stepping through the provided options.
* **[``DiscreteSlider``](../reference/widgets/DiscreteSlider.ipynb)**: Select a value using a slider.
* **[``RadioButtonGroup``](../reference/widgets/RadioButtonGroup.ipynb)**: Select a value from a set of mutually exclusive toggle buttons.
* **[``RadioBoxGroup``](../reference/widgets/RadioBoxGroup.ipynb)**: Select a value from a set of mutually exclusive checkboxes.
* **[``Select``](../reference/widgets/Select.ipynb)**: Select a value using a dropdown menu.

#### Multiple values

These widgets allow selecting _multiple_ values from a list or dictionary of options:

* **[``CheckBoxGroup``](../reference/widgets/CheckBoxGroup.ipynb)**: Select values by ticking the corresponding checkboxes.
* **[``CheckButtonGroup``](../reference/widgets/CheckButtonGroup.ipynb)**: Select values by toggling the corresponding buttons.
* **[``CrossSelector``](../reference/widgets/CrossSelector.ipynb)**: Select values by moving items between two lists.
* **[``MultiSelect``](../reference/widgets/MultiSelect.ipynb)**: Select values by highlighting in a list.

### Type-based selectors

Type-based selectors provide means to select a value according to its type, and all have a ``value``. The widgets in this category may also have other forms of validation beyond the type, e.g. the upper and lower bounds of sliders.

#### Single value

Allow selecting a single ``value`` of the appropriate type:

##### Numeric

Numeric selectors are bounded by a ``start`` and ``end`` value:

* **[``IntSlider``](../reference/widgets/IntSlider.ipynb)**: Select an integer value within a set bounds using a slider.
* **[``FloatSlider``](../reference/widgets/FloatSlider.ipynb)**: Select a float value within a set bounds using a slider.
* **[``Player``](../reference/widgets/Player.ipynb)**: Displays media-player-like controls, which allow playing and stepping over a range of integer values.

##### Boolean

* **[``Checkbox``](../reference/widgets/Checkbox.ipynb)**: Toggle a single condition between ``True``/``False`` states by ticking a checkbox.
* **[``Toggle``](../reference/widgets/Toggle.ipynb)**: Toggle a single condition between ``True``/``False`` states by clicking a button.

##### Dates

* **[``DatetimeInput``](../reference/widgets/DatetimeInput.ipynb)**: Enter a datetime value as text, parsing it using a pre-defined formatter.
* **[``DatePicker``](../reference/widgets/DatePicker.ipynb)**: Select a date value using a text box and the browser's date-picking utility.
* **[``DateSlider``](../reference/widgets/DateSlider.ipynb)**: Select a date value within a set bounds using a slider.

##### Text

* **[``PasswordInput``](../reference/widgets/PasswordInput.ipynb)**: Enter any string using a password input box.
* **[``TextInput``](../reference/widgets/TextInput.ipynb)**: Enter any string using a text input box.
* **[``TextAreaInput``](../reference/widgets/TextAreaInput.ipynb)**: Enter any string using a multi-line text input box.

##### Other

* **[``ColorPicker``](../reference/widgets/ColorPicker.ipynb)**: Select a color using the browser's color-picking utilities.
* **[``FileInput``](../reference/widgets/FileInput.ipynb)**: Upload a file from the frontend, making the file data and MIME type available in Python.
* **[``LiteralInput``](../reference/widgets/LiteralInput.ipynb)**: Enter any Python literal using a text entry box, which is then parsed in Python.

#### Ranges

Allow selecting a range of values of the appropriate type stored as a ``(lower, upper)`` tuple on the ``value`` parameter.

##### Numeric

* **[``IntRangeSlider``](../reference/widgets/IntRangeSlider.ipynb)**: Select an integer range using a slider with two handles.
* **[``RangeSlider``](../reference/widgets/RangeSlider.ipynb)**: Select a floating-point range using a slider with two handles.

##### Dates

* **[``DateRangeSlider``](../reference/widgets/DateRangeSlider.ipynb)**: Select a date range using a slider with two handles.

### Other

* **[``Button``](../reference/widgets/Button.ipynb)**: Allows triggering events when the button is clicked.  Unlike other widgets, it does not have a ``value`` parameter.
* **[``DataFrame``](../reference/widgets/DataFrame.ipynb)**: A widget that allows displaying and editing a Pandas DataFrame.
* **[``FileDownload``](../reference/widgets/FileDownload.ipynb)**: A button that allows downloading a file on the frontend by sending the file data to the browser.
