"""
Material template based on the material web components library.
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme



class MaterialTemplate(BasicTemplate):
    """
    MaterialTemplate is built on top of Material web components.
    """

    _css = pathlib.Path(__file__).parent / 'material.css'

    _template = pathlib.Path(__file__).parent / 'material.html'

    _modifiers = {
        Card: {
            'children': {'margin': (0, 10)},
            'title_css_classes': ['mdc-card-title'],
            'css_classes': ['mdc-card'],
            'header_css_classes': ['mdc-card__primary-action'],
            'button_css_classes': ['mdc-button', 'mdc-card-button']
        },
    }


class MaterialDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = MaterialTemplate


class MaterialDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = MaterialTemplate
