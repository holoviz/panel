"""In this module we provide a component to test template/ layout changes on all relevent layouts,
panes and widgets"""
import panel as pn
import param
import hvplot.pandas
import holoviews as hv
import pandas as pd
import numpy as np
from .holoviews_theme import get_dark_theme


class ComponentViewer(param.Parameterized):
    """a component to test template/ layout changes on all relevent layouts,
panes and widgets"""
    plot_hv = param.Parameter()

    def __init__(self, **params):
        if not "plot_hv" in params:
            params["plot_hv"] = hv.Div("Loading ...")

        super().__init__(**params)

        self.sine_df = self._get_sine_df()
        self.plot_hv_pane = pn.pane.HoloViews(self.plot_hv)
        self.update_plots()

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

    def _get_sine_df(self):
        data = {
            "phase": [],
            "frequency": [],
            "x": [],
            "y": [],
        }

        for phase in [0, np.pi/2]:
            for frequency in [0.5, 0.75, 1.0]:
                for x in range(100):
                    data["phase"].append(phase)
                    data["frequency"].append(frequency)
                    data["x"].append(x)
                    data["y"].append(np.sin(phase+frequency*x))

        return pd.DataFrame(data)


    def update_plots(self):
        from bokeh.themes.theme import Theme
        from panel.themes.theme_builder.holoviews_theme import get_dark_theme
        from panel.themes.theme_builder.theme import DARK_THEME
        from panel.themes.theme_builder.color_scheme import ANGULAR_DARK_COLOR_SCHEME
        hv.renderer('bokeh').theme = Theme(json=get_dark_theme(DARK_THEME))
        cycle = hv.Cycle(ANGULAR_DARK_COLOR_SCHEME.get_colors_category())
        options = {'Curve': dict(color=cycle, line_width=4)}
        self.plot_hv = self.sine_df.hvplot(x="x", y="y", by=["phase", "frequency"], height=400).options(options)
        print(self.plot_hv)
        self.plot_hv_pane.object = self.plot_hv

    def plot_view(self):
        return pn.Column(
            "### Plots",
            "#### Holoviews", self.plot_hv_pane,
        )

    def view(self):
        """Returns the component view"""



        return pn.Column(
            """### Markdown

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

You can **use the Theme Builder to design your Panel app**. The Theme builder is inspired by

- [material.io](https://material.io/design/)
- [material-ui.com](https://material-ui.com/)

You can also write `code` here

```python
print("Hello Panel World")
```
            """,
            self.button_view(),
            self.select_view(),
            self.dataframe_view(),
            self.plot_view(),
            min_height=800,
        )
