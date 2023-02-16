from __future__ import annotations

from ..viewable import Viewable
from .base import Design, Inherit


class Native(Design):

    _modifiers = {
        Viewable: {
            'stylesheets': [Inherit, 'css/native.css']
        }
    }
