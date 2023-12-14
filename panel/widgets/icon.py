from typing import ClassVar, List, Mapping

import param

from ..io.resources import CDN_DIST
from ..models import ToggleIcon as _PnToggleIcon
from .base import Widget


class ToggleIcon(Widget):

    icon_name = param.String(default='heart', doc="""
        The name of the icon to display.""")

    active_icon_name = param.String(default='', doc="""
        The name of the icon to display when toggled.""")

    value = param.Boolean(default=False, doc="""
        Whether the icon is toggled on or off.""")

    _widget_type = _PnToggleIcon

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'name', 'button_style': None}

    _stylesheets: ClassVar[List[str]] = [f'{CDN_DIST}css/icon.css']

    def __init__(self, **params):
        super().__init__(**params)
        if not self.icon_name:
            raise ValueError('The icon_name parameter must not be empty.')
