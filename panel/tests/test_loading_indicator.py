import time
import panel as pn
import param
import holoviews as hv
import random

DEFAULT_SPINNER = "https://raw.githubusercontent.com/holoviz/panel/master/panel/assets/spinner.gif"
SPINNERS = [
    DEFAULT_SPINNER,
    "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/assets/images/spinners/spinner_aqua.png",
]

STYLE = """
.bk.pnx-loading:before {
position: absolute;
height: 100%;
width: 100%;
content: '';
z-index: 1000;
background-color: rgb(255,255,255,0.75);
border-color: lightgray;
background-image: url('https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/assets/images/spinners/spinner_aqua.png');
background-repeat: no-repeat;
background-position: center;
background-size: 10% auto;
border-width: 1px;

}
.bk.pnx-loading:hover:before {
    cursor: progress;
}
"""


def test_app():
    pn.config.raw_css.append(STYLE)

    class App(param.Parameterized):
        start_loading = param.Action()
        stop_loading = param.Action()
        sleep = param.Number(1, bounds=(0.1,10), label="Update Data Time")
        spinner = param.ObjectSelector(default=DEFAULT_SPINNER, objects=SPINNERS)
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

            hv_plot = self.get_plot()
            self.hv_plot_panel = pn.pane.HoloViews(hv_plot)

            self.panels = [
                pn.Param(self.param.update_data),
                self.hv_plot_panel,
            ]

            self.settings=pn.WidgetBox(self.param.start_loading, self.param.stop_loading, self.param.sleep, self.param.spinner, self.param.load_main)
            self.main = pn.Column(*self.panels)
            self.css_pane = pn.pane.HTML()
            self.view = pn.Column(self.settings, self.main, self.css_pane)

        def _start_loading(self, *_):
            self.loading=True
        def _stop_loading(self, *_):
            self.loading=False

        @staticmethod
        def get_plot():
            xxs = ['one', 'two', 'tree', 'four', 'five', 'six']
            data = []
            for item in xxs:
                data.append((item, random.randint(0,10)))
            return hv.Bars(data, hv.Dimension('Car occupants'), 'Count')

        def _update_data(self, *_):
            self.loading=True
            time.sleep(self.sleep)
            self.hv_plot_panel.object=self.get_plot()
            self.loading=False

        @param.depends("loading", "load_main", watch=True)
        def toggle_loading(self):
            if self.loading:
                self.start_loading_indicator()
            else:
                self.stop_loading_indicator()

        def start_loading_indicator(self, *_):
            self.stop_loading_indicator()
            if self.load_main:
                self.main.css_classes=["pnx-loading"]
            else:
                for panel in self.panels:
                    panel.css_classes=["pnx-loading"]

        def stop_loading_indicator(self, *_):
            self.main.css_classes=[]
            for panel in self.panels:
                panel.css_classes=[]

        @param.depends("spinner", watch=True)
        def _update_spinner(self):
            self.css_pane.object=f"""<style>
.bk.pnx-loading:before {{
    background-image: url('{self.spinner}');
}}
</style>"""
            print("spinner changed")

    return App()

if __name__.startswith("bokeh"):
    test_app().view.servable()

