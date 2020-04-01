"""In this module we test the functionality of the theme_builder module"""
from panel.themes.theme_builder.color_utils import (
    rgb_to_hex,
    hex_to_rgb,
    rgb_to_hsl,
    hsl_to_rgb,
    hex_to_hsl,
    hsl_to_hex,
    compute_colors,
    multiply,
    is_dark,
    is_light,
    mix,
    saturate,
    lighten,
    tetrad,
)
import pytest


@pytest.fixture
def color():
    return "#9c27b0"


@pytest.fixture
def rgb():
    return (156, 39, 176)


@pytest.fixture
def hsl():
    # Corresponds to 291°, 64%, 42%
    return (0.8090024330900243, 0.6372093023255814, 0.4215686274509804)

# Source: https://material.io/inline-tools/color/
MATERIAL_OFFICIAL_PALETTE = {
    "50": "#f3e5f5",
    "100": "#e1bee7",
    "200": "#ce93d8",
    "300": "#ba68c8",
    "400": "#ab47bc",
    "500": "#9c27b0",
    "600": "#8e24aa",
    "700": "#7b1fa2",
    "800": "#6a1b9a",
    "900": "#4a148c",
    "A100": "#ea80fc",
    "A200": "#e040fb",
    "A400": "#d500f9",
    "A700": "#aa00ff",
}

# Source: http://mcg.mbitson.com/#!?mcgpalette0=%239c27b0
# DIFFERS TO THE OFFICIAL MATERIAL_OFFICIAL_PALETTE. DONT KNOW WHY.
MCG_MBITSON_COM_PALETTE = {
    "50": "#f3e5f6",
    "100": "#e1bee7",
    "200": "#ce93d8",
    "300": "#ba68c8",
    "400": "#ab47bc",
    "500": "#9c27b0",
    "600": "#9423a9",
    "700": "#8a1da0",
    "800": "#801797",
    "900": "#6e0e87",
    "A100": "#efb8ff",
    "A200": "#e485ff",
    "A400": "#d852ff",
    "A700": "#d238ff ",
}

# Source: Panel code
# Differs a bit to the MCG_MBITSON_COM_PALETTE due to rounding I would assume.
PANEL_PALETTE = {
    "50": "#f3e5f6",
    "100": "#e1bee7",
    "200": "#ce93d8",
    "300": "#ba68c8",
    "400": "#ab47bc",
    "500": "#9c27b0",
    "600": "#9423a9",
    "700": "#8a1da0",
    "800": "#801797",
    "900": "#6e0e87",
    "A100": "#f4d8ff",
    "A200": "#e7a4ff",
    "A400": "#d972ff",
    "A700": "#d358ff",
}

MCG_MBITSON_COM_PALETTE_W_CONTRAST = {
    "50" : "#f3e5f6",
    "100" : "#e1bee7",
    "200" : "#ce93d8",
    "300" : "#ba68c8",
    "400" : "#ab47bc",
    "500" : "#9c27b0",
    "600" : "#9423a9",
    "700" : "#8a1da0",
    "800" : "#801797",
    "900" : "#6e0e87",
    "A100" : "#efb8ff",
    "A200" : "#e485ff",
    "A400" : "#d852ff",
    "A700" : "#d238ff",
    "contrast": {
        "50" : "#000000",
        "100" : "#000000",
        "200" : "#000000",
        "300" : "#000000",
        "400" : "#ffffff",
        "500" : "#ffffff",
        "600" : "#ffffff",
        "700" : "#ffffff",
        "800" : "#ffffff",
        "900" : "#ffffff",
        "A100" : "#000000",
        "A200" : "#000000",
        "A400" : "#000000",
        "A700" : "#ffffff",
    }
}

@pytest.fixture
def color_palette():
    return MCG_MBITSON_COM_PALETTE


def test_rgb_to_hex(rgb, color):
    assert rgb_to_hex(rgb) == color


def test_hex_to_rgb(color, rgb):
    assert hex_to_rgb(color) == rgb


def test_rgb_to_hsl(rgb, hsl):
    assert rgb_to_hsl(rgb) == hsl


def test_hsl_to_rgb(hsl, rgb):
    assert hsl_to_rgb(hsl) == rgb


def test_hex_to_hsl(color, hsl):
    assert hex_to_hsl(color) == hsl


def test_hsl_to_hex(hsl, color):
    assert hsl_to_hex(hsl) == color


def test_tetrad():
    # given
    red = "#ff0000"
    # When
    actual = tetrad(red)
    # Then
    assert actual == [red, "#80ff00", "#00ffff", "#7f00ff"]


def test_mix():
    white = "#ffffff"
    black = "#000000"
    mix90 = "#1a1a1a"
    assert mix(white, black, 0) == white
    assert mix(white, black, 100) == black
    assert mix(white, black, 90) == mix90


def test_mix_black_and_white():
    white = "#ffffff"
    black = "#000000"
    for amount in range(0, 101):
        color = mix(black, white, amount)
        h, s, l = hex_to_hsl(color)
        l = round(l * 100) / 100
        assert (h, s, l) == (0, 0, amount / 100)


def test_saturate():
    red = "#ff0000"
    saturations = ["#ff0000"]*101
    for saturation in range(0, 101):
        actual = saturate(red, saturation)
        assert actual == saturations[saturation]


def test_lighten():
    red = "#ff0000"
    # Change item 35 from #ffb3b3 to #ffb2b2
    lightens = [
        "#ff0000",
        "#ff0505",
        "#ff0a0a",
        "#ff0f0f",
        "#ff1414",
        "#ff1a1a",
        "#ff1f1f",
        "#ff2424",
        "#ff2929",
        "#ff2e2e",
        "#ff3333",
        "#ff3838",
        "#ff3d3d",
        "#ff4242",
        "#ff4747",
        "#ff4d4d",
        "#ff5252",
        "#ff5757",
        "#ff5c5c",
        "#ff6161",
        "#ff6666",
        "#ff6b6b",
        "#ff7070",
        "#ff7575",
        "#ff7a7a",
        "#ff8080",
        "#ff8585",
        "#ff8a8a",
        "#ff8f8f",
        "#ff9494",
        "#ff9999",
        "#ff9e9e",
        "#ffa3a3",
        "#ffa8a8",
        "#ffadad",
        "#ffb2b2",
        "#ffb8b8",
        "#ffbdbd",
        "#ffc2c2",
        "#ffc7c7",
        "#ffcccc",
        "#ffd1d1",
        "#ffd6d6",
        "#ffdbdb",
        "#ffe0e0",
        "#ffe5e5",
        "#ffebeb",
        "#fff0f0",
        "#fff5f5",
        "#fffafa",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
        "#ffffff",
    ]
    for amount in range(0, 101):
        actual = lighten(red, amount)
        assert actual == lightens[amount]


def test_multiply():
    # Given
    color = "#9c27b0"
    # When
    actual = multiply(color, color)
    # Then
    assert actual == "#5f0579"  # Should be #5f0679 without rounding


def test_compute_colors(color, color_palette):
    # When
    actual = compute_colors(color)
    # Then
    assert actual == color_palette

@pytest.mark.parametrize(["color", "expected"], [
    ("#f3e5f6", False),
    ("#e1bee7", False),
    ("#ce93d8", False),
    ("#ba68c8", False),
    ("#ab47bc", True),
    ("#9c27b0", True),
    ("#9423a9", True),
    ("#8a1da0", True),
    ("#801797", True),
    ("#6e0e87", True),
    ("#efb8ff", False),
    ("#e485ff", False),
    ("#d852ff", False),
    ("#d238ff", True),
])
def test_is_dark(color, expected):
    assert is_dark(color)==expected
    assert is_light(color)!=expected