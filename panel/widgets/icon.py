from typing import ClassVar, List, Mapping

import param

from ..io.resources import CDN_DIST
from ..models import ToggleIcon as _PnToggleIcon
from .widget import Widget


class ToggleIcon(Widget):

    icon_name = param.String(default='heart', doc="""
        The name of the icon to display.""")

    value = param.Boolean(default=False, doc="""
        Whether the icon is toggled on or off.""")

    _widget_type = _PnToggleIcon

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'name', 'button_style': None}

    _stylesheets: ClassVar[List[str]] = [f'{CDN_DIST}css/button.css']

    __abstract = True
