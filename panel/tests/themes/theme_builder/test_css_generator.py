"""In this module we test the Css Generator functionality"""
import panel as pn
from panel.themes.theme_builder import (
    CssGenerator,
    DarkCssGenerator,
    DEFAULT_CSS_GENERATOR,
    DARK_CSS_GENERATOR,
    PANEL_COLOR_SCHEME,
    CHESTERISH_COLOR_SCHEME,
)
from panel.tests.themes.theme_test_app import ThemeTestApp


def test_can_construct():
    """Can construct CssGenerator"""
    # When:
    generator = CssGenerator()

    # Then
    assert generator.panel_css == ""
    assert generator.dataframe_css == ""


def test_dark_css_constructor():
    """Can construct DarkCssGenerator"""
    # When
    generator = DarkCssGenerator()

    # Then
    assert generator.panel_css != ""
    assert generator.dataframe_css != ""


def test_changing_color_updates_css():
    """When a user changes a color the css updates accordingly"""
    # Given
    generator = DarkCssGenerator()
    panel_css = generator.panel_css
    # When
    generator.color_scheme.primary = "#000000"
    # Then
    assert panel_css != generator.panel_css

def test_can_change_color_scheme():
    # Given
    generator = DarkCssGenerator()
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
    generator.color_scheme.primary = "#000000"
    # Then
    assert panel_css != generator.panel_css


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    DarkCssGenerator(color_scheme=CHESTERISH_COLOR_SCHEME).view().servable()
