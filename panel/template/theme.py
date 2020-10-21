import param

from bokeh.themes import Theme as _BkTheme, _dark_minimal


class Theme(param.Parameterized):
    """
    A Theme customizes the look and feel of a Template by providing
    custom CSS and bokeh Theme class.

    When adding a new theme a generic Theme class should be created,
    which is what users will important and set on the Template.theme
    parameter. Additionally a concrete implementation of the Theme
    should be created specific to the particular Template being used.

    For example when adding a DarkTheme there should be a
    corresponding MaterialDarkTheme which declares the Template class
    on its _template class variable. In this way a user can always use
    the generic Theme but the actual CSS and bokeh Theme will depend
    on the exact Template being used.
    """

    css = param.Filename()

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str))

    _template = None

    __abstract = True

    @classmethod
    def find_theme(cls, template_type):
        if cls._template is template_type:
            return cls
        for theme in param.concrete_descendents(cls).values():
            if theme._template is template_type:
                return theme


class DefaultTheme(Theme):
    """
    The DefaultTheme uses the standard Panel color palette.
    """



BOKEH_DARK = dict(_dark_minimal.json)

BOKEH_DARK['attrs']['Figure'].update({
    "background_fill_color": "#3f3f3f",
    "border_fill_color": "#2f2f2f",

})

class DarkTheme(Theme):
    """
    The DefaultTheme uses the standard Panel color palette.
    """

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=BOKEH_DARK))

MATERIAL_FONT = "Roboto, sans-serif, Verdana"
MATERIAL_THEME = {
        "attrs": {
            "Axis": {
                "major_label_text_font": MATERIAL_FONT,
                "major_label_text_font_size": "1.025em",
                "axis_label_standoff": 10,
                "axis_label_text_font": MATERIAL_FONT,
                "axis_label_text_font_size": "1.25em",
                "axis_label_text_font_style": "normal",
            },
            "Legend": {
                "spacing": 8,
                "glyph_width": 15,
                "label_standoff": 8,
                "label_text_font": MATERIAL_FONT,
                "label_text_font_size": "1.025em",
            },
            "ColorBar": {
                "title_text_font": MATERIAL_FONT,
                "title_text_font_size": "1.025em",
                "title_text_font_style": "normal",
                "major_label_text_font": MATERIAL_FONT,
                "major_label_text_font_size": "1.025em",
            },
            "Title": {
                "text_font": MATERIAL_FONT,
                "text_font_size": "1.15em",
            },
        }
    }

class MaterialTheme(Theme):
    """
    The MaterialTheme is a Theme in the style of Material Design
    """

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=MATERIAL_THEME))

# Source: https://material.angular.io/guide/theming#using-a-pre-built-theme
MATERIAL_DARK_100 = "rgb(48,48,48)"
MATERIAL_DARK_75 = "rgb(57,57,57)"
MATERIAL_DARK_50 = "rgb(66,66,66)"
MATERIAL_DARK_25 = "rgb(77,77,77)"
MATERIAL_TEXT_DIGITAL_DARK = "rgb(236,236,236)"
MATERIAL_DARK_THEME = {
        "attrs": {
            "Figure": {
                "background_fill_color": MATERIAL_DARK_50,
                "border_fill_color": MATERIAL_DARK_100,
                "outline_line_color": MATERIAL_DARK_75,
                "outline_line_alpha": 0.25,
            },
            "Grid": {"grid_line_color": MATERIAL_TEXT_DIGITAL_DARK, "grid_line_alpha": 0.25},
            "Axis": {
                "major_tick_line_alpha": 0,
                "major_tick_line_color": MATERIAL_TEXT_DIGITAL_DARK,
                "minor_tick_line_alpha": 0,
                "minor_tick_line_color": MATERIAL_TEXT_DIGITAL_DARK,
                "axis_line_alpha": 0,
                "axis_line_color": MATERIAL_TEXT_DIGITAL_DARK,
                "major_label_text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "major_label_text_font": MATERIAL_FONT,
                "major_label_text_font_size": "1.025em",
                "axis_label_standoff": 10,
                "axis_label_text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "axis_label_text_font": MATERIAL_FONT,
                "axis_label_text_font_size": "1.25em",
                "axis_label_text_font_style": "normal",
            },
            "Legend": {
                "spacing": 8,
                "glyph_width": 15,
                "label_standoff": 8,
                "label_text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "label_text_font": MATERIAL_FONT,
                "label_text_font_size": "1.025em",
                "border_line_alpha": 0,
                "background_fill_alpha": 0.25,
                "background_fill_color": MATERIAL_DARK_75,
            },
            "ColorBar": {
                "title_text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "title_text_font": MATERIAL_FONT,
                "title_text_font_size": "1.025em",
                "title_text_font_style": "normal",
                "major_label_text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "major_label_text_font": MATERIAL_FONT,
                "major_label_text_font_size": "1.025em",
                "background_fill_color": MATERIAL_DARK_75,
                "major_tick_line_alpha": 0,
                "bar_line_alpha": 0,
            },
            "Title": {
                "text_color": MATERIAL_TEXT_DIGITAL_DARK,
                "text_font": MATERIAL_FONT,
                "text_font_size": "1.15em",
            },
        }
    }

class MaterialDarkTheme(Theme):
    """
    The MaterialDarkTheme is a Dark Theme in the style of Material Design
    """

    bokeh_theme = param.ClassSelector(class_=(_BkTheme, str),
                                      default=_BkTheme(json=MATERIAL_DARK_THEME))