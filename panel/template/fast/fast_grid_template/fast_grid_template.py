"""The Fast GridTemplate provides a grid layout based on React Grid Layout similar to the
Panel ReactTemplate but in the Fast.design style and enabling the
use of Fast components.
"""
import pathlib

import param
from bokeh.themes import Theme as _BkTheme
from panel.template.theme import DarkTheme, DefaultTheme

from panel.template.fast import styles
from panel.template.fast.base import GridBasicTemplate


class FastGridTemplate(GridBasicTemplate):
    """
    The FastGridTemplate is build on top of Fast.design and the React Grid Layout.
    """

    _css = pathlib.Path(__file__).parent / "fast_grid_template.css"
    _js = pathlib.Path(__file__).parent.parent / "assets/js/fast_template.js"

    _template = pathlib.Path(__file__).parent / "fast_grid_template.html"

    def _get_theme(self, name: str = "default"):
        if name == "dark":
            return FastGridDarkTheme
        return FastGridDefaultTheme


class FastGridDefaultTheme(DefaultTheme):
    """The Default Theme of the FastGridTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "default.css")

    _template = FastGridTemplate

    style = param.ClassSelector(class_=styles.FastStyle, default=styles.DEFAULT_STYLE)

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=styles.DEFAULT_BOKEH_THEME)
    )


class FastGridDarkTheme(DarkTheme):
    """The Dark Theme of the FastGridTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "dark.css")

    _template = FastGridTemplate

    style = param.ClassSelector(class_=styles.FastStyle, default=styles.DARK_STYLE)

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=styles.DARK_BOKEH_THEME)
    )
