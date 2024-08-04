# Build a Custom FeatureInput Widget

Welcome to the "Build a Custom FeatureInput Widget" tutorial! In this guide, we will walk through the process of creating a custom widget that enables users to select a list of features and set their values. This can be particularly useful, for instance, in forecasting the power production of a wind turbine using advanced machine learning models.

We will leverage the `CompositeWidget` from HoloViz Panel to construct this custom widget. The `CompositeWidget` allows us to combine multiple Panel components into a more complex and functional widget. In this tutorial, we will combine a `MultiSelect` widget with a dynamic number of `FloatInput` widgets to achieve our goal.

<iframe src="https://panel-org-build-feature-input-widget.hf.space" frameborder="0" style="width: 100%;height:500px"></iframe>

You can find the full code, including requirements and tests, [here](https://huggingface.co/spaces/Panel-Org/build_feature_input_widget/tree/main).

## Code Overview

Below is the complete implementation of the `FeatureInput` custom widget:

```python
import panel as pn
import param

class FeatureInput(pn.widgets.CompositeWidget):
    """The FeatureInput enables a user to select from a list of features and set their values.

    ## Example

    ```python
    features = {
        "A": 1.0,
        "B": 2.0,
        "C": 3.0,
        "D": 4.0,
    }
    selected_features = ["A", "C"]
    widget = FeatureInput(features=features, selected_features=selected_features)
    ```
    """

    value = param.Dict(
        doc="The names of the features selected and their set values", allow_None=False
    )

    features = param.Dict(
        doc="The names of the available features and their default values",
        allow_None=False,
    )
    selected_features = param.ListSelector(
        doc="The list of selected features", allow_None=False
    )

    _selected_widgets = param.ClassSelector(
        class_=pn.Column, doc="The widgets used to edit the selected features"
    )

    _composite_type = pn.Column

    def __init__(self, **params):
        params["value"] = params.get("value", {})
        params["features"] = params.get("features", {})
        params["selected_features"] = params.get("selected_features", [])

        params["_selected_widgets"] = self.param._selected_widgets.class_()

        super().__init__(**params)

        selected_features_widget = pn.widgets.MultiChoice.from_param(
            self.param.selected_features, sizing_mode="stretch_width"
        )

        self._composite[:] = [selected_features_widget, self._selected_widgets]

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

A key design decision in this implementation is to use the parameter state to manage the widget's internal state and update the layout. The alternative would be to keep the state in the `MultiChoice` and `FloatInput` widgets. This makes the flow easier to reason about.

## Creating the Application

Now, let's create an application to demonstrate our custom `FeatureInput` widget in action. We will define a set of features related to a wind turbine and use our widget to select and set their values.

```python
def create_app():
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

    return pn.FlexBox(
        pn.Column(
            "## Widget",
            widget,
        ),
        pn.Column(
            "## Value",
            pn.pane.JSON(widget.param.value, width=500, height=200),
        ),
    )

if pn.state.served:
    pn.extension(design="material")

    create_app().servable()
```

You can serve the application with `panel serve name_of_file.py`.

## Explanation

### Widget Definition

The `FeatureInput` class inherits from `pn.widgets.CompositeWidget`. It defines the following parameters:

- `value`: A dictionary that stores the selected features and their corresponding values.
- `features`: A dictionary of available features and their default values.
- `selected_features`: The list of features that have been selected.
- `_selected_widgets`: A "private" column layout that contains the widgets for editing the selected features.

### Initialization

In the `__init__` method, we initialize the widget parameters and create a `MultiChoice` widget for selecting features. We also set up a column to hold the selected feature widgets. Finally we define the `_composite` attribute to hold the sub components of the widget.

### Parameter Dependencies

We use `@param.depends` decorators to define methods that react to changes in the `features` and `selected_features` parameters:

- `_reset_selected_features`: Ensures that only available features are selected.
- `_handle_selected_features_change`: Updates the widgets and the `value` parameter when the selected features change.

### Widget Updates

The `_update_value` method updates the `value` parameter based on the current values of the feature widgets. The `_update_selected_widgets` method creates and updates the widgets for the selected features.

### Example Application

The `create_app` function demonstrates how to use the `FeatureInput` widget with a predefined set of features. It returns a layout with the widget and a JSON pane to display the current values.

## Conclusion

In this tutorial, we have learned how to create a custom `FeatureInput` widget using HoloViz Panel's `CompositeWidget`. This custom widget allows users to select features and set their values interactively. Such a widget can be highly useful in various applications, such as configuring parameters for machine learning models or setting up simulations.

Feel free to explore and extend this example to suit your specific needs. Happy coding!

## References

- [CompositeWidget](../../reference/custom_components/CompositeWidget.html)
