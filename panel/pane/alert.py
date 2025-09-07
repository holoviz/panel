"""
Bootstrap inspired Alerts

See https://getbootstrap.com/docs/4.0/components/alerts/
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

import param

from ..io.resources import CDN_DIST
from .markup import Markdown

ALERT_TYPES = [
    "primary", "secondary", "success", "danger",
    "warning", "info", "light", "dark"
]


class Alert(Markdown):
    """
    The `Alert` pane allows providing contextual feedback messages for typical
    user actions. The Alert supports markdown strings.

    Reference: https://panel.holoviz.org/reference/panes/Alert.html

    :Example:

    >>> Alert('Some important message', alert_type='warning')
    """

    alert_type = param.Selector(default="primary", objects=ALERT_TYPES, doc="""
        The type of Alert and one of 'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'light', 'dark'.""")

    priority: ClassVar[float | bool | None] = 0

    _rename: ClassVar[Mapping[str, str | None]] = {'alert_type': None}

    _stylesheets: ClassVar[list[str]] = [
        f'{CDN_DIST}css/alerts.css'
    ]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        priority = Markdown.applies(obj)
        return 0 if priority else False

    def __init__(self, object=None, **params):
        if "sizing_mode" not in params and "width" not in params:
            params["sizing_mode"] = "stretch_width"
        super().__init__(object, **params)

    def _process_param_change(self, params):
        if 'css_classes' in params or 'alert_type' in params:
            params['css_classes'] = self.css_classes + [
                'alert', f'alert-{self.alert_type}'
            ]
        return super()._process_param_change(params)
