from __future__ import annotations

from typing import ClassVar, List, Mapping

import param

from ..io.resources import CDN_DIST
from ..models import ToggleIcon as _PnToggleIcon
from .base import Widget


class ToggleIcon(Widget):

    active_icon = param.String(default='', doc="""
        The name of the icon to display when toggled from
        tabler-icons.io](https://tabler-icons.io)/ or an SVG.""")

    icon = param.String(default='heart', doc="""
        The name of the icon to display from
        [tabler-icons.io](https://tabler-icons.io)/ or an SVG.""")

    size = param.String(default=None, doc="""
        An explicit size specified as a CSS font-size, e.g. '1.5em' or '20px'.""")

    value = param.Boolean(default=False, doc="""
        Whether the icon is toggled on or off.""")

    _widget_type = _PnToggleIcon

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'name', 'button_style': None}

    _stylesheets: ClassVar[List[str]] = [f'{CDN_DIST}css/icon.css']

    def __init__(self, **params):
        super().__init__(**params)

    @param.depends("icon", "active_icon", watch=True, on_init=True)
    def _update_icon(self):
        if not self.icon:
            raise ValueError('The icon parameter must not be empty.')

        icon_is_svg = self.icon.startswith('<svg')
        if icon_is_svg and not self.active_icon:
            raise ValueError('The active_icon parameter must not be empty if icon is an SVG.')
