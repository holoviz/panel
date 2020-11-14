"""Test of the loading functionality"""
import random
import time

import holoviews as hv
import panel as pn
import param
from panel.io.loading import (_LOADING_INDICATOR_CSS_CLASS, DARK_URL,
                              DEFAULT_URL, STYLE, _add_css_class, _remove_css_class,
                              start_loading_spinner, stop_loading_spinner)
from panel.tests.io import loading_spinners
import pytest
pn.config.raw_css.append(STYLE)
SPINNERS = {
    "Default": DEFAULT_URL,
    "Dark": DARK_URL,
    "Bar Chart": loading_spinners.bar_chart_url,
    "Bars": loading_spinners.bars_url,
    "Dual Ring": loading_spinners.dual_ring_url,
    "Message": loading_spinners.message_url,
    "Pulse": loading_spinners.pulse_url,
    "Rolling": loading_spinners.rolling_url,
    "Spin": loading_spinners.spin_url,
    "Spinner": loading_spinners.spinner_url,
}


def test_add_css_class():
    # Given
    css_class = "test-class"
    panel = pn.Column()

    # When/ Then
    _add_css_class(panel, css_class=css_class)
    assert panel.css_classes == [css_class]
    _add_css_class(panel, css_class=css_class)
    assert panel.css_classes == [css_class]

    # When/ Then
    panel2 = pn.Column()
    panel3 = pn.Column()
    _add_css_class(panel, panel2, panel3, css_class=css_class)
    assert panel.css_classes == [css_class]
    assert panel.css_classes == [css_class]
    assert panel2.css_classes == [css_class]


def test_remove_css_class():
    # Given
    css_class = "test-class"

    # When/ Then
    panel = pn.Column()
    _remove_css_class(panel, css_class=css_class)
    assert panel.css_classes is None

    # When/ Then
    panel.css_classes = [css_class]
    _remove_css_class(panel, css_class=css_class)
    assert panel.css_classes is None  # [] won't work in the browser!

    # When/ Then
    panel.css_classes = [css_class, "other"]
    _remove_css_class(panel, css_class=css_class)
    assert panel.css_classes == ["other"]

    # When/ Then
    panel.css_classes = [css_class]
    panel2 = pn.Column(css_classes=["test-class"])
    _remove_css_class(panel, panel2, css_class=css_class)
    assert panel.css_classes is None  # [] won't work in the browser!
    assert panel2.css_classes is None  # [] won't work in the browser!


def test_start__and_stop_loading_spinner():
    panel1 = pn.Column()
    panel2 = pn.Column(css_classes=["other"])

    start_loading_spinner(panel1, panel2)
    assert _LOADING_INDICATOR_CSS_CLASS in panel1.css_classes
    assert _LOADING_INDICATOR_CSS_CLASS in panel2.css_classes

    stop_loading_spinner(panel1, panel2)
    assert panel1.css_classes is None
    assert _LOADING_INDICATOR_CSS_CLASS not in panel2.css_classes

def test_app():
    class LoadingStyler(param.Parameterized):
        """A utility that can be used to select and style the loading spinner"""

        spinner = param.ObjectSelector(
            default=DEFAULT_URL, objects=SPINNERS, doc="The loading spinner to use"
        )
        spinner_height = param.Integer(50, bounds=(1, 100))
        background_alpha = param.Number(
            0.5, bounds=(0.0, 1.0), step=0.01, doc="The background alpha"
        )
        color = param.Color(loading_spinners.DEFAULT_COLOR)
        style = param.String("", doc="The CSS Style applied to the loading spinner")

        settings_panel = param.Parameter(doc="A panel containing the settings of the LoadingStyler")
        style_panel = param.Parameter(doc="An 'invisible' HTML pane containing the css style")

        def __init__(self, **params):
            super().__init__(**params)

            self.settings_panel = pn.Param(
                self,
                parameters=[
                    "spinner",
                    "spinner_height",
                    "background_alpha",
                    "color",
                    "style",
                ],
                widgets={
                    "style": {
                        "type": pn.widgets.TextAreaInput,
                        "sizing_mode": "stretch_both",
                        "disabled": True,
                    }
                },
            )

            self.style_panel = pn.pane.HTML(sizing_mode="fixed", width=0, height=0, margin=0)
            self._toggle_color()

        @property
        def _spinner_url(self):
            spinner = self.spinner
            if callable(spinner):
                return spinner(self.color)
            return spinner

        @param.depends("spinner", watch=True)
        def _toggle_color(self):
            color_picker: pn.widgets.ColorPicker = [
                widget
                for widget in self.settings_panel
                if isinstance(widget, pn.widgets.ColorPicker)
            ][0]
            color_picker.disabled = not callable(self.spinner)

        @param.depends("spinner", "spinner_height", "color", "background_alpha", watch=True)
        def _update_style(self):
            self.style = f"""
.bk.pn-loading:before {{
    background-image: url('{self._spinner_url}');
    background-size: auto {self.spinner_height}%;
    background-color: rgb(255,255,255,{self.background_alpha});
}}"""

        @param.depends("style", watch=True)
        def _update_loading_spinner_css(self):
            self.style_panel.object = f"""<style>{self.style}</style>"""

    class LoadingApp(param.Parameterized):
        """An app which show cases the loading spinner and enables the user to style it."""

        start_loading = param.Action(label="START LOADING", doc="Start the loading spinner")
        stop_loading = param.Action(label="STOP LOADING", doc="Stop the loading spinner")
        sleep = param.Number(
            1,
            bounds=(0.1, 10),
            label="Update time in seconds",
            doc="The time it takes to update the plot",
        )
        show_shared_spinner = param.Boolean(default=False, label="Show one shared loading spinner?")

        loading = param.Boolean(
            default=False, doc="""Whether or not to show the loading indicator"""
        )
        update_plot = param.Action(label="UPDATE PLOT", doc="Update the plot")

        panels = param.List()

        view = param.Parameter()
        styler = param.ClassSelector(class_=LoadingStyler)

        def __init__(self, **params):
            super().__init__(**params)

            self.start_loading = self._start_loading
            self.stop_loading = self._stop_loading

            self.update_plot = self._update_plot

            hv_plot = self._get_plot()
            self.hv_plot_panel = pn.pane.HoloViews(hv_plot, height=500)
            self.styler = LoadingStyler(name="Styles")

            self.panels = [
                pn.Param(
                    self.param.update_plot,
                    widgets={"update_plot": {"button_type": "success"}},
                ),
                self.hv_plot_panel,
            ]

            self.settings_panel = pn.WidgetBox(
                pn.Param(
                    self,
                    parameters=[
                        "start_loading",
                        "stop_loading",
                        "sleep",
                        "show_shared_spinner",
                    ],
                    widgets={
                        "style": {
                            "type": pn.widgets.TextAreaInput,
                            "sizing_mode": "stretch_both",
                            "disabled": True,
                        }
                    },
                ),
                self.styler.settings_panel,
                width=300,
                sizing_mode="stretch_height",
            )
            self.main = pn.Column(*self.panels)
            self.view = pn.Row(self.settings_panel, self.main, self.styler.style_panel)

        def _start_loading(self, *_):
            self.loading = True

        def _stop_loading(self, *_):
            self.loading = False

        @staticmethod
        def _get_plot():
            xxs = ["one", "two", "tree", "four", "five", "six"]
            data = []
            for item in xxs:
                data.append((item, random.randint(0, 10)))
            return hv.Bars(data, hv.Dimension("Car occupants"), "Count")

        def _update_plot(self, *_):
            self.loading = True
            time.sleep(self.sleep)
            self.hv_plot_panel.object = self._get_plot()
            self.loading = False

        @param.depends("loading", "show_shared_spinner", watch=True)
        def _update_loading_spinner(self):
            if self.loading:
                self._start_loading_spinner()
            else:
                self._stop_loading_spinner()

        def _start_loading_spinner(self, *_):
            # Only nescessary in this demo app to be able to toggle show_shared_spinner
            self._stop_loading_spinner()
            if self.show_shared_spinner:
                self.main.loading=True
            else:
                for panel in self.panels:
                    panel.loading=True

        def _stop_loading_spinner(self, *_):
            self.main.loading=False
            for panel in self.panels:
                panel.loading=False

    return LoadingApp(name="Loading Indicator App")


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    test_app().view.servable()
