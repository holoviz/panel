def get_theme(theme):
    print("background", theme.background.background)
    if theme.background.background == "#303030":
        return get_dark_theme(theme)
    else:
        return get_light_theme(theme)

def get_light_theme(theme):
    return {}

def get_dark_theme(theme):
    text = theme.foreground.text
    dark50 = theme.background.background
    dark100 = theme.background.dialog
    dark75 = theme.background.app_bar

    return {
        "attrs": {
            "Figure": {
                "background_fill_color": dark50,
                "border_fill_color": dark100,
                "outline_line_color": dark75,
                "outline_line_alpha": 0.25,
            },
            "Grid": {"grid_line_color": text, "grid_line_alpha": 0.25},
            "Axis": {
                "major_tick_line_alpha": 0,
                "major_tick_line_color": text,
                "minor_tick_line_alpha": 0,
                "minor_tick_line_color": text,
                "axis_line_alpha": 0,
                "axis_line_color": text,
                "major_label_text_color": text,
                "major_label_text_font": "OrstedSansRegular, sans-serif, Verdana",
                "major_label_text_font_size": "1.025em",
                "axis_label_standoff": 10,
                "axis_label_text_color": text,
                "axis_label_text_font": "OrstedSansRegular, sans-serif, Verdana",
                "axis_label_text_font_size": "1.25em",
                "axis_label_text_font_style": "normal",
            },
            "Legend": {
                "spacing": 8,
                "glyph_width": 15,
                "label_standoff": 8,
                "label_text_color": text,
                "label_text_font": "OrstedSansRegular, sans-serif, Verdana",
                "label_text_font_size": "1.025em",
                "border_line_alpha": 0,
                "background_fill_alpha": 0.25,
                "background_fill_color": dark75,
            },
            "ColorBar": {
                "title_text_color": text,
                "title_text_font": "OrstedSansRegular, sans-serif, Verdana",
                "title_text_font_size": "1.025em",
                "title_text_font_style": "normal",
                "major_label_text_color": text,
                "major_label_text_font": "OrstedSansRegular, sans-serif, Verdana",
                "major_label_text_font_size": "1.025em",
                "background_fill_color": dark75,
                "major_tick_line_alpha": 0,
                "bar_line_alpha": 0,
            },
            "Title": {
                "text_color": text,
                "text_font": "OrstedSansRegular, sans-serif, Verdana",
                "text_font_size": "1.15em",
            },
        }
    }