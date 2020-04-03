"""In this module we define the ColorScheme"""
import param
import panel as pn

EDITABLE_COLORS = [
    "primary",
    "secondary",
    # "success",
    # "info",
    "warning",
    # "danger",
    # "white",
    "light",
    "dark",
    # "black",
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
    warning = param.Color(default="#ffc107")

    white = param.Color(default="#ffffff", constant=True)
    black = param.Color(default="#000000", constant=True)

    light = param.Color(default="#f8f9fa")
    dark = param.Color(default="#212529")
    text_primary = param.String("rgba(255,255,255, 1.0)")
    secondary_text = param.String("rgba(255,255,255, 0.7)")
    disabled_text = param.String("rgba(255,255,255, 0.5)")
    dividers = param.String("rgba(255,255,255, 0.12)")
    focused = param.String("rgba(255,255,255, 0.12)")

    gray_50 = param.Color(default="#fafafa", readonly=True)
    gray_100 = param.Color(default="#f5f5f5", readonly=True)
    gray_200 = param.Color(default="#eeeeee", readonly=True)
    gray_300 = param.Color(default="#e0e0e0", readonly=True)
    gray_400 = param.Color(default="#bdbdbd", readonly=True)
    gray_500 = param.Color(default="#9e9e9e", readonly=True)
    gray_600 = param.Color(default="#757575", readonly=True)
    gray_700 = param.Color(default="#616161", readonly=True)
    gray_800 = param.Color(default="#424242", readonly=True)
    gray_900 = param.Color(default="#212121", readonly=True)

    def view(self):
        return pn.Column(
            "## Color Scheme",
            pn.Tabs(
                pn.Param(self, parameters=EDITABLE_COLORS, name="Editable", show_name=False),
                pn.Param(self, parameters=READ_ONLY_COLORS, name="Gray Palette", show_name=False),
            ),
        )

    def update(self, color_scheme):
        self.primary = color_scheme.primary
        self.secondary = color_scheme.secondary
        # self.success = color_scheme.success
        # self.info = color_scheme.info
        self.warning = color_scheme.warning
        # self.danger = color_scheme.danger
        self.light = color_scheme.light
        self.dark = color_scheme.dark


PANEL_COLOR_SCHEME = ColorScheme(name="Panel", light="#000000", dark="#ffffff")
CHESTERISH_COLOR_SCHEME = ColorScheme(
    name="chesterish",
    primary="#B5C2D9",
    secondary="#8ecdc8",
    warning="#B00020",
    # danger="#B00020",
    light="#ececec",
    dark="#323a48",  # "#27313d",
)
# See https://material.io/design/color/#tools-for-picking-colors
# See https://github.com/angular/components/blob/master/src/material/core/theming/_palette.scss
ANGULAR_DARK_COLOR_SCHEME = ColorScheme(
    name="Angular Dark",
    primary="#9c27b0",
    secondary="#69f0ae",
    warning="#f44336",
    light="#ececec",
    dark="#303030",
)

COLOR_SCHEMES = [
    PANEL_COLOR_SCHEME,
    CHESTERISH_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
]

COLOR_SCHEME_EDITABLE_COLORS = ["color_scheme." + item for item in EDITABLE_COLORS]