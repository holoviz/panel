"""We test that new widgets like wired or material has the same parameters as the
corresponding panel original widgets in order for them to be useable via pn.Param"""
import pytest

import panel as pn
from panel.components import wired

PARAMETERS_NOT_TO_TEST = {
    pn.widgets.FloatSlider: {"orientation", 'bar_color', 'callback_throttle', 'tooltips', 'value_throttled', 'callback_policy', 'direction', 'show_value'},
}

@pytest.mark.parametrize(["base", "target"], [
    (pn.widgets.Checkbox, wired.Checkbox),
    (pn.widgets.DatePicker, wired.DatePicker),
    (pn.widgets.FloatSlider, wired.FloatSlider),
    (pn.widgets.IntSlider, wired.IntSlider),
    (pn.widgets.LiteralInput, wired.LiteralInput),
    (pn.widgets.Select, wired.Select),
    (pn.widgets.TextInput, wired.TextInput),
])
def test_widget(base, target):
    parameters = set(base.param.objects()) - set(pn.widgets.Widget.param.objects())
    if base in PARAMETERS_NOT_TO_TEST:
        parameters = parameters - PARAMETERS_NOT_TO_TEST[base]
    for parameter in parameters:
        assert hasattr(target, parameter), parameter
        assert isinstance(target.param[parameter], type(base.param[parameter])), parameter
        assert base.param[parameter].default == target.param[parameter].default, parameter
