"""In this module we provide a component to test template/ layout changes on all relevent layouts,
panes and widgets"""
import panel as pn
import param

import pandas as pd


class ComponentViewer(param.Parameterized):
    """a component to test template/ layout changes on all relevent layouts,
panes and widgets"""

    def __init__(self, **params):
        super().__init__(**params)

    def button_view(self):
        button_default = pn.widgets.Button(name="DEFAULT")
        button_primary = pn.widgets.Button(name="PRIMARY", button_type="primary")
        button_success = pn.widgets.Button(name="SUCCESS", button_type="success")
        button_warning = pn.widgets.Button(name="WARNING", button_type="warning")
        button_danger = pn.widgets.Button(name="DANGER", button_type="danger")
        button_default_disabled = pn.widgets.Button(name="DEFAULT", disabled=True)
        button_primary_disabled = pn.widgets.Button(name="PRIMARY", button_type="primary", disabled=True)
        button_success_disabled = pn.widgets.Button(name="SUCCESS", button_type="success", disabled=True)
        button_warning_disabled = pn.widgets.Button(name="WARNING", button_type="warning", disabled=True)
        button_danger_disabled = pn.widgets.Button(name="DANGER", button_type="danger", disabled=True)


        buttons = pn.Row(
                button_default,
                button_primary,
                button_success,
                button_warning,
                button_danger,
            )
        buttons_disabled = pn.Row(
                button_default_disabled,
                button_primary_disabled,
                button_success_disabled,
                button_warning_disabled,
                button_danger_disabled,
            )
        return pn.Column(
            "### Button",
            buttons, buttons_disabled
        )

    def select_view(self):
        select_widget = pn.widgets.Select(
            name="Select", options=["Biology", "Chemistry", "Physics"]
        )
        select_widget_disabled = pn.widgets.Select(
            name="Select", options=["Biology", "Chemistry", "Physics"], disabled=True
        )
        return pn.Column(
            "### Select",
            pn.Row(
                select_widget, select_widget_disabled
            )
        )

    def dataframe_view(self):
        dataframe_pane = pn.pane.DataFrame(pd.DataFrame({"x": [1] * 4, "y": ["y"] * 4}))
        dataframe_widget = pn.widgets.DataFrame(pd.DataFrame({"x": [1] * 4, "y": ["y"] * 4}))
        return pn.Column(
            "### DataFrame",
            "#### Pane",
            dataframe_pane,
            "#### Widget",
            dataframe_widget,
        )

    def view(self):
        """Returns the component view"""



        return pn.Column(
            """### Text

[Panel](https://panel.holoviz.org/) is an open-source Python library that lets you create custom
interactive web apps and dashboards by connecting user-defined widgets to plots, images, tables, or
text.

Compared to other approaches, Panel is novel in that it

- supports nearly all plotting libraries,
- works just as well in a Jupyter notebook as on a standalone secure web server
- uses the same code for both those cases
- supports both Python-backed and static HTML/JavaScript exported applications,
- and can be used to develop rich interactive applications without tying your domain-specific code
to any particular GUI or web tools.

You can **use the Theme Builder to design your Panel app**.

You can also write `code` here

```python
print("Hello Panel World")
```
            """,
            self.button_view(),
            self.select_view(),
            self.dataframe_view(),
            min_height=800,
        )
