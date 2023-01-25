"""
Vanilla template
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class VanillaTemplate(BasicTemplate):
    """
    VanillaTemplate is built on top of Vanilla web components.
    """

    _css = pathlib.Path(__file__).parent / 'vanilla.css'

    _template = pathlib.Path(__file__).parent / 'vanilla.html'

    _modifiers = {
        Card: {
            'children': {'margin': (10, 10)},
            'margin': (5, 5)
        }
    }

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)


class VanillaDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = VanillaTemplate


class VanillaDarkTheme(DarkTheme):

    _template = VanillaTemplate
