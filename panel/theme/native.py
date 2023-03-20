from __future__ import annotations

from ..io.resources import CDN_DIST
from ..viewable import Viewable
from ..widgets.indicators import Number
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)


class NativeDefaultTheme(DefaultTheme):
    ""

class NativeDarkTheme(DarkTheme):

    modifiers = {
        Number: {
            'default_color': 'white'
        }
    }


class Native(Design):

    modifiers = {
        Viewable: {
            'stylesheets': [Inherit, f'{CDN_DIST}bundled/theme/native.css']
        }
    }

    _themes = {
        'dark': NativeDarkTheme,
        'default': NativeDefaultTheme
    }
