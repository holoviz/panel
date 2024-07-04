from __future__ import annotations

import pathlib

import param

from ..io.resources import CDN_DIST, CSS_URLS, JS_URLS
from ..layout import Accordion, Card
from ..viewable import Viewable
from ..widgets import Number, Tabulator
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)


class BootstrapDefaultTheme(DefaultTheme):
    """
    The BootstrapDefaultTheme is a light theme.
    """

    css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'bootstrap_default.css')

    _bs_theme = 'light'


class BootstrapDarkTheme(DarkTheme):
    """
    The BootstrapDarkTheme is a Dark Theme in the style of Bootstrap
    """

    css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'bootstrap_dark.css')

    _bs_theme = 'dark'

    modifiers = {
        Number: {
            'default_color': 'white'
        }
    }


class Bootstrap(Design):

    modifiers = {
        Accordion: {
            'active_header_background': 'var(--bs-surface-bg)'
        },
        Card: {
            'children': {'margin': (10, 10)},
            'button_css_classes': ['card-button'],
            'margin': (10, 5)
        },
        Tabulator: {
            'theme': 'bootstrap5',
            'theme_classes': ['table-sm']
        },
        Viewable: {
            'stylesheets': [Inherit, f'{CDN_DIST}bundled/theme/bootstrap.css']
        }
    }

    _themes = {
        'dark': BootstrapDarkTheme,
        'default': BootstrapDefaultTheme,
    }

    _resources = {
        'css': {
            'bootstrap': CSS_URLS['bootstrap5']
        },
        'js': {
            'bootstrap': JS_URLS['bootstrap5']
        }
    }
