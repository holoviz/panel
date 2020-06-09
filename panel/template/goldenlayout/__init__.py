"""
GoldenLayout template based on the golden_layout web components library.
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class GoldenLayoutTemplate(BasicTemplate):
    """
    GoldenLayoutTemplate is built on top of GoldenLayout web components.
    """

    _css = pathlib.Path(__file__).parent / 'golden_layout.css'

    _template = pathlib.Path(__file__).parent / 'golden_layout.html'

    _modifiers = {
        Card: {
        },
    }


class GoldenLayoutDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = GoldenLayoutTemplate


class GoldenLayoutDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = GoldenLayoutTemplate
