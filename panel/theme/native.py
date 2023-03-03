from __future__ import annotations

from ..viewable import Viewable
from ..widgets.indicators import Number
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)


class NativeDefaultTheme(DefaultTheme):
    ""

class NativeDarkTheme(DarkTheme):

    _modifiers = {
        Number: {
            'default_color': 'white'
        }
    }


class Native(Design):

    _modifiers = {
        Viewable: {
            'stylesheets': [Inherit, 'css/native.css']
        }
    }

    _themes = {
        'dark': NativeDarkTheme,
        'default': NativeDefaultTheme
    }
