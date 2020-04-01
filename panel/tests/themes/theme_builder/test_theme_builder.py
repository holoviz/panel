"""In this module we the the ThemeBuilder functionality"""
import panel as pn
from panel.themes.theme_builder import (
    ColorScheme,
    CssGenerator,
    ThemeBuilder,
    ComponentViewer,
    COLOR_SCHEMES,
    DEFAULT_CSS_GENERATOR,
    DARK_CSS_GENERATOR,
    PANEL_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
)


def test_can_construct_with_css_generator():
    """Can constructor ThemeBuilder with custom css_generator"""
    # When
    theme = ThemeBuilder(css_generator=DARK_CSS_GENERATOR)
    # Then
    assert theme.css_generator == DARK_CSS_GENERATOR
    assert theme.css_generator.panel_css != ""
    assert theme.css_generator.dataframe_css != ""


def test_can_change_css_generator():
    """Can change css_generator of ThemeBuilder"""
    # Given
    theme = ThemeBuilder(css_generator=DEFAULT_CSS_GENERATOR)
    assert theme.css_generator.panel_css == ""
    assert theme.css_generator.dataframe_css == ""
    # When
    theme.css_generator = DARK_CSS_GENERATOR
    # Then
    assert theme.css_generator.panel_css != ""
    assert theme.css_generator.dataframe_css != ""


def test_changing_color_changes_scheme():
    """If a user change a color then the css scheme changes accordingly"""
    # Given
    theme = ThemeBuilder()
    theme.css_generator = DARK_CSS_GENERATOR
    panel_css = theme.css_generator.panel_css

    # When
    theme.css_generator.color_scheme.primary = "#000000"
    # Then
    assert theme.css_generator.color_scheme.primary == "#000000"
    assert panel_css != theme.css_generator._get_panel_css()
    assert panel_css != theme.css_generator.panel_css


def test_can_change_css_generator_and_color_scheme():
    """A user can change the css_generator and color_scheme"""
    # Given
    theme = ThemeBuilder()
    # When
    theme.css_generator = DARK_CSS_GENERATOR
    theme.color_scheme = ANGULAR_DARK_COLOR_SCHEME
    # Then
    assert theme.css_generator.color_scheme.primary == ANGULAR_DARK_COLOR_SCHEME.primary


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"

    # @Philippfr: The app does not seem to stretch_width
    # Neither the Row or the ThemeTestApp
    app = pn.Row(
            ThemeBuilder().view(max_width=400),
            pn.layout.VSpacer(width=25),
            ComponentViewer().view(),
        ).servable()
