from bokeh.models import Segment

from panel.theme.fast import (
    DARK_STYLE, DEFAULT_STYLE, FastDarkTheme, FastDefaultTheme,
)


def _segment_line_color(theme, **kwargs):
    segment = Segment(x0=0, y0=0, x1=1, y1=1, **kwargs)
    theme.bokeh_theme.apply_to_model(segment)
    return segment.line_color


def test_fast_dark_theme_styles_segments():
    assert _segment_line_color(FastDarkTheme()) == DARK_STYLE.neutral_foreground_rest


def test_fast_dark_theme_keeps_explicit_segment_color():
    assert _segment_line_color(FastDarkTheme(), line_color='red') == 'red'


def test_fast_default_theme_does_not_style_segments():
    assert 'Segment' not in DEFAULT_STYLE.create_bokeh_theme()['attrs']
    assert _segment_line_color(FastDefaultTheme()) == 'black'
