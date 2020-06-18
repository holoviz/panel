"""Bootstrap inspired Alerts

See https://getbootstrap.com/docs/4.0/components/alerts/
"""
import param

from panel.pane.markup import Markdown

ALERT_TYPES = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]


class Alert(Markdown):
    """
    An Alert that renders Markdown

    - CSS Styling is done via the classes `alert` and `alert-TYPE`, where TYPE is the alert_type.
    - sizing_mode is set to `stretch_width` by default
    """

    alert_type = param.ObjectSelector("primary", objects=ALERT_TYPES)

    @classmethod
    def applies(cls, obj):
        priority = Markdown.applies(obj)
        return 0 if priority else False

    def __init__(self, text, **kwargs):
        if "margin" not in kwargs:
            kwargs["margin"] = (0, 0, 25, 0)
        if "sizing_mode" not in kwargs:
            kwargs["sizing_mode"] = "stretch_width"
        super().__init__(text, **kwargs)
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
