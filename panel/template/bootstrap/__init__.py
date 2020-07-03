"""
Bootstrap template based on the bootstrap.css library.
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class BootstrapTemplate(BasicTemplate):
    """
    BootstrapTemplate
    """

    _css = pathlib.Path(__file__).parent / 'bootstrap.css'

    _template = pathlib.Path(__file__).parent / 'bootstrap.html'

    _modifiers = {
        Card: {
            'children': {'margin': (0, 10)},
            'button_css_classes': ['card-button']
        },
    }


class BootstrapDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = BootstrapTemplate


class BootstrapDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = BootstrapTemplate
