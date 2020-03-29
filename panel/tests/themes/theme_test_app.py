import panel as pn
import param

import pandas as pd

class ThemeTestApp(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)

        self.button_default = pn.widgets.Button(name="Click me")
        self.button_primary = pn.widgets.Button(name="Click me", button_type="primary")
        self.button_success = pn.widgets.Button(name="Click me", button_type="success")
        self.button_warning = pn.widgets.Button(name="Click me", button_type="warning")
        self.button_danger = pn.widgets.Button(name="Click me", button_type="danger")

        self.dataframe_pane = pn.pane.DataFrame(pd.DataFrame({"x": [1]*4, "y": ['y']*4}))
        self.dataframe_widget = pn.widgets.DataFrame(pd.DataFrame({"x": [1]*4, "y": ['y']*4}))

    def view(self):
        return pn.Column(
            """# Test App

This is text
            """,
            self.button_default,
            self.button_primary,
            self.button_success,
            self.button_warning,
            self.button_danger,
            self.dataframe_pane,
            self.dataframe_widget,
            min_height=800,
        )