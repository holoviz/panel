"""	
GoldenTemplate based on the golden-layout library.	
"""	
import pathlib	

import param	

from ..base import BasicTemplate	
from ..theme import DarkTheme, DefaultTheme


class GoldenTemplate(BasicTemplate):	
    """	
    GoldenTemplate is built on top of golden-layout library.	
    """	
    _css = pathlib.Path(__file__).parent / 'golden.css'	

    _template = pathlib.Path(__file__).parent / 'golden.html'	


class GoldenDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = GoldenTemplate


class GoldenDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = GoldenTemplate
