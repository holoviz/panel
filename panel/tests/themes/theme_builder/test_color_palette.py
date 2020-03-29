"""In this module we test the functionality of the ColorPalette"""
from panel.themes.theme_builder import ColorPalette


def test_can_construct():
    """Can constructor ColorPalette"""
    ColorPalette()

def test_can_view():
    """Can view ColorPalette"""
    # Given
    palette = ColorPalette()
    # When
    palette.view()
    # Then: No exception is raised

if __name__.startswith("bokeh"):
    ColorPalette().view().servable()