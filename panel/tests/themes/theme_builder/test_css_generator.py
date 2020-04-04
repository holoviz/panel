"""In this module we test the Css Generator functionality"""
import panel as pn
from panel.themes.theme_builder import (
    CssGenerator,
    CHESTERISH_COLOR_SCHEME,
)
from panel.themes.theme_builder import color_palette

def test_can_construct():
    """Can construct CssGenerator"""
    # When:
    generator = CssGenerator()

    # Then
    assert generator.panel_css != ""
    assert generator.dataframe_css != ""


def test_changing_color_updates_css():
    """When a user changes a color the css updates accordingly"""
    # Given
    generator = CssGenerator()
    assert generator.color_scheme.primary != color_palette.YELLOW
    panel_css = generator.panel_css
    # When
    generator.color_scheme.primary = color_palette.YELLOW
    # Then
    assert panel_css != generator.panel_css

def test_can_update_color_scheme():
    """Can change the color scheme"""
    # Given
    generator = CssGenerator()
    panel_css = generator.panel_css
    # When
    # @Philipfr: I would have liked to havee
    # generator.color_scheme = CHESTERISH_COLOR_SCHEME
    # But then it seems the @param.depends of _set_panel_css no longer works
    generator.color_scheme.update(CHESTERISH_COLOR_SCHEME)
    # Then
    assert panel_css != generator.panel_css

    # When
    panel_css = generator.panel_css
    generator.color_scheme.primary = color_palette.DEEP_ORANGE
    # Then
    assert panel_css != generator.panel_css


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    app = CssGenerator()
    app.color_scheme.update(CHESTERISH_COLOR_SCHEME)
    app.view().servable()
