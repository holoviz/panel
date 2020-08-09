"""In this module we test the functionality of the alerts"""
import pytest

import panel as pn

from panel.pane import Alert
from panel.pane.alert import ALERT_TYPES


def test_constructor():
    """Test that an Alert can be instantiated"""
    alert = Alert(text="This is some text")
    # pylint: disable=no-member
    assert set(alert.css_classes) == {"alert", f"alert-{Alert.param.alert_type.default}"}
    # pylint: enable=no-member


@pytest.mark.parametrize(["alert_type"], [(alert_type,) for alert_type in ALERT_TYPES])
def test_alert_type_change(alert_type):
    """Test that an alert can change alert_type"""
    alert = Alert(text="This is some text")

    alert.alert_type = alert_type
    assert set(alert.css_classes) == {"alert", f"alert-{alert_type}"}

def test_existing_css_classes():
    """Test that an alert can change alert_type"""
    alert = Alert(text="This is some text", css_classes=["important"])
    assert set(alert.css_classes) == {"alert", f"alert-{Alert.param.alert_type.default}", "important"}

    alert.alert_type="info"
    assert set(alert.css_classes) == {"alert", "alert-info", "important"}


def test_all_view():
    """Test that we can construct and view all Alerts"""
    alerts = []
    for alert_type in ALERT_TYPES:
        text = f"""\
            This is a **{alert_type}** alert with [an example link](https://panel.holoviz.org/).
            Give it a click if you like."""
        alert = Alert(text=text, alert_type=alert_type)
        alerts.append(alert)

        assert "alert" in alert.css_classes
        assert f"alert-{alert_type}" in alert.css_classes

    return pn.Column(*alerts, sizing_mode="stretch_width")


if __name__.startswith("bk"):
    test_all_view().servable()
