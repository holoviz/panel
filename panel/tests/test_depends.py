import pytest

from panel.depends import bind, transform_dependency
from panel.pane import panel
from panel.param import ParamFunction
from panel.widgets import IntSlider


def test_transform_dependency():
    widget = IntSlider()
    assert transform_dependency(widget) is widget.param.value


def test_bind_param_to_arg():
    widget = IntSlider(value=0)

    def add1(value):
        return value + 1

    bound_function = bind(add1, widget.param.value)

    assert bound_function() == 1

    widget.value = 1

    assert bound_function() == 2

    with pytest.raises(TypeError):
        bound_function(1)


def test_bind_widget_to_arg():
    widget = IntSlider(value=0)

    def add1(value):
        return value + 1

    bound_function = bind(add1, widget)

    assert bound_function() == 1

    widget.value = 1

    assert bound_function() == 2

    with pytest.raises(TypeError):
        bound_function(1)


def test_bind_constant_to_arg():
    def add1(value):
        return value + 1

    bound_function = bind(add1, 1)

    assert bound_function() == 2

    with pytest.raises(TypeError):
        bound_function(1)


def test_bind_widget_to_kwarg():
    widget = IntSlider(value=0)

    def add1(value):
        return value + 1

    bound_function = bind(add1, value=widget)

    assert bound_function() == 1

    widget.value = 1

    assert bound_function() == 2

    with pytest.raises(TypeError):
        bound_function(1)


def test_bind_two_widget_arg_with_remaining_arg():
    widget = IntSlider(value=0)

    def add(value, value2):
        return value + value2

    bound_function = bind(add, widget)

    assert bound_function(1) == 1

    widget.value = 1

    assert bound_function(2) == 3
    assert bound_function(value2=3) == 4


def test_bind_two_widgets_as_kwargs():
    widget = IntSlider(value=0)
    widget2 = IntSlider(value=1)

    def add(value, value2):
        return value + value2

    bound_function = bind(add, value=widget, value2=widget2)

    assert bound_function() == 1

    widget.value = 1

    assert bound_function() == 2

    widget2.value = 2

    assert bound_function() == 3

    with pytest.raises(TypeError):
        bound_function(1, 2)

    assert bound_function(value2=5) == 6


def test_bind_bound_function_to_arg():
    widget = IntSlider(value=1)

    def add1(value):
        return value + 1

    def divide(value):
        return value / 2

    bound_function = bind(divide, bind(add1, widget.param.value))

    assert bound_function() == 1

    widget.value = 3

    assert bound_function() == 2


def test_bind_bound_function_to_kwarg():
    widget = IntSlider(value=1)

    def add1(value):
        return value + 1

    def divide(divisor=2, value=0):
        return value / divisor

    bound_function = bind(divide, value=bind(add1, widget.param.value))

    assert bound_function() == 1

    widget.value = 3

    assert bound_function() == 2


def test_bind_bare_emits_warning(caplog):

    def foo():
        return 'bar'

    ParamFunction(foo)

    # Emits a Param warning
    panel(bind(foo))

    found = False
    for log_record in caplog.records:
        if (log_record.levelname == 'WARNING' and
           "The function 'foo' does not have any dependencies and will never update" in log_record.message):
            found = True
    assert found
