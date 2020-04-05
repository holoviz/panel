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
        return pn.Row(
            pn.Param(
                self,
                parameters=["primary", "secondary", "warning", "theme"],
                expand_button=False,
                sizing_mode="stretch_width",
            ),
        )

    def update(self, color_scheme):
        self.primary = color_scheme.primary
        self.secondary = color_scheme.secondary
        self.warning = color_scheme.warning
        self.theme = color_scheme.theme

    def get_colors_accent(self):
        primary = self.primary
        return [
            primary.color_50,
            primary.color_100,
            primary.color_200,
            primary.color_300,
            primary.color_400,
            primary.color_500,
            primary.color_600,
            primary.color_700,
            primary.color_800,
            primary.color_900,
            primary.color_a100,
            primary.color_a200,
            primary.color_a400,
            primary.color_a700,
        ]

    def get_colors_category(self):
        colors = [
            self.primary.color_500,
            self.secondary.color_500,
            self.warning.color_500,
        ]
        for palette in color_palette.PALETTES:
            color = palette.color_500
            if color not in colors:
                colors.append(color)

        colors.append(self.primary.color_a100)
        colors.append(self.secondary.color_a100)
        colors.append(self.warning.color_a100)

        for palette in color_palette.PALETTES:
            color = palette.color_a100
            if color not in colors:
                colors.append(color)

        return colors


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
    theme=theme.DARK_THEME,
)
ANGULAR_DARK_COLOR_SCHEME = ColorScheme(
    name="Purple-Green",
    primary=color_palette.PURPLE,
    secondary=color_palette.GREEN,
    warning=color_palette.RED,
    theme=theme.DARK_THEME,
)

COLOR_SCHEMES = [
    PANEL_COLOR_SCHEME,
    CHESTERISH_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
]