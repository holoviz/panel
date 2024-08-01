from __future__ import annotations

import pathlib

import param

from bokeh.themes import Theme as _BkTheme

from ..config import config
from ..io.resources import CDN_DIST
from ..layout import Accordion, Card
from ..viewable import Viewable
from ..widgets import Tabulator
from ..widgets.indicators import Dial, Number, String
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)

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

MATERIAL_BACKGROUND = "#212529"
MATERIAL_DARK_75 = "rgb(57,57,57)"
MATERIAL_SURFACE = "#2b3035"
MATERIAL_DARK_25 = "rgb(77,77,77)"
MATERIAL_TEXT_DIGITAL_DARK = "rgb(236,236,236)"

MATERIAL_DARK_THEME = {
    "attrs": {
        "figure": {
            "background_fill_color": MATERIAL_SURFACE,
            "border_fill_color": MATERIAL_BACKGROUND,
            "outline_line_color": MATERIAL_DARK_75,
            "outline_line_alpha": 0.25,
        },
        "Grid": {
            "grid_line_color": MATERIAL_TEXT_DIGITAL_DARK,
            "grid_line_alpha": 0.25
        },
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
            "background_fill_color": MATERIAL_SURFACE,
        },
        "ColorBar": {
            "title_text_color": MATERIAL_TEXT_DIGITAL_DARK,
            "title_text_font": MATERIAL_FONT,
            "title_text_font_size": "1.025em",
            "title_text_font_style": "normal",
            "major_label_text_color": MATERIAL_TEXT_DIGITAL_DARK,
            "major_label_text_font": MATERIAL_FONT,
            "major_label_text_font_size": "1.025em",
            "background_fill_color": MATERIAL_SURFACE,
            "major_tick_line_alpha": 0,
            "bar_line_alpha": 0,
        },
        "Title": {
            "text_font_size": "1.15em",
        }
    }
}

class MaterialThemeMixin(param.Parameterized):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'material_variables.css')


class MaterialDefaultTheme(MaterialThemeMixin, DefaultTheme):
    """
    The MaterialDefaultTheme is a light theme.
    """

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=MATERIAL_THEME))


class MaterialDarkTheme(MaterialThemeMixin, DarkTheme):
    """
    The MaterialDarkTheme is a Dark Theme in the style of Material Design
    """

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=MATERIAL_DARK_THEME))

    modifiers = {
        Dial: {
            'label_color': 'white'
        },
        Number: {
            'default_color': 'var(--mdc-theme-on-background)'
        },
        String: {
            'default_color': 'var(--mdc-theme-on-background)'
        }
    }


class Material(Design):

    modifiers = {
        Accordion: {
            'active_header_background': 'var(--mdc-theme-surface)'
        },
        Card: {
            'children': {'margin': (5, 10)},
            'title_css_classes': ['mdc-card-title'],
            'css_classes': ['mdc-card'],
            'button_css_classes': ['mdc-button', 'mdc-card-button'],
            'margin': (10, 5)
        },
        Tabulator: {
            'theme': 'materialize'
        },
        Viewable: {
            'stylesheets': [Inherit, f'{CDN_DIST}bundled/theme/material.css']
        }
    }

    _resources = {
        'css': {
            'material': f"{config.npm_cdn}/material-components-web@7.0.0/dist/material-components-web.min.css"
        },
        'font': {
            'roboto': 'https://fonts.googleapis.com/css?family=Roboto:300,400,500',
            'icons': 'https://fonts.googleapis.com/css?family=Material+Icons&display=block'
        },
        'js': {
            'material': f"{config.npm_cdn}/material-components-web@7.0.0/dist/material-components-web.min.js"
        }
    }

    _themes = {
        'default': MaterialDefaultTheme,
        'dark': MaterialDarkTheme
    }
