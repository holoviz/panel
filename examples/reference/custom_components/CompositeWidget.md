# `CompositeWidget`

`CompositeWidget` simplifies the creation of custom Panel widgets using only Python and Panel components.

```{pyodide}
import param
import panel as pn
from panel.widgets import CompositeWidget

pn.extension()

class ButtonGroup(CompositeWidget):
    """A widget that allows selecting between multiple options by clicking a button.

    The value will trigger an event if a button is re-clicked.
    """
    value = param.Parameter(label="Value", doc="The selected value")
    options = param.Selector(allow_None=False, doc="The available options")

    def __init__(self, **params):
        params["margin"] = params.get("margin", (5, 0))
        super().__init__(**params)
        self._update_composite()

    @param.depends("options", watch=True)
    def _update_composite(self):
        buttons = []
        with pn.config.set(sizing_mode="stretch_width"):
            for option in self.options:
                button = pn.widgets.Button(
                    name=option,
                    on_click=pn.bind(self._update_value, value=option),
                    margin=(5, 5),
                )
                buttons.append(button)
        self._composite[:] = buttons

    def _update_value(self, event, value):
        if self.value != value:
            self.value = value
        else:
            self.param.trigger("value")


button_group = ButtonGroup(options=["Option 1", "Option 2", "Option 3"], width=300)
pn.Column(button_group, button_group.param.value).servable()
```

::: note

If you want to create new panes or layouts using Python, check out [`Viewer`](Viewer.md).

For creating new components using JavaScript, refer to [`JSComponent`](JSComponent.md), [`ReactComponent`](ReactComponent.md), or [`AnyWidgetComponent`](AnyWidgetComponent.md).

:::

## API

### Parameters

- **`value`**: The `value` parameter that every widget has.

### Attributes

- **`_composite`**: The layout to be displayed.

### Class Attributes

- **`_composite_type`**: The type of layout for the `_composite`. Default is pn.Row.

## Usage

Custom `CompositeWidgets` can be used just like built-in Panel widgets with `pn.Param`, `pn.bind`, `@pn.depends`, etc.

Let's demonstrate this by using the `button_group` with the `ChatInterface`.

```{pyodide}
def callback(contents, user, interface):
    return f"You sent {contents}"

pn.chat.ChatInterface(callback=callback, widgets=[button_group], objects=["Please click an option and send it"], width=700, height=500).servable()
```

Now, let's create another `CompositeComponent`. We will create a `CustomDateRangePicker` by combining the custom `ButtonGroup` and the built-in `DateRangePicker`:

```{pyodide}
from datetime import date, timedelta

_PERIODS = ["Day", "MTD", "YTD", "All"]

class CustomDateRangeSelector(CompositeWidget):
    value = param.DateRange(label="Period")

    _composite_type = pn.Column
    _periods = ["Day", "MTD", "YTD", "All"]

    def __init__(self, **params):
        super().__init__(**params)

        if not self.value:
            with param.discard_events(self):
                self._update_period("Day")

        with pn.config.set(sizing_mode="stretch_width"):
            period_buttons = ButtonGroup(value="Day", options=_PERIODS)
            pn.bind(self._update_period, period=period_buttons, watch=True)
            date_range_widget = pn.widgets.DateRangePicker.from_param(self.param.value)

        self._composite[:] = [period_buttons, date_range_widget]


    def _update_period(self, period):
        today = date.today()
        yesterday = today - timedelta(days=1)

        if period == "Day":
            self.value = (yesterday - timedelta(days=1), yesterday)
        elif period == "MTD":
            self.value = (yesterday.replace(day=1) - timedelta(days=1), yesterday)
        elif period == "YTD":
            self.value = (yesterday.replace(day=1, month=1) - timedelta(days=1), yesterday)
        elif period == "All":
            self.value = (date(2020, 1, 1), yesterday)

custom_date_range_selector = CustomDateRangeSelector(sizing_mode="fixed", width=500)
custom_date_range_selector.servable()
```

Notice the usage of the `period_buttons` with `pn.bind`. We provided `period_buttons` directly because it's a widget, not the more general `period_buttons.param.value`, which is necessary for a general `Parameterized` class.
