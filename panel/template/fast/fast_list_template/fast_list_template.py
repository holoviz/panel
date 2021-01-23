"""The FastListTemplate provides a list layout based on similar to the
Panel VanillaTemplate but in the Fast.design style and enabling the
use of Fast components.
"""
import pathlib

import param
from bokeh.themes import Theme as _BkTheme
from panel.template.theme import DarkTheme, DefaultTheme

from panel.template.fast import styles
from panel.template.fast.base import BasicTemplate


class FastListTemplate(BasicTemplate):
    """
    The FastListTemplate is build on top of Fast.design.
    """

    _css = pathlib.Path(__file__).parent / "fast_list_template.css"
    _js = pathlib.Path(__file__).parent.parent / "assets/js/fast_template.js"

    _template = pathlib.Path(__file__).parent / "fast_list_template.html"

    def _get_theme(self, name: str = "default"):
        if name == "dark":
            return DarkTheme
        return DefaultTheme


class DefaultTheme(DefaultTheme):
    """The Default Theme of the FastListTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "default.css")

    _template = FastListTemplate

    style = param.ClassSelector(class_=styles.FastStyle, default=styles.DEFAULT_STYLE)

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=styles.DEFAULT_BOKEH_THEME)
    )


class DarkTheme(DarkTheme):
    """The Dark Theme of the FastListTemplate"""

    css = param.Filename(default=pathlib.Path(__file__).parent / "dark.css")

    _template = FastListTemplate

    style = param.ClassSelector(class_=styles.FastStyle, default=styles.DARK_STYLE)

    bokeh_theme = param.ClassSelector(
        class_=(_BkTheme, str), default=_BkTheme(json=styles.DARK_BOKEH_THEME)
    )
