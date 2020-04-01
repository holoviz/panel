"""The ColorPalette is inspired by the [Material Design Color Palette]\
    (https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=9C27B0)

It provides

- functionality to create and edit a Color Palette similar to the Material Design Color Palette
- functionality to calculate a palette (close to) the Material Design Color Palette based on the
selection of one color
"""
import panel as pn
import param
from .color_utils import compute_colors, is_dark

WHITE_BLACK_PARAMETERS = ["white", "black"]
COLOR_PARAMETERS = [
    "color_50",
    "color_100",
    "color_200",
    "color_300",
    "color_400",
    "color_500",
    "color_600",
    "color_700",
    "color_800",
    "color_900",
    "color_A100",
    "color_A200",
    "color_A400",
    "color_A700",
]
CONTRAST_PARAMETERS = [
    "color_50",
    "color_100",
    "color_200",
    "color_300",
    "color_400",
    "color_500",
    "color_600",
    "color_700",
    "color_800",
    "color_900",
    "color_A100",
    "color_A200",
    "color_A400",
    "color_A700",
]
COLOR_AND_CONTRAST_PARAMETERS = COLOR_PARAMETERS + CONTRAST_PARAMETERS


class ColorPalette(param.Parameterized):
    white = param.Color(default="#ffffff", precedence=-0.1)
    black = param.Color(default="#000000", precedence=-0.1)

    color_50 = param.Color(default="#f3e5f6", precedence=0.0)
    color_100 = param.Color(default="#e1bee7", precedence=0.1)
    color_200 = param.Color(default="#ce93d8", precedence=0.2)
    color_300 = param.Color(default="#ba68c8", precedence=0.3)
    color_400 = param.Color(default="#ab47bc", precedence=0.4)
    color_500 = param.Color(default="#9c27b0", precedence=0.5)
    color_600 = param.Color(default="#9423a9", precedence=0.6)
    color_700 = param.Color(default="#8a1da0", precedence=0.7)
    color_800 = param.Color(default="#801797", precedence=0.8)
    color_900 = param.Color(default="#6e0e87", precedence=0.9)
    color_A100 = param.Color(default="#efb8ff", precedence=1.1)
    color_A200 = param.Color(default="#e485ff", precedence=1.2)
    color_A400 = param.Color(default="#d852ff", precedence=1.4)
    color_A700 = param.Color(default="#d238ff", precedence=1.7)

    contrast_50 = param.Color(default="#000000", precedence=0.0)
    contrast_100 = param.Color(default="#000000", precedence=0.1)
    contrast_200 = param.Color(default="#000000", precedence=0.2)
    contrast_300 = param.Color(default="#000000", precedence=0.3)
    contrast_400 = param.Color(default="#ffffff", precedence=0.4)
    contrast_500 = param.Color(default="#ffffff", precedence=0.5)
    contrast_600 = param.Color(default="#ffffff", precedence=0.6)
    contrast_700 = param.Color(default="#ffffff", precedence=0.7)
    contrast_800 = param.Color(default="#ffffff", precedence=0.8)
    contrast_900 = param.Color(default="#ffffff", precedence=0.9)
    contrast_A100 = param.Color(default="#000000", precedence=1.1)
    contrast_A200 = param.Color(default="#000000", precedence=1.2)
    contrast_A400 = param.Color(default="#000000", precedence=1.4)
    contrast_A700 = param.Color(default="#ffffff", precedence=1.7)

    @param.depends("color_500", watch=True)
    def update(self):
        colors = compute_colors(self.color_500)

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

        self.contrast_50 = self.white if is_dark(self.color_50) else self.black
        self.contrast_100 = self.white if is_dark(self.color_100) else self.black
        self.contrast_200 = self.white if is_dark(self.color_200) else self.black
        self.contrast_300 = self.white if is_dark(self.color_300) else self.black
        self.contrast_400 = self.white if is_dark(self.color_400) else self.black
        self.contrast_500 = self.white if is_dark(self.color_500) else self.black
        self.contrast_600 = self.white if is_dark(self.color_600) else self.black
        self.contrast_700 = self.white if is_dark(self.color_700) else self.black
        self.contrast_800 = self.white if is_dark(self.color_800) else self.black
        self.contrast_900 = self.white if is_dark(self.color_900) else self.black
        self.contrast_A100 = self.white if is_dark(self.color_A100) else self.black
        self.contrast_A200 = self.white if is_dark(self.color_A200) else self.black
        self.contrast_A400 = self.white if is_dark(self.color_A400) else self.black
        self.contrast_A700 = self.white if is_dark(self.color_A700) else self.black

    def edit_view(self):
        return pn.Column(
            "## Color Palette Editor",
            pn.Param(
                self,
                show_name=False,
                parameters=COLOR_PARAMETERS,
            ),
        )

    def single_color_edit_view(self):
        return pn.Column(
            "## Color Palette Editor",
            self.param.color_500,
            self.readonly_view(),
        )

    def to_html_table(self):
        return f"""\
<table style="width:100%;text-align:center"><tbody>
<tr style="background-color:{self.color_50};color:{self.contrast_50}"><td>50: </td><td>{self.color_50}</td></tr>
<tr style="background-color:{self.color_100};color:{self.contrast_100}"><td>100: </td><td>{self.color_100}</td></tr>
<tr style="background-color:{self.color_200};color:{self.contrast_200}"><td>200: </td><td>{self.color_200}</td></tr>
<tr style="background-color:{self.color_300};color:{self.contrast_300}"><td>300: </td><td>{self.color_300}</td></tr>
<tr style="background-color:{self.color_400};color:{self.contrast_400}"><td>400: </td><td>{self.color_400}</td></tr>
<tr style="background-color:{self.color_500};color:{self.contrast_500}"><td>500: </td><td>{self.color_500}</td></tr>
<tr style="background-color:{self.color_600};color:{self.contrast_600}"><td>600: </td><td>{self.color_600}</td></tr>
<tr style="background-color:{self.color_700};color:{self.contrast_700}"><td>700: </td><td>{self.color_700}</td></tr>
<tr style="background-color:{self.color_800};color:{self.contrast_800}"><td>800: </td><td>{self.color_800}</td></tr>
<tr style="background-color:{self.color_900};color:{self.contrast_900}"><td>900: </td><td>{self.color_900}</td></tr>
<tr style="background-color:{self.color_A100};color:{self.contrast_A100}"><td>A100: </td><td>{self.color_A100}</td></tr>
<tr style="background-color:{self.color_A200};color:{self.contrast_A200}"><td>A200: </td><td>{self.color_A200}</td></tr>
<tr style="background-color:{self.color_A400};color:{self.contrast_A400}"><td>A400: </td><td>{self.color_A400}</td></tr>
<tr style="background-color:{self.color_A700};color:{self.contrast_A700}"><td>A700: </td><td>{self.color_A700}</td></tr>
</tbody></table>"""

    def readonly_view(self):
        return pn.Column(
            "## Color Palette",
            pn.pane.HTML(self.to_html_table())
        )
