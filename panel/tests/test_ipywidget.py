"""We test that we can work with Ipywidgets and AnyWidgets via Parameters or Reactive values
instead of Traitlets observer pattern.

The purpose is to enable Panel users to easily use Ipywidgets using familiar APIs.
"""

import pytest

pytest.importorskip("ipywidgets")

import param
import pytest

from ipywidgets import DOMWidget, register
from traitlets import Float, Int, Unicode

from panel.pane import IPyWidget
from panel.viewable import Layoutable, Viewer
from panel.wrappers.ipywidget import (
    ModelWrapper, WidgetViewer, _get_public_and_relevant_trait_names,
    create_parameterized, create_rx, create_viewer,
)


@register
class ExampleWidget(DOMWidget):
    _view_name = Unicode("ExampleIpyWidgetView").tag(sync=True)
    _view_module = Unicode("example_ipywidget").tag(sync=True)
    _view_module_version = Unicode("0.1.0").tag(sync=True)

    name = Unicode("Default Name").tag(description="A string trait")
    age = Int(0).tag(description="An integer trait")
    weight = Float(0.0).tag(description="A float trait")
    read_only = Unicode("A Value", read_only=True)


@pytest.fixture
def widget():
    return ExampleWidget(name="A", age=1, weight=1.1)

def _assert_is_synced(viewer, widget):
    # widget synced to viewer
    widget.name = "B"
    widget.age = 2
    widget.weight = 2.2
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight

    # widget synced to viewer
    with param.edit_constant(viewer):
        viewer.name = "C"
    viewer.age = 3
    viewer.weight = 3.3
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight

def test_create_parameterized(widget):
    viewer = create_parameterized(widget)

    assert {"name", "age", "weight"} <= set(viewer.param)

    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.weight == widget.weight

def test_create_parameterized_readonly(widget):
    parameterized = create_parameterized(widget, names=("read_only",))
    parameterized.read_only = "Some other value"
    assert widget.read_only != "Some other value"


def test_create_parameterized_is_synced(widget):
    viewer = create_parameterized(widget)

    assert viewer.name == widget.name == "A"
    assert viewer.age == widget.age == 1
    assert viewer.weight == widget.weight == 1.1

    _assert_is_synced(viewer, widget)


def test_create_parameterized_names_tuple(widget):
    viewer = create_parameterized(widget, names=("name", "age"))

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


def test_create_parameterized_bases(widget):
    class ExampleParameterized(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(0, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = create_parameterized(widget, bases=ExampleParameterized)
    assert isinstance(viewer, ExampleParameterized)
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(viewer.param)

    assert viewer.name == widget.name == "A"
    assert viewer.age == widget.age == ExampleParameterized.param.age.default

    # widget synced to viewer
    widget.name = "B"
    widget.age = 2
    assert viewer.name == widget.name
    assert viewer.age == widget.age

    # widget synced to viewer
    with param.edit_constant(viewer):
        viewer.name = "C"
    viewer.age = 3
    viewer.weight = 3.3
    assert viewer.name == widget.name
    assert viewer.age == widget.age

def test_create_parameterized_names_dict(widget):
    viewer = create_parameterized(widget, names={"name": "xname", "age": "xage"})

    assert {"xname", "xage"} <= set(viewer.param)
    assert "weight" not in set(viewer.param)

    assert viewer.xname == widget.name
    assert viewer.xage == widget.age

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert viewer.xname == widget.name
    assert viewer.xage == widget.age

    # widget synced to viewer
    viewer.xname = "C"
    viewer.xage = 3
    assert viewer.xname == widget.name
    assert viewer.xage == widget.age


def test_create_viewer(widget):
    viewer = create_viewer(widget)

    assert isinstance(viewer, Layoutable)
    assert isinstance(viewer, Viewer)

    component = viewer.__panel__()
    assert isinstance(component, IPyWidget)

    viewer.sizing_mode = "stretch_width"
    assert viewer.sizing_mode == component.sizing_mode

def test_create_viewer_names_and_kwargs(widget):
    viewer = create_viewer(widget, names=("name", "age"), sizing_mode="stretch_width")
    assert viewer.__panel__().sizing_mode == "stretch_width"


def test_create_viewer_bases(widget):

    class ExampleParameterized(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(0, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = create_viewer(widget, bases=ExampleParameterized)

    assert viewer.name == widget.name == "A"
    assert viewer.age == widget.age == 0
    assert viewer.weight == widget.weight == 1.1

    _assert_is_synced(viewer, widget)


def test_to_rx_all_public_and_relevant(widget):
    rxs = create_rx(widget)

    names = _get_public_and_relevant_trait_names(widget)
    for name, rx in zip(names, rxs):
        assert isinstance(rx, param.reactive.rx)
        assert rx.rx.value == getattr(widget, name)


def test_to_rx_all_custom(widget):
    age, weight, name = create_rx(widget, "age", "weight", "name")
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


def test_to_rx_subset(widget):
    name, age = create_rx(widget, "name", "age")
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


def test_to_rx_single(widget):
    age = create_rx(widget, "age")
    assert isinstance(age, param.reactive.rx)

    assert age.rx.value == widget.age

    # widget synced to reactive
    widget.age = 2
    assert age.rx.value == widget.age

    # reactive synced to viewer
    age.rx.value = 3
    assert age.rx.value == widget.age


def test_wrap_model_names_tuple():
    class ExampleWrapper(ModelWrapper):
        _model_class = ExampleWidget
        _names = ("name", "age")

    wrapper = ExampleWrapper(age=100)

    widget = wrapper.model
    assert wrapper.name == widget.name == "Default Name"
    assert wrapper.age == widget.age == 100

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age

    # widget synced to viewer
    wrapper.name = "C"
    wrapper.age = 3
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age


def test_wrap_model_names_dict():
    class ExampleWrapper(ModelWrapper):
        _model_class = ExampleWidget
        _names = {"name": "xname", "age": "xage"}

    wrapper = ExampleWrapper(xage=100)

    widget = wrapper.model
    assert wrapper.xname == widget.name == "Default Name"
    assert wrapper.xage == widget.age == 100

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert wrapper.xname == widget.name
    assert wrapper.xage == widget.age

    # widget synced to viewer
    wrapper.xname = "C"
    wrapper.xage = 3
    assert wrapper.xname == widget.name
    assert wrapper.xage == widget.age


def test_widget_viewer_from_class_and_no_names():
    class ExampleViewer(WidgetViewer):
        _model_class = ExampleWidget

    wrapper = ExampleViewer(age=100)
    assert {"weight", "age", "name", "design", "tags"} <= set(wrapper.param)

    widget = wrapper.model
    assert wrapper.name == widget.name == "Default Name"
    assert wrapper.age == widget.age == 100

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age

    # widget synced to viewer
    wrapper.name = "C"
    wrapper.age = 3
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age


def test_widget_viewer_from_class_and_list_names():
    class ExampleViewer(WidgetViewer):
        _model_class = ExampleWidget
        _names = ["name", "age"]

    wrapper = ExampleViewer(age=100)

    widget = wrapper.model
    assert wrapper.name == widget.name == "Default Name"
    assert wrapper.age == widget.age == 100

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age

    # widget synced to viewer
    wrapper.name = "C"
    wrapper.age = 3
    assert wrapper.name == widget.name
    assert wrapper.age == widget.age


def test_widget_viewer_from_class_and_dict_names():
    class ExampleViewer(WidgetViewer):
        _model_class = ExampleWidget
        _names = {"name": "xname", "age": "xage"}

    wrapper = ExampleViewer(xage=100)

    widget = wrapper.model
    assert wrapper.xname == widget.name == "Default Name"
    assert wrapper.xage == widget.age == 100

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    assert wrapper.xname == widget.name
    assert wrapper.xage == widget.age

    # widget synced to viewer
    wrapper.xname = "C"
    wrapper.xage = 3
    assert wrapper.xname == widget.name
    assert wrapper.xage == widget.age


def test_widget_viewer_from_instance():
    class ExampleWidgetViewer(WidgetViewer):
        _model_class = ExampleWidget

        name = param.String("default", doc="A string parameter")
        age = param.Integer(3, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = ExampleWidgetViewer(height=500, sizing_mode="stretch_width")
    widget = viewer.model
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(viewer.param)

    assert viewer.name == widget.name == "Default Name"
    assert viewer.age == widget.age == 3
    assert viewer.weight == widget.weight == 0.0

    _assert_is_synced(viewer, widget)


def test_widget_viewer_child_class(widget):
    class ExampleWidgetViewer(WidgetViewer):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(3, bounds=(0, 10))
        not_trait = param.Parameter(-2.0)

    viewer = ExampleWidgetViewer(model=widget, height=500, sizing_mode="stretch_width")
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(viewer.param)

    assert viewer.name == widget.name == "A"
    assert viewer.age == widget.age == 3
    assert viewer.weight == widget.weight == 1.1

    _assert_is_synced(viewer, widget)
