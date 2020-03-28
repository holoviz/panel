import param
import panel as pn

EDITABLE_COLORS = [
    "primary",
    "secondary",
    "success",
    "info",
    "warning",
    "danger",
    "color",
    "background",
]

class BootStrapColors(param.Parameterized):
    primary = param.Color(default="#0d6efd")
    secondary = param.Color(default="#6c757d")
    success = param.Color(default="#28a745")
    info = param.Color(default="#17a2b8")
    warning = param.Color(default="#ffc107")
    danger = param.Color(default="#dc3545")
    color = param.Color(default="#f8f9fa") # light
    background = param.Color(default="#212529") # dark

THEMES = {
    "default": BootStrapColors(
        color = "#000000",
        background = "#ffffff"
    ),
    "chesterish": BootStrapColors(
        color = "#323a48",
        background = "#323a48",
    ),
    "angular_dark": BootStrapColors(
        primary = "#644c76",
        color = "#ececec",
        background = "#3b4956",
    )
}

class BoostrapThemeGenerator(BootStrapColors):
    theme = param.ObjectSelector(default=list(THEMES.values())[0], objects=THEMES)

    white = param.Color(default="#ffffff", readonly=True)
    black = param.Color(default="#000000", readonly=True)

    gray_100 = param.Color(default="#f8f9fa", readonly=True)
    gray_200 = param.Color(default="#e9ecef", readonly=True)
    gray_300 = param.Color(default="#dee2e6", readonly=True)
    gray_400 = param.Color(default="#ced4da", readonly=True)
    gray_500 = param.Color(default="#adb5bd", readonly=True)
    gray_600 = param.Color(default="#6c757d", readonly=True)
    gray_700 = param.Color(default="#495057", readonly=True)
    gray_800 = param.Color(default="#343a40", readonly=True)
    gray_900 = param.Color(default="#212529", readonly=True)

    panel_css = param.String()
    dataframe_css = param.String()

    def __init__(self, **params):
        super().__init__(**params)

        self._panel_css_pane = pn.pane.HTML()
        self._dataframe_css_pane = pn.pane.HTML()

        self._update_from_theme()
        self._set_panel_css()
        self._set_dataframe_css()

    @param.depends("theme", watch=True)
    def _update_from_theme(self):
        self.primary = self.theme.primary
        self.secondary = self.theme.secondary
        self.success = self.theme.success
        self.info = self.theme.info
        self.warning = self.theme.warning
        self.danger = self.theme.danger
        self.color = self.theme.color
        self.background = self.theme.background

    @param.depends(*EDITABLE_COLORS, watch=True)
    def _set_panel_css(self):
        self.panel_css = self._get_panel_css()

    @param.depends("panel_css", watch=True)
    def _set_panel_css_pane(self):
        self._panel_css_pane.object = "<style>" + self.panel_css + "</style>"

    @param.depends(*EDITABLE_COLORS, watch=True)
    def _set_dataframe_css(self):
        self.dataframe_css = self._get_dataframe_css()

    @param.depends("dataframe_css", watch=True)
    def _set_dataframe_css_pane(self):
        self._dataframe_css_pane.object = "<style>" + self.dataframe_css + "</style>"

    def view(self):
        return pn.Column(
            self.param.theme,
            self._panel_css_pane,
            self._dataframe_css_pane,
            pn.Param(self, parameters=EDITABLE_COLORS, default_layout=pn.Row),
        )

    def _get_panel_css(self):
        return f"""\
body {{
    background-color: {self.background};
    color: {self.color};
}}

h1, h2, h3, h4, h5 {{
color: {self.primary} !important;
}}"""

    def _get_dataframe_css(self):
        return f"""\
table.panel-df {{
    color: rgb(236,236,236);
}}
.panel-df tbody tr:nth-child(odd) {{
    background: #3f495a;
}}
.panel-df tbody tr {{
    background: #394251;
   }}
.panel-df thead {{
    background: #27313d;
    color: #bbc2e1;
    border-bottom: 1px solid #27313d;
    /* vertical-align: bottom; */
}}
.panel-df tr:hover:nth-child(odd) {{
    background: #3d4757 !important;
    /* cursor: pointer; */
}}
.panel-df tr:hover {{
    background: #373f4e !important;
    /* cursor: pointer; */
}}
.panel-df thead tr:hover:nth-child(1) {{
    background-color: inherit !important;
}}

.panel-df thead:hover {{
    background: #27313d !important;
}}"""