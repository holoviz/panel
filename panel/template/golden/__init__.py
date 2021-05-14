"""
GoldenTemplate based on the golden-layout library.
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class GoldenTemplate(BasicTemplate):
    """
    GoldenTemplate is built on top of golden-layout library.
    """
    sidebar_width = param.Integer(20, doc="""
        The width of the sidebar in percent. Default is 20.""")

    _css = pathlib.Path(__file__).parent / 'golden.css'

    _template = pathlib.Path(__file__).parent / 'golden.html'

    _modifiers = {
        Card: {
            'children': {'margin': (10, 10)},
            'button_css_classes': ['golden-card-button']
        },
    }

    _resources = {
        'css': {
            'goldenlayout': "https://golden-layout.com/files/latest/css/goldenlayout-base.css",
        },
        'js': {
            'jquery': "http://code.jquery.com/jquery-1.11.1.min.js",
            'goldenlayout': "https://golden-layout.com/files/latest/js/goldenlayout.js"
        }
    }

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)


class GoldenDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = GoldenTemplate


class GoldenDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = GoldenTemplate
