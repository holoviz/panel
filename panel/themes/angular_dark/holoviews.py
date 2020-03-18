"""This covers theming holoviews, hvplots and bokeh plots"""
from . import colors

THEME = {
        "attrs": {
            "Figure": {
                "background_fill_color": colors.DARK_50,
                "border_fill_color": colors.DARK_100,
                "outline_line_color": colors.DARK_75,
                "outline_line_alpha": 0.25,
            },
            "Grid": {"grid_line_color": colors.TEXT_DIGITAL_DARK, "grid_line_alpha": 0.25},
            "Axis": {
                "major_tick_line_alpha": 0,
                "major_tick_line_color": colors.TEXT_DIGITAL_DARK,
                "minor_tick_line_alpha": 0,
                "minor_tick_line_color": colors.TEXT_DIGITAL_DARK,
                "axis_line_alpha": 0,
                "axis_line_color": colors.TEXT_DIGITAL_DARK,
                "major_label_text_color": colors.TEXT_DIGITAL_DARK,
                "major_label_text_font": "sans-serif, Verdana",
                "major_label_text_font_size": "1.025em",
                "axis_label_standoff": 10,
                "axis_label_text_color": colors.TEXT_DIGITAL_DARK,
                "axis_label_text_font": "sans-serif, Verdana",
                "axis_label_text_font_size": "1.25em",
                "axis_label_text_font_style": "normal",
            },
            "Legend": {
                "spacing": 8,
                "glyph_width": 15,
                "label_standoff": 8,
                "label_text_color": colors.TEXT_DIGITAL_DARK,
                "label_text_font": "sans-serif, Verdana",
                "label_text_font_size": "1.025em",
                "border_line_alpha": 0,
                "background_fill_alpha": 0.25,
                "background_fill_color": colors.DARK_75,
            },
            "ColorBar": {
                "title_text_color": colors.TEXT_DIGITAL_DARK,
                "title_text_font": "sans-serif, Verdana",
                "title_text_font_size": "1.025em",
                "title_text_font_style": "normal",
                "major_label_text_color": colors.TEXT_DIGITAL_DARK,
                "major_label_text_font": "sans-serif, Verdana",
                "major_label_text_font_size": "1.025em",
                "background_fill_color": colors.DARK_75,
                "major_tick_line_alpha": 0,
                "bar_line_alpha": 0,
            },
            "Title": {
                "text_color": colors.TEXT_DIGITAL_DARK,
                "text_font": "sans-serif, Verdana",
                "text_font_size": "1.15em",
            },
        }
    }
