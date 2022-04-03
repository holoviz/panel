"""
Bootstrap template based on the bootstrap.css library.
"""
import pathlib

import param

from ...io.resources import CSS_URLS, JS_URLS
from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class BootstrapTemplate(BasicTemplate):
    """
    BootstrapTemplate
    """

    sidebar_width = param.Integer(350, doc="""
        The width of the sidebar in pixels. Default is 350.""")

    _css = pathlib.Path(__file__).parent / 'bootstrap.css'

    _template = pathlib.Path(__file__).parent / 'bootstrap.html'

    _modifiers = {
        Card: {
            'children': {'margin': (10, 10)},
            'button_css_classes': ['card-button'],
            'margin': (10, 5)
        },
    }

    _resources = {
        'css': {
            'bootstrap': CSS_URLS['bootstrap4']
        },
        'js': {
            'jquery': JS_URLS['jQuery'],
            'bootstrap': JS_URLS['bootstrap4']
        }
    }


class BootstrapDefaultTheme(DefaultTheme):

    _template = BootstrapTemplate


class BootstrapDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = BootstrapTemplate
