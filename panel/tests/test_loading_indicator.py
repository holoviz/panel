import random
import time

import holoviews as hv
import param

import panel as pn
from panel.loading_indicator import (
    _LOADING_INDICATOR_CSS_CLASS,
    _add_css_class,
    _remove_css_class,
    start_loading_indicator,
    stop_loading_indicator,
)

DEFAULT_LOADING_INDICATOR = (
    "https://raw.githubusercontent.com/holoviz/panel/master/panel/assets/spinner.gif"
)
SPINNERS = {
    "Default": DEFAULT_LOADING_INDICATOR,
    "Aqua": "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/assets/images/spinners/spinner_aqua.png",
    "Bricks": "https://www.inspiredled.com/wp-content/plugins/fyrelazyload/assets/img/loader.gif",
    "Circles": "https://siegroup1.github.io/SIEGroup-Report.io/pic/login-gif-11.gif",
    "Circles Simple": "https://ruciart.com/wp-content/themes/ruciart/assets/img/spinner.gif",
    "Facebook": "https://www.viptogo.com/wp-content/themes/viptogo-theme/img/loader.gif",
    "Panel Breath": "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/assets/images/spinners/spinner_panel_breath_light_400_340.gif",
    "Panel Rotating": "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/assets/images/spinners/spinner_panel_rotate_400_400.gif",
    "Super": "https://csf.com.au/tools/retirement-modeller/images/loading.gif",
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
    class App(param.Parameterized):
        start_loading = param.Action()
        stop_loading = param.Action()
        sleep = param.Number(1, bounds=(0.1, 10), label="Update Data Time")
        spinner = param.ObjectSelector(
            default=DEFAULT_LOADING_INDICATOR, objects=SPINNERS
        )
        spinner_height = param.Integer(40, bounds=(1, 150))
        load_main = param.Boolean(default=False, label="Mark all as loading")

        loading = param.Boolean(default=False)
        update_data = param.Action()

        panels = param.List()

        view = param.Parameter()

        def __init__(self, **params):
            super().__init__(**params)

            self.start_loading = self._start_loading
            self.stop_loading = self._stop_loading

            self.update_data = self._update_data

            hv_plot = self._get_plot()
            self.hv_plot_panel = pn.pane.HoloViews(hv_plot, height=500)

            self.panels = [
                pn.Param(
                    self.param.update_data,
                    widgets={"update_data": {"button_type": "success"}},
                ),
                self.hv_plot_panel,
            ]

            self.settings = pn.WidgetBox(
                pn.Param(
                    self,
                    parameters=[
                        "start_loading",
                        "stop_loading",
                        "sleep",
                        "spinner",
                        "spinner_height",
                        "load_main",
                    ],
                ),
                width=300,
                sizing_mode="stretch_height",
            )
            self.main = pn.Column(*self.panels)
            self.css_pane = pn.pane.HTML(
                sizing_mode="fixed", width=0, height=0, margin=0
            )
            self.view = pn.Row(self.settings, self.main, self.css_pane)

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

        @param.depends("spinner", "spinner_height", watch=True)
        def _update_loading_indicator_css(self):
            self.css_pane.object = f"""<style>
.bk.panel-loading:before {{
    background-image: url('{self.spinner}');
    background-size: {self.spinner_height}px auto;
}}
</style>"""

    return App()


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    test_app().view.servable()
