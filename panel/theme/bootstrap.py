from __future__ import annotations

import pathlib

import param

from ..io.resources import CSS_URLS, JS_URLS
from ..layout import Card
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

    _modifiers = {
        Number: {
            'default_color': 'var(--mdc-theme-on-background)'
        }
    }


class Bootstrap(Design):

    _modifiers = {
        Card: {
            'children': {'margin': (10, 10)},
            'button_css_classes': ['card-button'],
            'margin': (10, 5)
        },
        Tabulator: {
            'theme': 'bootstrap4'
        },
        Viewable: {
            'stylesheets': [Inherit, 'css/bootstrap.css']
        }
    }

    _themes = {
        'default': BootstrapDefaultTheme,
        'dark': BootstrapDarkTheme
    }

    _resources = {
        'css': {
            'bootstrap': CSS_URLS['bootstrap5']
        },
        'js': {
            'bootstrap': JS_URLS['bootstrap5']
        }
    }
