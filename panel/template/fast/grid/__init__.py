"""
The Fast GridTemplate provides a grid layout based on React Grid
Layout similar to the Panel ReactTemplate but in the Fast.design style
and enabling the use of Fast components.
"""
import pathlib

import param

from ..base import FastGridBaseTemplate
from ..theme import FastDarkTheme, FastDefaultTheme


class FastGridTemplate(FastGridBaseTemplate):
    """
    The `FastGridTemplate` is a grid based Template with a header, sidebar and main area. It is
    based on the fast.design style and works well in both default (light) and dark mode.

    Reference: https://panel.holoviz.org/reference/templates/FastGridTemplate.html

    Example:

    >>> template = pn.template.FastGridTemplate(
    ...     site="Panel", title="FastGridTemplate", accent="#A01346",
    ...     sidebar=[pn.pane.Markdown("## Settings"), some_slider],
    ... ).servable()
    >>> template.main[0:6,:]=some_python_object

    Some *accent* colors that work well are #A01346 (Fast), #00A170 (Mint), #DAA520 (Golden Rod),
    #2F4F4F (Dark Slate Grey), #F08080 (Light Coral) and #4099da (Summer Sky).

    Please note the `FastListTemplate` cannot display in a notebook output cell.
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
