"""An App Template based on Bootstrap with a header, sidebar and main section"""
import glob
import pathlib

import param

import panel as pn

HEADER_HEIGHT = 58
SIDEBAR_WIDTH = 200

ROOT_PATH = pathlib.Path(__file__).parent
TEMPLATE = "app.html"
TEMPLATE_PATH = ROOT_PATH / TEMPLATE

# @Philippfr. Should the app.css file go into the _styles folder?
APP_CSS_PATH = ROOT_PATH / "app.css"

SIDEBAR_TOP_SPACING = 15
MAIN_MARGIN = (
    25,
    50,
    25,
    50,
)


# @Philipfr. Would it make sense to be able to change the value of all the parameters dynamically?
# I.e. the user could instantiate his app and then play around with the settings to find the
# one that works for him?
class AppTemplate(pn.Template):
    title = param.String("App Title")
    url = param.String("https://panel.holoviz.org/index.html")
    template_name = param.Parameter(TEMPLATE)
    sidebar_width = SIDEBAR_WIDTH
    header_height = HEADER_HEIGHT
    sidebar_top_spacing = 15
    main_margin = MAIN_MARGIN

    def __init__(
        self, **params,
    ):
        pn.config.css_files.append(APP_CSS_PATH)

        # @Philipfr: Maybe even more of this should be put in the app template
        title = pn.Row(
            pn.pane.Markdown(f"[{self.title}]({self.url})", css_classes=["app-title"],),
            width=self.sidebar_width,
            sizing_mode="stretch_height",
        )
        header = pn.Row(
            title, pn.layout.HSpacer(), sizing_mode="stretch_width", height=self.header_height,
        )
        top_spacer = pn.layout.HSpacer(height=SIDEBAR_TOP_SPACING)

        self.header = header
        self.sidebar = pn.Column(top_spacer, height_policy="max", width=self.sidebar_width,)
        self.main = pn.Column(sizing_mode="stretch_width", margin=self.main_margin,)

        items = {
            "header": header,
            "sidebar": self.sidebar,
            "main": self.main,
        }

        root_path = pathlib.Path(__file__).parent

        if not "template" in params:
            params["template"] = (root_path / self.template_name).read_text()

        super().__init__(
            items=items, **params
        )

if __name__.startswith("bk"):
    AppTemplate().servable()