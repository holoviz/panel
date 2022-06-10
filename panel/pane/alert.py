"""
Bootstrap inspired Alerts

See https://getbootstrap.com/docs/4.0/components/alerts/
"""
from __future__ import annotations

from typing import Any, ClassVar, Mapping

import param

from panel.pane.markup import Markdown

ALERT_TYPES = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]


class Alert(Markdown):
    """
    The `Alert` pane allows providing contextual feedback messages for typical
    user actions. The Alert supports markdown strings.

    Reference: https://panel.holoviz.org/reference/panes/Alert.html

    :Example:

    >>> Alert('Some important message', alert_type='warning')
    """

    alert_type = param.ObjectSelector("primary", objects=ALERT_TYPES)

    priority: ClassVar[float | bool | None] = 0

    _rename: ClassVar[Mapping[str, str | None]] = dict(Markdown._rename, alert_type=None)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        priority = Markdown.applies(obj)
        return 0 if priority else False

    def __init__(self, object=None, **params):
        if "margin" not in params:
            params["margin"] = (0, 0, 25, 0)
        if "sizing_mode" not in params:
            params["sizing_mode"] = "stretch_width"
        super().__init__(object, **params)
        self._set_css_classes()

    @param.depends("alert_type", watch=True)
    def _set_css_classes(self):
        css_classes = []
        if self.css_classes:
            for class_ in self.css_classes:
                if class_ != "alert" and not class_.startswith("alert-"):
                    css_classes.append(class_)

        css_classes.append("alert")
        css_classes.append(f"alert-{self.alert_type}")
        self.css_classes = css_classes
