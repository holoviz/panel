"""The ColorPalette is inspired by the [Material Design Color Palette]\
    (https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=9C27B0)

It provides

- functionality to create and edit a Color Palette similar to the Material Design Color Palette
- functionality to calculate a palette (close to) the Material Design Color Palette based on the
selection of one color
"""
import param

import panel as pn

from .color_utils import compute_colors, is_dark
from . import color

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
    "color_a100",
    "color_a200",
    "color_a400",
    "color_a700",
]
CONTRAST_PARAMETERS = [
    "contrast_50",
    "contrast_100",
    "contrast_200",
    "contrast_300",
    "contrast_400",
    "contrast_500",
    "contrast_600",
    "contrast_700",
    "contrast_800",
    "contrast_900",
    "contrast_a100",
    "contrast_a200",
    "contrast_a400",
    "contrast_a700",
]
COLOR_AND_CONTRAST_PARAMETERS = COLOR_PARAMETERS + CONTRAST_PARAMETERS


class ColorPalette(param.Parameterized):
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
    color_a100 = param.Color(default="#efb8ff", precedence=1.1)
    color_a200 = param.Color(default="#e485ff", precedence=1.2)
    color_a400 = param.Color(default="#d852ff", precedence=1.4)
    color_a700 = param.Color(default="#d238ff", precedence=1.7)

    contrast_50 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.0
    )
    contrast_100 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.1
    )
    contrast_200 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.2
    )
    contrast_300 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.3
    )
    contrast_400 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.4
    )
    contrast_500 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.5
    )
    contrast_600 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.6
    )
    contrast_700 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.7
    )
    contrast_800 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.8
    )
    contrast_900 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=0.9
    )
    contrast_a100 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=1.1
    )
    contrast_a200 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=1.2
    )
    contrast_a400 = param.ObjectSelector(
        default=color.DARK_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=1.4
    )
    contrast_a700 = param.ObjectSelector(
        default=color.LIGHT_PRIMARY_TEXT, objects=color.PRIMARY_TEXTS, precedence=1.7
    )

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
        self.color_a100 = colors["A100"]
        self.color_a200 = colors["A200"]
        self.color_a400 = colors["A400"]
        self.color_a700 = colors["A700"]

        self.contrast_50 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_50) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_100 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_100) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_200 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_200) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_300 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_300) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_400 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_400) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_500 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_500) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_600 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_600) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_700 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_700) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_800 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_800) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_900 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_900) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_a100 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_a100) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_a200 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_a200) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_a400 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_a400) else color.DARK_PRIMARY_TEXT
        )
        self.contrast_a700 = (
            color.LIGHT_PRIMARY_TEXT if is_dark(self.color_a700) else color.DARK_PRIMARY_TEXT
        )

    def edit_view(self):
        return pn.Column(
            "## Color Palette Editor",
            pn.Param(self, show_name=False, parameters=COLOR_PARAMETERS,),
        )

    def single_color_edit_view(self):
        return pn.Column("## Color Palette Editor", self.param.color_500, self.readonly_view(),)

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
<tr style="background-color:{self.color_a100};color:{self.contrast_a100}"><td>A100: </td><td>{self.color_a100}</td></tr>
<tr style="background-color:{self.color_a200};color:{self.contrast_a200}"><td>A200: </td><td>{self.color_a200}</td></tr>
<tr style="background-color:{self.color_a400};color:{self.contrast_a400}"><td>A400: </td><td>{self.color_a400}</td></tr>
<tr style="background-color:{self.color_a700};color:{self.contrast_a700}"><td>A700: </td><td>{self.color_a700}</td></tr>
</tbody></table>"""

    def readonly_view(self):
        return pn.Column("## Color Palette", pn.pane.HTML(self.to_html_table()))


RED = ColorPalette(
    name="red",
    color_50="#ffebee",
    color_100="#ffcdd2",
    color_200="#ef9a9a",
    color_300="#e57373",
    color_400="#ef5350",
    color_500="#f44336",
    color_600="#e53935",
    color_700="#d32f2f",
    color_800="#c62828",
    color_900="#b71c1c",
    color_a100="#ff8a80",
    color_a200="#ff5252",
    color_a400="#ff1744",
    color_a700="#d50000",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


PINK = ColorPalette(
    name="pink",
    color_50="#fce4ec",
    color_100="#f8bbd0",
    color_200="#f48fb1",
    color_300="#f06292",
    color_400="#ec407a",
    color_500="#e91e63",
    color_600="#d81b60",
    color_700="#c2185b",
    color_800="#ad1457",
    color_900="#880e4f",
    color_a100="#ff80ab",
    color_a200="#ff4081",
    color_a400="#f50057",
    color_a700="#c51162",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


PURPLE = ColorPalette(
    name="purple",
    color_50="#f3e5f5",
    color_100="#e1bee7",
    color_200="#ce93d8",
    color_300="#ba68c8",
    color_400="#ab47bc",
    color_500="#9c27b0",
    color_600="#8e24aa",
    color_700="#7b1fa2",
    color_800="#6a1b9a",
    color_900="#4a148c",
    color_a100="#ea80fc",
    color_a200="#e040fb",
    color_a400="#d500f9",
    color_a700="#aa00ff",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.LIGHT_PRIMARY_TEXT,
    contrast_400=color.LIGHT_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


DEEP_PURPLE = ColorPalette(
    name="deep_purple",
    color_50="#ede7f6",
    color_100="#d1c4e9",
    color_200="#b39ddb",
    color_300="#9575cd",
    color_400="#7e57c2",
    color_500="#673ab7",
    color_600="#5e35b1",
    color_700="#512da8",
    color_800="#4527a0",
    color_900="#311b92",
    color_a100="#b388ff",
    color_a200="#7c4dff",
    color_a400="#651fff",
    color_a700="#6200ea",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.LIGHT_PRIMARY_TEXT,
    contrast_400=color.LIGHT_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


INDIGO = ColorPalette(
    name="indigo",
    color_50="#e8eaf6",
    color_100="#c5cae9",
    color_200="#9fa8da",
    color_300="#7986cb",
    color_400="#5c6bc0",
    color_500="#3f51b5",
    color_600="#3949ab",
    color_700="#303f9f",
    color_800="#283593",
    color_900="#1a237e",
    color_a100="#8c9eff",
    color_a200="#536dfe",
    color_a400="#3d5afe",
    color_a700="#304ffe",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.LIGHT_PRIMARY_TEXT,
    contrast_400=color.LIGHT_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


BLUE = ColorPalette(
    name="blue",
    color_50="#e3f2fd",
    color_100="#bbdefb",
    color_200="#90caf9",
    color_300="#64b5f6",
    color_400="#42a5f5",
    color_500="#2196f3",
    color_600="#1e88e5",
    color_700="#1976d2",
    color_800="#1565c0",
    color_900="#0d47a1",
    color_a100="#82b1ff",
    color_a200="#448aff",
    color_a400="#2979ff",
    color_a700="#2962ff",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.LIGHT_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


LIGHT_BLUE = ColorPalette(
    name="light_blue",
    color_50="#e1f5fe",
    color_100="#b3e5fc",
    color_200="#81d4fa",
    color_300="#4fc3f7",
    color_400="#29b6f6",
    color_500="#03a9f4",
    color_600="#039be5",
    color_700="#0288d1",
    color_800="#0277bd",
    color_900="#01579b",
    color_a100="#80d8ff",
    color_a200="#40c4ff",
    color_a400="#00b0ff",
    color_a700="#0091ea",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


CYAN = ColorPalette(
    name="cyan",
    color_50="#e0f7fa",
    color_100="#b2ebf2",
    color_200="#80deea",
    color_300="#4dd0e1",
    color_400="#26c6da",
    color_500="#00bcd4",
    color_600="#00acc1",
    color_700="#0097a7",
    color_800="#00838f",
    color_900="#006064",
    color_a100="#84ffff",
    color_a200="#18ffff",
    color_a400="#00e5ff",
    color_a700="#00b8d4",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


TEAL = ColorPalette(
    name="teal",
    color_50="#e0f2f1",
    color_100="#b2dfdb",
    color_200="#80cbc4",
    color_300="#4db6ac",
    color_400="#26a69a",
    color_500="#009688",
    color_600="#00897b",
    color_700="#00796b",
    color_800="#00695c",
    color_900="#004d40",
    color_a100="#a7ffeb",
    color_a200="#64ffda",
    color_a400="#1de9b6",
    color_a700="#00bfa5",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


GREEN = ColorPalette(
    name="green",
    color_50="#e8f5e9",
    color_100="#c8e6c9",
    color_200="#a5d6a7",
    color_300="#81c784",
    color_400="#66bb6a",
    color_500="#4caf50",
    color_600="#43a047",
    color_700="#388e3c",
    color_800="#2e7d32",
    color_900="#1b5e20",
    color_a100="#b9f6ca",
    color_a200="#69f0ae",
    color_a400="#00e676",
    color_a700="#00c853",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


LIGHT_GREEN = ColorPalette(
    name="light_green",
    color_50="#f1f8e9",
    color_100="#dcedc8",
    color_200="#c5e1a5",
    color_300="#aed581",
    color_400="#9ccc65",
    color_500="#8bc34a",
    color_600="#7cb342",
    color_700="#689f38",
    color_800="#558b2f",
    color_900="#33691e",
    color_a100="#ccff90",
    color_a200="#b2ff59",
    color_a400="#76ff03",
    color_a700="#64dd17",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.DARK_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


LIME = ColorPalette(
    name="lime",
    color_50="#f9fbe7",
    color_100="#f0f4c3",
    color_200="#e6ee9c",
    color_300="#dce775",
    color_400="#d4e157",
    color_500="#cddc39",
    color_600="#c0ca33",
    color_700="#afb42b",
    color_800="#9e9d24",
    color_900="#827717",
    color_a100="#f4ff81",
    color_a200="#eeff41",
    color_a400="#c6ff00",
    color_a700="#aeea00",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.DARK_PRIMARY_TEXT,
    contrast_700=color.DARK_PRIMARY_TEXT,
    contrast_800=color.DARK_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


YELLOW = ColorPalette(
    name="yellow",
    color_50="#fffde7",
    color_100="#fff9c4",
    color_200="#fff59d",
    color_300="#fff176",
    color_400="#ffee58",
    color_500="#ffeb3b",
    color_600="#fdd835",
    color_700="#fbc02d",
    color_800="#f9a825",
    color_900="#f57f17",
    color_a100="#ffff8d",
    color_a200="#ffff00",
    color_a400="#ffea00",
    color_a700="#ffd600",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.DARK_PRIMARY_TEXT,
    contrast_700=color.DARK_PRIMARY_TEXT,
    contrast_800=color.DARK_PRIMARY_TEXT,
    contrast_900=color.DARK_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


AMBER = ColorPalette(
    name="amber",
    color_50="#fff8e1",
    color_100="#ffecb3",
    color_200="#ffe082",
    color_300="#ffd54f",
    color_400="#ffca28",
    color_500="#ffc107",
    color_600="#ffb300",
    color_700="#ffa000",
    color_800="#ff8f00",
    color_900="#ff6f00",
    color_a100="#ffe57f",
    color_a200="#ffd740",
    color_a400="#ffc400",
    color_a700="#ffab00",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.DARK_PRIMARY_TEXT,
    contrast_700=color.DARK_PRIMARY_TEXT,
    contrast_800=color.DARK_PRIMARY_TEXT,
    contrast_900=color.DARK_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


ORANGE = ColorPalette(
    name="orange",
    color_50="#fff3e0",
    color_100="#ffe0b2",
    color_200="#ffcc80",
    color_300="#ffb74d",
    color_400="#ffa726",
    color_500="#ff9800",
    color_600="#fb8c00",
    color_700="#f57c00",
    color_800="#ef6c00",
    color_900="#e65100",
    color_a100="#ffd180",
    color_a200="#ffab40",
    color_a400="#ff9100",
    color_a700="#ff6d00",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.DARK_PRIMARY_TEXT,
    contrast_700=color.DARK_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.DARK_PRIMARY_TEXT,
)


DEEP_ORANGE = ColorPalette(
    name="deep_orange",
    color_50="#fbe9e7",
    color_100="#ffccbc",
    color_200="#ffab91",
    color_300="#ff8a65",
    color_400="#ff7043",
    color_500="#ff5722",
    color_600="#f4511e",
    color_700="#e64a19",
    color_800="#d84315",
    color_900="#bf360c",
    color_a100="#ff9e80",
    color_a200="#ff6e40",
    color_a400="#ff3d00",
    color_a700="#dd2c00",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


BROWN = ColorPalette(
    name="brown",
    color_50="#efebe9",
    color_100="#d7ccc8",
    color_200="#bcaaa4",
    color_300="#a1887f",
    color_400="#8d6e63",
    color_500="#795548",
    color_600="#6d4c41",
    color_700="#5d4037",
    color_800="#4e342e",
    color_900="#3e2723",
    color_a100="#d7ccc8",
    color_a200="#bcaaa4",
    color_a400="#8d6e63",
    color_a700="#5d4037",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.LIGHT_PRIMARY_TEXT,
    contrast_400=color.LIGHT_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


GREY = ColorPalette(
    name="grey",
    color_50="#fafafa",
    color_100="#f5f5f5",
    color_200="#eeeeee",
    color_300="#e0e0e0",
    color_400="#bdbdbd",
    color_500="#9e9e9e",
    color_600="#757575",
    color_700="#616161",
    color_800="#424242",
    color_900="#212121",
    color_a100="#ffffff",
    color_a200="#eeeeee",
    color_a400="#bdbdbd",
    color_a700="#616161",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.DARK_PRIMARY_TEXT,
    contrast_500=color.DARK_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.DARK_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)


BLUE_GREY = ColorPalette(
    name="blue_grey",
    color_50="#eceff1",
    color_100="#cfd8dc",
    color_200="#b0bec5",
    color_300="#90a4ae",
    color_400="#78909c",
    color_500="#607d8b",
    color_600="#546e7a",
    color_700="#455a64",
    color_800="#37474f",
    color_900="#263238",
    color_a100="#cfd8dc",
    color_a200="#b0bec5",
    color_a400="#78909c",
    color_a700="#455a64",
    contrast_50=color.DARK_PRIMARY_TEXT,
    contrast_100=color.DARK_PRIMARY_TEXT,
    contrast_200=color.DARK_PRIMARY_TEXT,
    contrast_300=color.DARK_PRIMARY_TEXT,
    contrast_400=color.LIGHT_PRIMARY_TEXT,
    contrast_500=color.LIGHT_PRIMARY_TEXT,
    contrast_600=color.LIGHT_PRIMARY_TEXT,
    contrast_700=color.LIGHT_PRIMARY_TEXT,
    contrast_800=color.LIGHT_PRIMARY_TEXT,
    contrast_900=color.LIGHT_PRIMARY_TEXT,
    contrast_a100=color.DARK_PRIMARY_TEXT,
    contrast_a200=color.DARK_PRIMARY_TEXT,
    contrast_a400=color.LIGHT_PRIMARY_TEXT,
    contrast_a700=color.LIGHT_PRIMARY_TEXT,
)

PALETTES = [
    AMBER,
    BLUE_GREY,
    BLUE,
    BROWN,
    CYAN,
    DEEP_ORANGE,
    DEEP_PURPLE,
    GREEN,
    GREY,
    INDIGO,
    LIGHT_BLUE,
    LIGHT_GREEN,
    LIME,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    TEAL,
    YELLOW,
]
