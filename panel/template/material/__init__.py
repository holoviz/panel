"""
Material template based on the material web components library.
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import MaterialDarkTheme, MaterialTheme

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

    _resources = {
        'css': {
            'material': "https://unpkg.com/material-components-web@v4.0.0/dist/material-components-web.min.css",
        },
        'js': {
            'material': "https://unpkg.com/material-components-web@v4.0.0/dist/material-components-web.min.js"
        }
    }


class MaterialDefaultTheme(MaterialTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = MaterialTemplate


class MaterialDarkTheme(MaterialDarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = MaterialTemplate
