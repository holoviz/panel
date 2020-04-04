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

        self.button_default = pn.widgets.Button(name="DEFAULT")
        self.button_primary = pn.widgets.Button(name="PRIMARY", button_type="primary")
        self.button_success = pn.widgets.Button(name="SUCCESS", button_type="success")
        self.button_warning = pn.widgets.Button(name="WARNING", button_type="warning")
        self.button_danger = pn.widgets.Button(name="DANGER", button_type="danger")

        self.dataframe_pane = pn.pane.DataFrame(pd.DataFrame({"x": [1] * 4, "y": ["y"] * 4}))
        self.dataframe_widget = pn.widgets.DataFrame(pd.DataFrame({"x": [1] * 4, "y": ["y"] * 4}))

        self.select_widget = pn.widgets.Select(
            name="Select", options=["Biology", "Chemistry", "Physics"]
        )
        self.select_widget_disabled = pn.widgets.Select(
            name="Select", options=["Biology", "Chemistry", "Physics"], disabled=True
        )

    def view(self):
        """Returns the component view"""
        return pn.Column(
            """# Test App

This is text
            """,
            self.button_default,
            self.button_primary,
            self.button_success,
            self.button_warning,
            self.button_danger,
            self.select_widget,
            self.select_widget_disabled,
            self.dataframe_pane,
            self.dataframe_widget,
            min_height=800,
        )
