"""In this module we test the functionality of the ColorPalette"""
from panel.themes.theme_builder import ColorPalette
import panel as pn

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
