from __future__ import annotations

from ..io.resources import CDN_DIST
from ..viewable import Viewable
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)


class NativeDefaultTheme(DefaultTheme):
    ""


class NativeDarkTheme(DarkTheme):
    # Inherits modifiers from DarkTheme (Number and String with 'default_color': 'white')
    pass


class Native(Design):
    modifiers = {Viewable: {"stylesheets": [Inherit, f"{CDN_DIST}bundled/theme/native.css"]}}

    _themes = {"dark": NativeDarkTheme, "default": NativeDefaultTheme}
