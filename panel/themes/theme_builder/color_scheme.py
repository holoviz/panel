"""In this module we define the ColorScheme"""
import param
import panel as pn
from . import theme
from . import color_palette

COLOR_SCHEME_EDITABLE_COLORS = [
    "color_scheme.primary",
    "color_scheme.secondary",
    "color_scheme.warning",
    "color_scheme.theme",
]

# See https://material.io/design/color/#tools-for-picking-colors
# See https://github.com/angular/components/blob/master/src/material/core/theming/_palette.scss
class ColorScheme(param.Parameterized):
    primary = param.ObjectSelector(color_palette.PURPLE, objects=color_palette.PALETTES)
    secondary = param.ObjectSelector(color_palette.GREEN, objects=color_palette.PALETTES)
    warning = param.ObjectSelector(color_palette.RED, objects=color_palette.PALETTES)
    theme = param.ObjectSelector(default=theme.LIGHT_THEME, objects=theme.THEMES)

    def view(self):
        return pn.Param(self, name="Selections")
        # return pn.Column(
        #     "## Color Scheme",
        #     pn.Tabs(
        #         pn.Param(self, name="Selections", show_name=False),
        #         self.primary.readonly_view,
        #         self.secondary.readonly_view,
        #         self.warning.readonly_view,
        #     ),
        # )

    def update(self, color_scheme):
        self.primary = color_scheme.primary
        self.secondary = color_scheme.secondary
        self.warning = color_scheme.warning


PANEL_COLOR_SCHEME = ColorScheme(
    name="Panel",
    primary=color_palette.BLUE,
    secondary=color_palette.GREEN,
    warning=color_palette.RED,
    )
CHESTERISH_COLOR_SCHEME = ColorScheme(
    name="Chesterish",
    primary=color_palette.BLUE_GREY,
    secondary=color_palette.CYAN,
    warning=color_palette.RED,
)
ANGULAR_DARK_COLOR_SCHEME = ColorScheme(
    name="Purple-Green",
    primary=color_palette.PURPLE,
    secondary=color_palette.GREEN,
    warning=color_palette.RED,
)

COLOR_SCHEMES = [
    PANEL_COLOR_SCHEME,
    CHESTERISH_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
]