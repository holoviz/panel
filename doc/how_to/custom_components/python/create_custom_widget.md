# Build a Widget in Python

In this guide we will demonstrate how to create a custom widget that enables users to select a list of features and set their values entirely in Python.

We will leverage the `PyComponent` class to construct this custom widget. The `PyComponent` allows us to combine multiple Panel components into a more complex and functional widget. The resulting class will combine a `MultiSelect` widget with a dynamic number of `FloatInput` widgets.

## Code Overview

Below is the complete implementation of the `FeatureInput` custom widget:

```{pyodide}
import panel as pn
import param

from panel.widgets.base import WidgetBase
from panel.custom import PyComponent

class FeatureInput(WidgetBase, PyComponent):
    """
    The `FeatureInput` enables a user to select from a list of features and set their values.
    """

    value = param.Dict(
        doc="The names of the features selected and their set values", allow_None=False
    )

    features = param.Dict(
        doc="The names of the available features and their default values"
    )

    selected_features = param.ListSelector(
        doc="The list of selected features"
    )

    _selected_widgets = param.ClassSelector(
        class_=pn.Column, doc="The widgets used to edit the selected features"
    )

    def __init__(self, **params):
        params["value"] = params.get("value", {})
        params["features"] = params.get("features", {})
        params["selected_features"] = params.get("selected_features", [])

        params["_selected_widgets"] = self.param._selected_widgets.class_()

        super().__init__(**params)

        self._selected_features_widget = pn.widgets.MultiChoice.from_param(
            self.param.selected_features, sizing_mode="stretch_width"
        )

    def __panel__(self):
        return pn.Column(self._selected_features_widget, self._selected_widgets)

    @param.depends("features", watch=True, on_init=True)
    def _reset_selected_features(self):
        selected_features = []
        for feature in self.selected_features.copy():
            if feature in self.features.copy():
                selected_features.append(feature)

        self.param.selected_features.objects = list(self.features)
        self.selected_features = selected_features

    @param.depends("selected_features", watch=True, on_init=True)
    def _handle_selected_features_change(self):
        org_value = self.value

        self._update_selected_widgets(org_value)
        self._update_value()

    def _update_value(self, *args):  # pylint: disable=unused-argument
        new_value = {}

        for widget in self._selected_widgets:
            new_value[widget.name] = widget.value

        self.value = new_value

    def _update_selected_widgets(self, org_value):
        new_widgets = {}

        for feature in self.selected_features:
            value = org_value.get(feature, self.features[feature])
            widget = self._new_widget(feature, value)
            new_widgets[feature] = widget

        self._selected_widgets[:] = list(new_widgets.values())

    def _new_widget(self, feature, value):
        widget = pn.widgets.FloatInput(
            name=feature, value=value, sizing_mode="stretch_width"
        )
        pn.bind(self._update_value, widget, watch=True)
        return widget
```

This is a lot to take in so let us break it down into a few pieces:

### Inheritance

The `FeatureInput` class inherits from `pn.custom.PyComponent` and `pn.widgets.WidgetBase`. This multiple inheritance structure allows us to create custom components that behave one of the three core component types that Panel defines `Widget`, `Pane` and `Panel` (i.e. a layout). You should always inherit from the component type base class first, i.e. `WidgetBase` in this case and the component implementation class second, i.e. `PyComponent` in this case.

### Parameter Definitions

It defines the following parameters:

- `value`: A dictionary that stores the selected features and their corresponding values.
- `features`: A dictionary of available features and their default values.
- `selected_features`: The list of features that have been selected.
- `_selected_widgets`: A "private" column layout that contains the widgets for editing the selected features.

### State handling

The two most important methods in configuring state are the constructor (`__init__`) and the (`__panel__`) method which will be invoked to create the component lazily at render time.

#### Constructor

In the `__init__` method, we initialize the widget parameters and create a `MultiChoice` widget for selecting features. We also set up a column to hold the selected feature widgets.

#### `__panel__`

`PyComponent` classes must define a `__panel__` method which tells Panel how the component should be rendered. Here we return a layout of the `MultiSelect` and a column containing the selected features.

#### Syncing state

We use `@param.depends` decorators to define methods that react to changes in the `features` and `selected_features` parameters:

- `_reset_selected_features`: Ensures that only available features are selected.
- `_handle_selected_features_change`: Updates the widgets and the `value` parameter when the selected features change.

#### Widget Updates

The `_update_value` method updates the `value` parameter based on the current values of the feature widgets. The `_update_selected_widgets` method creates and updates the widgets for the selected features.

## Creating the Application

Now, let's create an application to demonstrate our custom `FeatureInput` widget in action. We will define a set of features related to a wind turbine and use our widget to select and set their values:

```{pyodide}
features = {
    "Blade Length (m)": 73.5,
    "Cut-in Wind Speed (m/s)": 3.5,
    "Cut-out Wind Speed (m/s)": 25,
    "Grid Connection Capacity (MW)": 5,
    "Hub Height (m)": 100,
    "Rated Wind Speed (m/s)": 12,
    "Rotor Diameter (m)": 150,
    "Turbine Efficiency (%)": 45,
    "Water Depth (m)": 30,
    "Wind Speed (m/s)": 10,
}
selected_features = ["Wind Speed (m/s)", "Rotor Diameter (m)"]
widget = FeatureInput(
    features=features,
    selected_features=selected_features,
    width=500,
)

pn.FlexBox(
    pn.Column(
        "## Widget",
        widget,
    ),
    pn.Column(
        "## Value",
        pn.pane.JSON(widget.param.value, width=500, height=200),
    ),
)
```

## References

- [PyComponent](../../../reference/custom_components/PyComponent.md)
