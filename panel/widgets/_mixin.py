from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

import param

from bokeh.models import Tooltip as BkTooltip

from .base import Widget
from .indicators import TooltipIcon


class TooltipMixin(Widget):

    __abstract = True

    description = param.ClassSelector(default=None, class_=(str, BkTooltip, TooltipIcon), doc="""
        The description in the tooltip.""")

    description_delay = param.Integer(default=500, doc="""
        Delay (in milliseconds) to display the tooltip after the cursor has
        hovered over the Button, default is 500ms.""")

    _rename: ClassVar[Mapping[str, str | None]]  = {
        'description': 'tooltip', 'description_delay': 'tooltip_delay'
    }

    def _process_param_change(self, params) -> dict[str, Any]:
        desc = params.get('description')
        if isinstance(desc, TooltipIcon):
            params['description'] = TooltipIcon.value
        if isinstance(desc, str):
            params['description'] = BkTooltip(content=desc, position='right')
        return super()._process_param_change(params)
