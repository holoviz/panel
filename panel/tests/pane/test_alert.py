"""In this module we test the functionality of the alerts"""
import pytest

import panel as pn

from panel.pane import Alert
from panel.pane.alert import ALERT_TYPES


@pytest.mark.parametrize(["alert_type"], [(alert_type,) for alert_type in ALERT_TYPES])
def test_alert_type_change(alert_type, document, comm):
    """Test that an alert can change alert_type"""
    alert = Alert("This is some text")

    model = alert.get_root(document, comm)

    alert.alert_type = alert_type
    assert set(model.css_classes) == {"alert", f"alert-{alert_type}", "markdown"}


def manualtest_all_view():
    """Test that we can construct and view all Alerts"""
    alerts = []
    for alert_type in ALERT_TYPES:
        text = f"""\
            This is a **{alert_type}** alert with [an example link](https://panel.holoviz.org/).
            Give it a click if you like."""
        alert = Alert(text, alert_type=alert_type)
        alert_app = pn.Column(
            alert,
            pn.Param(
                alert,
                parameters=["object", "alert_type"],
                widgets={"object":
                pn.widgets.TextAreaInput},
            ),
        )
        alerts.append(alert_app)

        assert "alert" in alert.css_classes
        assert f"alert-{alert_type}" in alert.css_classes

    return pn.Column(*alerts, margin=50)


if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    manualtest_all_view().servable()
