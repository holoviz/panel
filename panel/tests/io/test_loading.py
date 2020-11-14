from panel.layout.base import WidgetBox
import random
import time

import holoviews as hv
import param

import panel as pn
from panel.io.loading import (
    _LOADING_INDICATOR_CSS_CLASS,
    _add_css_class,
    _remove_css_class,
    start_loading_indicator,
    stop_loading_indicator,
)
from panel.tests.io import loading_indicators

DEFAULT_LOADING_INDICATOR = (
    "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/e6cb56375bb1c436975e09739a231fb31e628a63/spinners/default.svg"
)
DARK_LOADING_INDICATOR = (
    "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/e6cb56375bb1c436975e09739a231fb31e628a63/spinners/dark.svg"
)

SPINNERS = {
    "Default": DEFAULT_LOADING_INDICATOR,
    "Dark": DARK_LOADING_INDICATOR,
    "Bar Chart": loading_indicators.bar_chart_url,
    "Bars": loading_indicators.bars_url,
    "Dual Ring": loading_indicators.dual_ring_url,
    "Message": loading_indicators.message_url,
    "Pulse": loading_indicators.pulse_url,
    "Rolling": loading_indicators.rolling_url,
    "Spin": loading_indicators.spin_url,
    "Spinner": loading_indicators.spinner_url,
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


def test_start__and_stop_loading_indicator():
    panel1 = pn.Column()
    panel2 = pn.Column(css_classes=["other"])

    start_loading_indicator(panel1, panel2)
    assert _LOADING_INDICATOR_CSS_CLASS in panel1.css_classes
    assert _LOADING_INDICATOR_CSS_CLASS in panel2.css_classes

    stop_loading_indicator(panel1, panel2)
    assert panel1.css_classes is None
    assert _LOADING_INDICATOR_CSS_CLASS not in panel2.css_classes


def test_app():
    class LoadingIndicatorStyler(param.Parameterized):
        spinner = param.ObjectSelector(default=DEFAULT_LOADING_INDICATOR, objects=SPINNERS)
        spinner_height = param.Integer(50, bounds=(1, 100))
        background_alpha = param.Number(0.5, bounds=(0.0,1.0), step=0.01, doc="The background alpha")
        color = param.Color(loading_indicators.DEFAULT_COLOR)
        style = param.String("")

        settings_panel = param.Parameter()
        style_panel = param.Parameter()

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
                    "style": {"type": pn.widgets.TextAreaInput, "sizing_mode": "stretch_both", "disabled": True}
                },
            )

            self.style_panel = pn.pane.HTML(sizing_mode="fixed", width=0, height=0, margin=0)
            self._toggle_color()

        @property
        def spinner_url(self):
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
    background-image: url('{self.spinner_url}');
    background-size: auto {self.spinner_height}%;
    background-color: rgb(255,255,255,{self.background_alpha});
}}"""

        @param.depends("style", watch=True)
        def _update_loading_indicator_css(self):
            self.style_panel.object = f"""<style>{self.style}</style>"""

    class LoadingIndicatorApp(param.Parameterized):
        start_loading = param.Action(doc="Start the loading indicator")
        stop_loading = param.Action(doc="Stop the loading indicator")
        sleep = param.Number(1, bounds=(0.1, 10), label="Time to update plot", doc="The time it takes to update the plot")
        load_main = param.Boolean(default=False, label="Show common loading indicator?")

        loading = param.Boolean(default=False)
        update_data = param.Action(doc="Update the plot")

        panels = param.List()

        view = param.Parameter()
        styler = param.ClassSelector(class_=LoadingIndicatorStyler)

        def __init__(self, **params):
            super().__init__(**params)

            self.start_loading = self._start_loading
            self.stop_loading = self._stop_loading

            self.update_data = self._update_data

            hv_plot = self._get_plot()
            self.hv_plot_panel = pn.pane.HoloViews(hv_plot, height=500)
            self.styler = LoadingIndicatorStyler(name="Styles")

            self.panels = [
                pn.Param(
                    self.param.update_data,
                    widgets={"update_data": {"button_type": "success"}},
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
                        "load_main",
                    ],
                    widgets={
                        "style": {"type": pn.widgets.TextAreaInput, "sizing_mode": "stretch_both", "disabled": True}
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

        def _update_data(self, *_):
            self.loading = True
            time.sleep(self.sleep)
            self.hv_plot_panel.object = self._get_plot()
            self.loading = False

        @param.depends("loading", "load_main", watch=True)
        def _update_loading_indicator(self):
            if self.loading:
                self._start_loading_indicator()
            else:
                self._stop_loading_indicator()

        def _start_loading_indicator(self, *_):
            # Only nescessary in this demo app to be able to toggle load_main
            self._stop_loading_indicator()
            if self.load_main:
                start_loading_indicator(self.main)
            else:
                start_loading_indicator(*self.panels)

        def _stop_loading_indicator(self, *_):
            # self.main.css_classes=[]
            # for panel in self.panels:
            #     panel.css_classes=[]
            stop_loading_indicator(self.main, *self.panels)



    return LoadingIndicatorApp(name="Loading Indicator App")


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    test_app().view.servable()
