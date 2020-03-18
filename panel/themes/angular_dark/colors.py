BLUE = "rgb(64,153,218)"
WHITE = "white"
AQUA = "rgb(142, 205, 200)"
AUBERGINE = "rgb(100,76,118)"
CORAL = "rgb(232,87,87)"
SUN = "rgb(253,215,121)"
SAND_LIGHT_100 = "rgb(216,209,202)"
SAND_LIGHT_75 = "rgb(226,221,215)"
SAND_LIGHT_50 = "rgb(236,232,228)"
SAND_LIGHT_25 = "rgb(245,244,242)"
SAND_DARK_100 = "rgb(183,173,165)"
SAND_DARK_75 = "rgb(210,194,187)"
SAND_DARK_50 = "rgb(219,214,210)"
SAND_DARK_25 = "rgb(237,235,233)"
CLOUD_100 = "rgb(153,164,174)"
CLOUD_75 = "rgb(178,187,194)"
CLOUD_50 = "rgb(204,210,214)"
CLOUD_25 = "rgb(229,235,235)"
TEXT_DIGITAL = "rgb(59,73,86)"
TEXT_PRINT = "black"

DARK_100 = "rgb(48,48,48)"
DARK_75 = "rgb(57,57,57)"
DARK_50 = "rgb(66,66,66)"
DARK_25 = "rgb(77,77,77)"
TEXT_DIGITAL_DARK = "rgb(236,236,236)"

PRIMARY_COLORS = [BLUE, WHITE]
SUPPORT_COLORS = [AQUA, AUBERGINE]
HIGHLIGHT_COLORS = [
    CORAL,
    SUN,
]
SAND_LIGHT_COLORS = [
    SAND_LIGHT_100,
    SAND_LIGHT_75,
    SAND_LIGHT_50,
    SAND_LIGHT_25,
]
SAND_DARK_COLORS = [
    SAND_DARK_100,
    SAND_DARK_75,
    SAND_DARK_50,
    SAND_DARK_25,
]
CLOUD_COLORS = [
    CLOUD_100,
    CLOUD_75,
    CLOUD_50,
    CLOUD_25,
]
NEUTRAL_COLORS = [
    CLOUD_100,
    SAND_LIGHT_100,
    SAND_DARK_100,
    CLOUD_75,
    SAND_DARK_75,
    SAND_LIGHT_75,
    CLOUD_50,
    SAND_LIGHT_50,
    SAND_DARK_50,
    CLOUD_25,
    SAND_DARK_25,
    SAND_LIGHT_25,
]
ALL_COLORS = [BLUE] + SUPPORT_COLORS + HIGHLIGHT_COLORS + NEUTRAL_COLORS

COLOR_CYCLE = (
    [BLUE]
    + SUPPORT_COLORS
    + HIGHLIGHT_COLORS
    + [CLOUD_100, SAND_LIGHT_100]
    + [
        "#ffbb78",
        "#2ca02c",
        "#aec7e8",
        "#ff7f0e",
        "#98df8a",
        "#d62728",
        "#ff9896",
        "#9467bd",
        "#c5b0d5",
        "#8c564b",
        "#c49c94",
        "#e377c2",
        "#f7b6d2",
        "#7f7f7f",
        "#c7c7c7",
        "#bcbd22",
        "#dbdb8d",
        "#17becf",
        "#9edae5",
    ]
)
