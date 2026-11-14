import pytest

from bokeh.models import Axis, Segment

from panel.theme import (
    Bootstrap, Fast, Material, Native,
)

DESIGNS = [Bootstrap, Fast, Material, Native]


def _apply(design, theme, model):
    bokeh_theme = design(theme=theme).theme.bokeh_theme
    if bokeh_theme is not None:
        bokeh_theme.apply_to_model(model)
    return model


def _segment_color(design, theme, **kwargs):
    return _apply(design, theme, Segment(x0=0, y0=0, x1=1, y1=1, **kwargs)).line_color


def _axis_color(design, theme):
    return _apply(design, theme, Axis()).axis_line_color


@pytest.mark.parametrize('design', DESIGNS)
def test_dark_theme_styles_segments_like_axes(design):
    assert _segment_color(design, 'dark') == _axis_color(design, 'dark')
    assert _segment_color(design, 'dark') != 'black'


@pytest.mark.parametrize('design', DESIGNS)
def test_dark_theme_keeps_explicit_segment_color(design):
    assert _segment_color(design, 'dark', line_color='red') == 'red'


@pytest.mark.parametrize('design', DESIGNS)
def test_default_theme_does_not_style_segments(design):
    assert _segment_color(design, 'default') == 'black'
