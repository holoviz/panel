"""
The Fast GridTemplate provides a grid layout based on React Grid
Layout similar to the Panel ReactTemplate but in the Fast.design style
and enabling the use of Fast components.
"""
import pathlib

import param

from ..base import FastGridBaseTemplate
from ..theme import FastDefaultTheme, FastDarkTheme


class FastGridTemplate(FastGridBaseTemplate):
    """
    The FastGridTemplate is build on top of Fast.design and the React Grid Layout.
    """

    _css = FastGridBaseTemplate._css + [
        pathlib.Path(__file__).parent / "fast_grid_template.css"
    ]

    _template = pathlib.Path(__file__).parent / "fast_grid_template.html"


class FastGridDefaultTheme(FastDefaultTheme):
    """The Default Theme of the FastGridTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "default.css")

    _template = FastGridTemplate


class FastGridDarkTheme(FastDarkTheme):
    """The Dark Theme of the FastGridTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "dark.css")

    _template = FastGridTemplate
