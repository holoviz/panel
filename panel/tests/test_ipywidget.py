"""We test that we can work with Ipywidgets and AnyWidgets via Parameters or Reactive values
instead of Traitlets observer pattern.

The purpose is to enable Panel users to easily use Ipywidgets using familiar APIs.
"""

import param

from traitlets import (
    Float, HasTraits, Int, Unicode,
)

import panel as pn

from panel.ipywidget import to_rx, to_viewer


class ExampleTraitlets(HasTraits):
    name = Unicode("Default Name").tag(description="A string trait")
    age = Int(0).tag(description="An integer trait")
    height = Float(0.0).tag(description="A float trait")


def test_to_viewer():
    widget = ExampleTraitlets(name="A", age=1, height=1.1)

    viewer = to_viewer(widget)

    assert isinstance(viewer, pn.viewable.Viewer)
    assert {"name", "age", "height"} == set(viewer.param.params)

    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.height == widget.height

    # widget synced to widget
    widget.name = "B"
    widget.age = 2
    widget.height = 2.2
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.height == widget.height

    # widget synced to viewer
    viewer.name = "C"
    viewer.age = 3
    viewer.height = 3.3
    assert viewer.name == widget.name
    assert viewer.age == widget.age
    assert viewer.height == widget.height

    component = viewer.__panel__()
    assert isinstance(component, pn.pane.IPyWidget)
    assert component.object == widget


def test_to_viewer_parameter_list():
    widget = ExampleTraitlets(name="A", age=1, height=1.1)

    viewer = to_viewer(widget, parameters=["name", "age"])

    assert isinstance(viewer, pn.viewable.Viewer)
    assert {"name", "age"} == set(viewer.param.params)

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

def test_to_viewer_kwargs():
    widget = ExampleTraitlets(name="A", age=1, height=1.1)

    viewer = to_viewer(widget, parameters=["name", "age"], sizing_mode="stretch_width")
    assert viewer.sizing_mode=="stretch_width"

def test_to_rx():
    widget = ExampleTraitlets(name="A", age=1, height=1.1)

    name, age, height = to_rx(widget)
    assert isinstance(name, param.rx)
    assert isinstance(age, param.rx)
    assert isinstance(height, param.rx)

    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert height.rx.value == widget.height

    # widget synced to reactive
    widget.name = "B"
    widget.age = 2
    widget.height = 2.2
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert height.rx.value == widget.height

    # reactive synced to viewer
    name.rx.value = "C"
    age.rx.value = 3
    height.rx.value = 3.3
    assert name.rx.value == widget.name
    assert age.rx.value == widget.age
    assert height.rx.value == widget.height


def test_to_rx_parameter_list():
    widget = ExampleTraitlets(name="A", age=1, height=1.1)

    name, age = to_rx(widget, parameters=["name", "age"])
    assert isinstance(name, param.rx)
    assert isinstance(age, param.rx)

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
