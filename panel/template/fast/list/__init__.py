"""
The FastListTemplate provides a list layout based on similar to the
Panel VanillaTemplate but in the Fast.design style and enabling the
use of Fast components.
"""
import pathlib

import param

from ..base import FastBaseTemplate
from ..theme import FastDefaultTheme, FastDarkTheme


class FastListTemplate(FastBaseTemplate):
    """
    The FastListTemplate is build on top of Fast.design.
    """

    _css = FastBaseTemplate._css + [
        pathlib.Path(__file__).parent / "fast_list_template.css"
    ]

    _template = pathlib.Path(__file__).parent / "fast_list_template.html"



class FastListDefaultTheme(FastDefaultTheme):
    """The Default Theme of the FastListTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "default.css")

    _template = FastListTemplate


class FastListDarkTheme(FastDarkTheme):
    """The Dark Theme of the FastListTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "dark.css")

    _template = FastListTemplate
