"""
Bootstrap template based on the bootstrap.css library.
"""
import pathlib

import param

from bokeh.models import ImportedStyleSheet

from ...io.resources import CSS_URLS, JS_URLS
from ...layout import Card
from ...viewable import Viewable
from ...widgets.select import SelectBase
from ..base import BasicTemplate, Inherit
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
        SelectBase: {
            'stylesheets': [Inherit, ImportedStyleSheet(url='/bundled/bootstrap5/css/bootstrap.min.css')]
        },
        Viewable: {
            'stylesheets': [Inherit, ImportedStyleSheet(url='components.css')]
        }
    }

    _resources = {
        'css': {
            'bootstrap': CSS_URLS['bootstrap5']
        },
        'js': {
            'jquery': JS_URLS['jQuery'],
            'bootstrap': JS_URLS['bootstrap5']
        }
    }


class BootstrapDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _bs_theme = 'light'

    _template = BootstrapTemplate


class BootstrapDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _bs_theme = 'dark'

    _template = BootstrapTemplate
