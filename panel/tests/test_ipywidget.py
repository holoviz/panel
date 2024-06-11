"""We test that we can work with Ipywidgets and AnyWidgets via Parameters or Reactive values
instead of Traitlets observer pattern.

The purpose is to enable Panel users to easily use Ipywidgets using familiar APIs.
"""

import param
import pytest

from ipywidgets import DOMWidget, register
from traitlets import Float, Int, Unicode

from panel.ipywidget import to_parameterized, to_rx, to_viewer
from panel.pane import IPyWidget
from panel.viewable import Layoutable, Viewer


@register
class ExampleIpyWidget(DOMWidget):
    _view_name = Unicode("ExampleIpyWidgetView").tag(sync=True)
    _view_module = Unicode("example_ipywidget").tag(sync=True)
    _view_module_version = Unicode("0.1.0").tag(sync=True)

    name = Unicode("Default Name").tag(description="A string trait")
    age = Int(0).tag(description="An integer trait")
    weight = Float(0.0).tag(description="A float trait")


@pytest.fixture
def widget():
    return ExampleIpyWidget(name="A", age=1, weight=1.1)


def test_to_parameterized(widget):
    viewer = to_parameterized(widget)

    assert {"name", "age", "weight"} <= set(viewer.param)

    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight


def test_to_parameterized_is_synced(widget):
    viewer = to_parameterized(widget)

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    widget.weight = 2.2
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight

    # widget synced to viewer
    viewer.name = "C"
    viewer.age = 3
    viewer.weight = 3.3
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight


def test_to_parameterized_parameter_list(widget):
    viewer = to_parameterized(widget, parameters=["name", "age"])

    assert {"name", "age"} <= set(viewer.param)
    assert "weight" not in set(viewer.param)

    assert viewer.name == widget.name
    assert viewer.age == widget.age

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert viewer.name == widget.name
    assert viewer.age == widget.age

    # widget synced to viewer
    viewer.name = "C"
    viewer.age = 3
    assert viewer.name == widget.name
    assert viewer.age == widget.age


def test_to_parameterized_bases(widget):

    class ExampleParameterized(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(0, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = to_parameterized(widget, bases=ExampleParameterized)
    assert isinstance(viewer, ExampleParameterized)
    assert {"name", "age", "weight", "not_trait"} <= set(viewer.param)

    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight


def test_to_viewer(widget):
    viewer = to_viewer(widget)

    assert isinstance(viewer, Layoutable)
    assert isinstance(viewer, Viewer)

    component = viewer.__panel__()
    assert isinstance(component, IPyWidget)

    viewer.sizing_mode = "stretch_width"
    assert viewer.sizing_mode == component.sizing_mode


def test_to_viewer_kwargs(widget):
    viewer = to_viewer(widget, parameters=["name", "age"], sizing_mode="stretch_width")
    assert viewer.__panel__().sizing_mode == "stretch_width"


def test_to_rx(widget):
    age, weight, name = to_rx(widget, parameters=["age", "weight", "name"])
    assert isinstance(name, param.reactive.rx)
    assert isinstance(age, param.reactive.rx)
    assert isinstance(weight, param.reactive.rx)

    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert weight.rx.value == widget.weight

    # widget synced to reactive
    widget.name = "B"
    widget.age = 2
    widget.weight = 2.2
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert weight.rx.value == widget.weight

    # reactive synced to viewer
    name.rx.value = "C"
    age.rx.value = 3
    weight.rx.value = 3.3
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert weight.rx.value == widget.weight


def test_to_rx_parameter_list(widget):
    name, age = to_rx(widget, parameters=["name", "age"])
    assert isinstance(name, param.reactive.rx)
    assert isinstance(age, param.reactive.rx)

    assert name.rx.value == widget.name
    assert age.rx.value == widget.age

    # widget synced to reactive
    widget.name = "B"
    widget.age = 2
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age

    # reactive synced to viewer
    name.rx.value = "C"
    age.rx.value = 3
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
