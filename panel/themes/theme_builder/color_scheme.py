"""In this module we define the ColorScheme"""
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