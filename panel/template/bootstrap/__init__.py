"""
Bootstrap template based on the bootstrap.css library.
"""
import pathlib

import param

from ...config import config
from ...layout import Row, Column, HSpacer, Spacer, ListLike, Card
from ...pane import HTML
from ..base import BasicTemplate
from ..theme import DefaultTheme


class BootstrapTemplate(BasicTemplate):
    """
    BootstrapTemplate
    """

    _css = pathlib.Path(__file__).parent / 'bootstrap.css'

    _template = pathlib.Path(__file__).parent / 'bootstrap.html'

    _modifiers = {
        Card: {
            'button_css_classes': ['card-button']
        },
    }


class BootstrapDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = BootstrapTemplate
