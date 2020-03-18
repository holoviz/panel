"""This Module Provides functionality to configure a Theme"""

# @Philippfr:
# If possible I would like to let the user change theme or individual colors while the app is running
# If possible I would like the user to specify the palette.
import pathlib
import param
import panel as pn
import glob
import importlib
# @Philippfr: Should we always import. Or should we done something else to minimize Panel start up
# time?
import holoviews as hv

ROOT_PATH = pathlib.Path(__file__).parent
THEMES = ["default", "bootstrap", "angular_dark"]
THEME = "default"

class Theme(param.Parameterized):
    # @Philippfr: I would have like to call theme name but it raises
    # ValueError: Theme not in Parameter None's list of possible objects,
    # valid options include [default, angular_material_purple_green, bootstrap_dashboard]
    theme = param.ObjectSelector(default="default", objects=THEMES)
    path = param.ClassSelector(class_=pathlib.Path)
    colors = param.Parameter()
    holoviews_theme = param.Dict()
    configure = param.Action()


    def __init__(self, **params):
        super().__init__(**params)

        self.configure = self._configure

        if self.theme:
            self._set_path()

    @param.depends("theme")
    def _set_path(self):
        self.path = ROOT_PATH / self.theme

    @param.depends("path")
    def _set_colors(self):
        try:
            color_module = importlib.import_module("panel.themes." + self.theme + ".color")
            self.colors = color_module.color
        except:
            self.colors = None

    @param.depends("path")
    def _set_holoviews_theme(self):
        try:
            holoviews_module = importlib.import_module("panel.themes." + self.theme + ".holoviews")
            self.holoviews_theme = holoviews_module.theme
        except:
            self.holoviews_theme = None


    def _configure(self):
        self._append_css_files()

        if self.holoviews_theme:
            hv.renderer("bokeh").theme = self.holoviews_theme

    def _append_css_files(self):
        glob_str = str(self.path / "*.css")
        print(glob_str)
        for css_file in glob.glob(glob_str):
            print(css_file)
            pn.config.css_files.append(css_file)