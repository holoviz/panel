"""In this module we the the ThemeBuilder functionality"""
import panel as pn
from panel.themes.theme_builder import (
    ColorScheme,
    CssGenerator,
    ThemeBuilder,
    ComponentViewer,
    COLOR_SCHEMES,
    PANEL_COLOR_SCHEME,
    ANGULAR_DARK_COLOR_SCHEME,
)


def test_can_construct_with_css_generator():
    """Can constructor ThemeBuilder with custom css_generator"""
    # When
    css_generator = CssGenerator()
    theme = ThemeBuilder(css_generator=css_generator)
    # Then
    assert theme.css_generator == css_generator
    assert theme.css_generator.panel_css != ""
    assert theme.css_generator.dataframe_css != ""


def test_changing_color_changes_scheme():
    """If a user change a color then the css scheme changes accordingly"""
    # Given
    theme = ThemeBuilder()
    panel_css = theme.css_generator.panel_css

    # When
    theme.css_generator.color_scheme.primary = "green"
    # Then
    assert theme.css_generator.color_scheme.primary == "#000000"
    assert panel_css != theme.css_generator._get_panel_css()
    assert panel_css != theme.css_generator.panel_css


def test_can_change_css_generator_and_color_scheme():
    """A user can change the css_generator and color_scheme"""
    # Given
    theme = ThemeBuilder()
    # When
    theme.css_generator = CssGenerator()
    theme.color_scheme = ANGULAR_DARK_COLOR_SCHEME
    # Then
    assert theme.css_generator.color_scheme.primary == ANGULAR_DARK_COLOR_SCHEME.primary

def test_can_view():
    ThemeBuilder().view()

if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"

    # @Philippfr: The app does not seem to stretch_width
    # Neither the Row or the ThemeTestApp
    app = pn.Row(
            ThemeBuilder().view(max_width=400),
            pn.layout.VSpacer(width=25),
            ComponentViewer().view(),
        ).servable()
