import param
import panel as pn

EDITABLE_COLORS = [
    "primary",
    "secondary",
    "success",
    "info",
    "warning",
    "danger",
    "white",
    "light",
    "dark",
    "black",
]
READ_ONLY_COLORS = [
    "gray_100",
    "gray_200",
    "gray_300",
    "gray_400",
    "gray_500",
    "gray_600",
    "gray_700",
    "gray_800",
    "gray_900",
]

class ColorPalette(param.Parameterized):
    color_50 = param.Color(default="#f3e5f6", constant=True, precedence=0.0)
    color_100 = param.Color(default="#e1bee7", constant=True, precedence=0.1)
    color_200 = param.Color(default="#ce93d8", constant=True, precedence=0.2)
    color_300 = param.Color(default="#ba68c8", constant=True, precedence=0.3)
    color_400 = param.Color(default="#ab47bc", constant=True, precedence=0.4)
    color_500 = param.Color(default="#9c27b0", precedence=0.5)
    color_600 = param.Color(default="#9423a9", constant=True, precedence=0.6)
    color_700 = param.Color(default="#8a1da0", constant=True, precedence=0.7)
    color_800 = param.Color(default="#801797", constant=True, precedence=0.8)
    color_900 = param.Color(default="#6e0e87", constant=True, precedence=0.9)
    color_A100 = param.Color(default="#efb8ff", constant=True, precedence=1.1)
    color_A200 = param.Color(default="#e485ff", constant=True, precedence=1.2)
    color_A400 = param.Color(default="#d852ff", constant=True, precedence=1.4)
    color_A700 = param.Color(default="#d238ff", constant=True, precedence=1.7)

    contrast_50 = param.Color(default="#000000", constant=True, precedence=0.0)
    contrast_100 = param.Color(default="#000000", constant=True, precedence=0.1)
    contrast_200 = param.Color(default="#000000", constant=True, precedence=0.2)
    contrast_300 = param.Color(default="#000000", constant=True, precedence=0.3)
    contrast_400 = param.Color(default="#ffffff", constant=True, precedence=0.4)
    contrast_500 = param.Color(default="#ffffff", constant=True, precedence=0.5)
    contrast_600 = param.Color(default="#ffffff", constant=True, precedence=0.6)
    contrast_700 = param.Color(default="#ffffff", constant=True, precedence=0.7)
    contrast_800 = param.Color(default="#ffffff", constant=True, precedence=0.8)
    contrast_900 = param.Color(default="#ffffff", constant=True, precedence=0.9)
    contrast_A100 = param.Color(default="#000000", constant=True, precedence=1.1)
    contrast_A200 = param.Color(default="#000000", constant=True, precedence=1.2)
    contrast_A400 = param.Color(default="#000000", constant=True, precedence=1.4)
    contrast_A700 = param.Color(default="#ffffff", constant=True, precedence=1.7)

    @param.depends("color_500", watch=True)
    def _update(self):
        from . import utils
        colors = utils.compute_colors(self.color_500)
        with param.edit_constant(self):
            self.color_50 = colors["50"]
            self.color_100 = colors["100"]
            self.color_200 = colors["200"]
            self.color_300 = colors["300"]
            self.color_400 = colors["400"]
            # self.color_500 = colors["500"]
            self.color_600 = colors["600"]
            self.color_700 = colors["700"]
            self.color_800 = colors["800"]
            self.color_900 = colors["900"]
            self.color_A100 = colors["A100"]
            self.color_A200 = colors["A200"]
            self.color_A400 = colors["A400"]
            self.color_A700 = colors["A700"]

            self.contrast_50 = "#ffffff" if utils.is_dark(self.color_50) else "#000000"
            self.contrast_100 = "#ffffff" if utils.is_dark(self.color_100) else "#000000"
            self.contrast_200 = "#ffffff" if utils.is_dark(self.color_200) else "#000000"
            self.contrast_300 = "#ffffff" if utils.is_dark(self.color_300) else "#000000"
            self.contrast_400 = "#ffffff" if utils.is_dark(self.color_400) else "#000000"
            self.contrast_500 = "#ffffff" if utils.is_dark(self.color_500) else "#000000"
            self.contrast_600 = "#ffffff" if utils.is_dark(self.color_600) else "#000000"
            self.contrast_700 = "#ffffff" if utils.is_dark(self.color_700) else "#000000"
            self.contrast_800 = "#ffffff" if utils.is_dark(self.color_800) else "#000000"
            self.contrast_900 = "#ffffff" if utils.is_dark(self.color_900) else "#000000"
            self.contrast_A100 = "#ffffff" if utils.is_dark(self.color_A100) else "#000000"
            self.contrast_A200 = "#ffffff" if utils.is_dark(self.color_A200) else "#000000"
            self.contrast_A400 = "#ffffff" if utils.is_dark(self.color_A400) else "#000000"
            self.contrast_A700 = "#ffffff" if utils.is_dark(self.color_A700) else "#000000"

    def view(self):
        class TwoColumnLayout(pn.layout.GridBox):
            def __init__(self, *objects, **params):
                params["ncols"]=2
                super().__init__(*objects, **params)
        return pn.Column(
            "## Color Palette",
            pn.Param(self, default_layout=TwoColumnLayout, show_name=False),
        )

class ColorScheme(param.Parameterized):
    primary = param.Color(default="#0d6efd")
    secondary = param.Color(default="#6c757d")
    success = param.Color(default="#28a745")
    info = param.Color(default="#17a2b8")
    warning = param.Color(default="#ffc107")
    danger = param.Color(default="#dc3545")
    white = param.Color(default="#ffffff")
    light = param.Color(default="#f8f9fa")
    dark = param.Color(default="#212529")
    black = param.Color(default="#000000")

    gray_100 = param.Color(default="#f8f9fa", readonly=True)
    gray_200 = param.Color(default="#e9ecef", readonly=True)
    gray_300 = param.Color(default="#dee2e6", readonly=True)
    gray_400 = param.Color(default="#ced4da", readonly=True)
    gray_500 = param.Color(default="#adb5bd", readonly=True)
    gray_600 = param.Color(default="#6c757d", readonly=True)
    gray_700 = param.Color(default="#495057", readonly=True)
    gray_800 = param.Color(default="#343a40", readonly=True)
    gray_900 = param.Color(default="#212529", readonly=True)

    def view(self):
        return pn.Column(
            "## Color Scheme",
            pn.Tabs(
                pn.Param(self, parameters=EDITABLE_COLORS, name="Editable", show_name=False),
                pn.Param(self, parameters=READ_ONLY_COLORS, name="Read Only", show_name=False),
            ),
        )

    def update(self, color_scheme):
        self.primary = color_scheme.primary
        self.secondary = color_scheme.secondary
        self.success = color_scheme.success
        self.info = color_scheme.info
        self.warning = color_scheme.warning
        self.danger = color_scheme.danger
        self.light = color_scheme.light
        self.dark = color_scheme.dark


PANEL_COLOR_SCHEME = ColorScheme(name="Panel", light="#000000", dark="#ffffff")
CHESTERISH_COLOR_SCHEME = ColorScheme(
    name="chesterish",
    primary="#B5C2D9",
    secondary="#8ecdc8",
    warning="#B00020",
    danger="#B00020",
    light="#ececec",
    dark="#323a48",  # "#27313d",
)
# See https://material.io/design/color/#tools-for-picking-colors
# See https://github.com/angular/components/blob/master/src/material/core/theming/_palette.scss
ANGULAR_DARK_COLOR_SCHEME = ColorScheme(
    name="Angular Dark",
    primary="#9c27b0",
    secondary="#69f0ae",
    light="#ececec",
    dark="#303030",
)

COLOR_SCHEMES = [
    PANEL_COLOR_SCHEME,
    CHESTERISH_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
]

COLOR_SCHEME_EDITABLE_COLORS = ["color_scheme." + item for item in EDITABLE_COLORS]


class CssGenerator(param.Parameterized):
    color_scheme = param.ClassSelector(class_=ColorScheme, readonly=True)
    panel_css = param.String()
    dataframe_css = param.String()

    def __init__(self, **params):
        self.param.color_scheme.default = ColorScheme()

        super().__init__(**params)

        self._set_panel_css()
        self._set_dataframe_css()

    def _get_panel_css(self):
        return ""

    def _get_dataframe_css(self):
        return ""

    @param.depends("color_scheme", *COLOR_SCHEME_EDITABLE_COLORS, watch=True)
    def _set_panel_css(self):
        self.panel_css = self._get_panel_css()

    @param.depends("color_scheme", *COLOR_SCHEME_EDITABLE_COLORS, watch=True)
    def _set_dataframe_css(self):
        self.dataframe_css = self._get_dataframe_css()

    @param.depends("color_scheme")
    def _color_scheme_view(self):
        return self.color_scheme.view()

    def _css_view(self):
        return pn.Column(
            "## CSS",
            pn.Tabs(
                pn.Param(
                    self.param.panel_css,
                    name="Panel",
                    widgets={"panel_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
                pn.Param(
                    self.param.dataframe_css,
                    name="Dataframe",
                    widgets={"dataframe_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
            ),
        )

    @param.depends("color_scheme")
    def view(self):
        return pn.Column(self._color_scheme_view, pn.layout.HSpacer(width=10), self._css_view,)


class DarkCssGenerator(CssGenerator):
    def _get_panel_css(self):
        return f"""\
body {{
    background-color: {self.color_scheme.dark};
    color: {self.color_scheme.light};
}}

h1, h2, h3, h4, h5 {{
color: {self.color_scheme.primary} !important;
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
    background: {self.color_scheme.dark};
    color: {self.color_scheme.light};
    border-bottom: 1px solid {self.color_scheme.primary};
}}
.panel-df tr:hover:nth-child(odd) {{
    background: #3d4757 !important;
}}
.panel-df tr:hover {{
    background: #373f4e !important;
}}
.panel-df thead tr:hover:nth-child(1) {{
    background-color: inherit !important;
}}

.panel-df thead:hover {{
    background: #27313d !important;
}}"""


DEFAULT_CSS_GENERATOR = CssGenerator(name="Default")
DARK_CSS_GENERATOR = DarkCssGenerator(name="Dark")

CSS_GENERATORS = [DEFAULT_CSS_GENERATOR, DARK_CSS_GENERATOR]


class ThemeBuilder(param.Parameterized):
    css_generator = param.ObjectSelector(default=CSS_GENERATORS[1], objects=CSS_GENERATORS, precedence=0.1)
    color_scheme = param.ObjectSelector(default=COLOR_SCHEMES[0], objects=COLOR_SCHEMES, precedence=0.2)

    def __init__(self, **params):
        super().__init__(**params)

        # @Philippfr: They still take up some space,
        # i.e. the Theme Builder header is not shown on top
        # How do I solve that?
        self._panel_css_pane = pn.pane.HTML(height=0, width=0)
        self._dataframe_css_pane = pn.pane.HTML(height=0, width=0)

        self._set_panel_css_pane()
        self._set_dataframe_css_pane()

    @param.depends("color_scheme", watch=True)
    def _update_css_generator_color_scheme(self):
        self.css_generator.color_scheme.update(self.color_scheme)

    @param.depends("css_generator", "css_generator.panel_css", watch=True)
    def _set_panel_css_pane(self):
        # print("_set_panel_css_pane", self.css_generator.panel_css)
        self._panel_css_pane.object = "<style>" + self.css_generator.panel_css + "</style>"

    @param.depends("css_generator", "css_generator.dataframe_css", watch=True)
    def _set_dataframe_css_pane(self):
        # print("_set_dataframe_css_pane")
        self._dataframe_css_pane.object = "<style>" + self.css_generator.dataframe_css + "</style>"

    @param.depends("css_generator")
    def _css_generator_view(self):
        return self.css_generator.view()

    def view(self, **params):
        return pn.Column(
            self._panel_css_pane,
            self._dataframe_css_pane,
            "# Theme Builder",
            pn.Param(
                self,
                parameters=["css_generator", "color_scheme"],
                show_name=False,
                # @Philipfr: I don't want to show expand button
                # But it does not seem to work?
                expand=False,
            ),
            self._css_generator_view,
            **params,
        )
