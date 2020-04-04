"""In this module we test the functionality of the ColorPalette"""
from panel.themes.theme_builder import ColorPalette
from panel.themes.theme_builder import color_palette
import panel as pn
import pytest

def test_can_construct():
    """Can constructor ColorPalette"""
    ColorPalette()

def test_can_readonly_view():
    """Can view ColorPalette"""
    palette = ColorPalette()
    palette.readonly_view()

def test_can_edit_view():
    """Can view ColorPalette"""
    palette = ColorPalette()
    palette.edit_view()

def test_can_single_color_edit_view():
    """Can view ColorPalette"""
    palette = ColorPalette()
    palette.single_color_edit_view()

if __name__.startswith("bokeh"):
    pn.config.sizing_mode="stretch_width"
    palette = ColorPalette()
    pn.Row(
        # palette.readonly_view,
        palette.single_color_edit_view,
        # palette.edit_view,
    ).servable()

@pytest.mark.parametrize(["palette"], [
    (palette,) for palette in color_palette.PALETTES
])
def test_color_palette_exists_and_is_valid(palette):
    assert isinstance(palette, ColorPalette)