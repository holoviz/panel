"""In this module we test the Color Scheme generator"""
from panel.themes.theme_builder import ColorScheme


def test_can_construct():
    """Can constructor ColorScheme"""
    ColorScheme()

def test_can_view():
    """Can view ColorScheme"""
    # Given
    scheme = ColorScheme()
    # When
    scheme.view()
    # Then: No exception is raised

if __name__.startswith("bokeh"):
    ColorScheme().view().servable()
