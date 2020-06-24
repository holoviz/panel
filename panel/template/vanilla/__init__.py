"""
Vanilla template 
"""
import pathlib

import param

from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme



class VanillaTemplate(BasicTemplate):
    """
    VanillaTemplate is built on top of Vanilla web components.
    """

    _css = pathlib.Path(__file__).parent / 'vanilla.css'

    _template = pathlib.Path(__file__).parent / 'vanilla.html'

class VanillaDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = VanillaTemplate


class VanillaDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = VanillaTemplate
