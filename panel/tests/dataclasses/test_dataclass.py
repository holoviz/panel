"""
Tests for utilities that allow us to wrap dataclass like class and
instances via familiar APIs like watch, bind, depends and rx."
"""
from typing import Callable, Literal

import param
import pytest

import panel as pn

from panel._dataclasses.pydantic import PydanticUtils
from panel.dataclass import (
    ModelParameterized, ModelViewer, _get_utils, sync_with_parameterized,
    to_parameterized, to_rx, to_viewer,
)
from panel.viewable import Layoutable, Viewer

PydanticUtils._is_testing =True

def get_traitlets_example_model():
    import traitlets

    from ipywidgets import DOMWidget, register

    @register
    class TraitletsExampleModel(DOMWidget):
        _view_name = traitlets.Unicode("ExampleIpyWidgetView").tag(sync=True)
        _view_module = traitlets.Unicode("example_ipywidget").tag(sync=True)
        _view_module_version = traitlets.Unicode("0.1.0").tag(sync=True)

        name = traitlets.Unicode("Default Name").tag(description="A string trait")
        age = traitlets.Int(0).tag(description="An integer trait")
        weight = traitlets.Float(0.0).tag(description="A float trait")
        read_only = traitlets.Unicode("A Value", read_only=True)
        bool_field = traitlets.Bool(False)
        bytes_field = traitlets.Bytes(b"abc")
        callable_field = traitlets.Callable(str)
        dict_field = traitlets.Dict({"a": 1, "b": 2})
        literal_field = traitlets.Enum(["a", "b", "c"], default_value="a")
        list_field = traitlets.List([1, 2, 3])
        tuple_field = traitlets.Tuple((1, 2, 3))

    return TraitletsExampleModel


def get_pydantic_example_model():
    from pydantic import BaseModel



    class PydanticExampleModel(BaseModel):
        name: str = "Default Name"
        age: int = 0
        weight: float = 0.0
        read_only: str = "A Value" # Cannot make constant
        bool_field: bool = False
        bytes_field: bytes = b"abc"
        callable_field: Callable = str
        dict_field: dict = {"a": 1, "b": 2}
        literal_field: Literal['a','b','c'] = 'a'
        list_field: list = [1, 2, 3]
        tuple_field: tuple = (1, 2, 3)


    return PydanticExampleModel



EXAMPLE_MODELS = [ ]
for get_example_model in [get_traitlets_example_model, get_pydantic_example_model]:
    try:
        EXAMPLE_MODELS.append(get_example_model())
    except ImportError:
        pass


@pytest.fixture(params=EXAMPLE_MODELS)
def model_class(request):
    return request.param

@pytest.fixture()
def model(model_class):
    return model_class(name="A", age=1, weight=1.1)

@pytest.fixture()
def utils(model):
    return _get_utils(model)

@pytest.fixture
def can_observe_field(utils):
    return utils.can_observe_field

@pytest.fixture
def supports_constant_fields(utils):
    return utils.supports_constant_fields

def _assert_is_synced(parameterized, model, can_observe_field):
    if can_observe_field:
        # sync: model -> parameterized
        model.name = "B"
        model.age = 2
        model.weight = 2.2
        assert parameterized.name == model.name
        assert parameterized.age == model.age
        assert parameterized.weight == model.weight

    # parameterized synced to model
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    parameterized.weight = 3.3
    assert parameterized.name == model.name
    assert parameterized.age == model.age
    assert parameterized.weight == model.weight

def test_sync_with_parameterized(model, can_observe_field):
    class ExampleParameterized(param.Parameterized):
        name = param.String(default="Default Name")
        age = param.Integer(default=0)
        weight = param.Number(default=0.0)

    parameterized = ExampleParameterized()
    sync_with_parameterized(model, parameterized)

    _assert_is_synced(parameterized, model, can_observe_field)

def test_to_parameterized(model):
    viewer = to_parameterized(model)

    assert {"name", "age", "weight"} <= set(viewer.param)

    assert viewer.name == model.name
    assert viewer.age == model.age
    assert viewer.weight == model.weight


def test_to_parameterized_readonly(model, supports_constant_fields):
    if not supports_constant_fields:
        pytest.skip(f"Constant fields not supported for {type(model)}")

    parameterized = to_parameterized(model, names=("read_only",))
    with param.edit_constant(parameterized):
        parameterized.read_only = "Some other value"
    assert model.read_only != "Some other value"


def test_to_parameterized_is_synced(model, can_observe_field):
    viewer = to_parameterized(model)

    assert viewer.name == model.name == "A"
    assert viewer.age == model.age == 1
    assert viewer.weight == model.weight == 1.1

    _assert_is_synced(viewer, model, can_observe_field)


def test_to_parameterized_names_tuple(model, can_observe_field):
    parameterized = to_parameterized(model, names=("name", "age"))

    assert {"name", "age"} <= set(parameterized.param)
    assert "weight" not in set(parameterized.param)

    assert parameterized.name == model.name
    assert parameterized.age == model.age

    if can_observe_field:
        # model synced to parameterized
        model.name = "B"
        model.age = 2
        assert parameterized.name == model.name
        assert parameterized.age == model.age

    # parameterized synced to model
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    assert parameterized.name == model.name
    assert parameterized.age == model.age


def test_to_parameterized_bases(model, can_observe_field):
    class ExampleParameterized(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(0, bounds=(0, 10))
        not_trait = param.Parameter(1)

    parameterized = to_parameterized(model, bases=ExampleParameterized)
    assert isinstance(parameterized, ExampleParameterized)
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(parameterized.param)

    assert parameterized.name == model.name == "A"
    assert parameterized.age == model.age == ExampleParameterized.param.age.default

    if can_observe_field:
        # sync: model -> parameterized
        model.name = "B"
        model.age = 2
        assert parameterized.name == model.name
        assert parameterized.age == model.age

    # sync: parameterized -> model
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    parameterized.weight = 3.3
    assert parameterized.name == model.name
    assert parameterized.age == model.age


def test_to_parameterized_names_dict(model, can_observe_field):
    parameterized = to_parameterized(model, names={"name": "xname", "age": "xage"})

    assert {"xname", "xage"} <= set(parameterized.param)
    assert "weight" not in set(parameterized.param)

    assert parameterized.xname == model.name
    assert parameterized.xage == model.age

    if can_observe_field:
        # sync: model -> parameterized
        model.name = "B"
        model.age = 2
        assert parameterized.xname == model.name
        assert parameterized.xage == model.age

    # sync: parameterized -> model
    parameterized.xname = "C"
    parameterized.xage = 3
    assert parameterized.xname == model.name
    assert parameterized.xage == model.age


def test_to_viewer(model):
    viewer = to_viewer(model)

    assert isinstance(viewer, Layoutable)
    assert isinstance(viewer, Viewer)

    component = viewer.__panel__()
    assert component
    # Make sure we can view the component
    pn.panel(component)

    # Todo: Move this part to test_ipywidget
    viewer.sizing_mode = "stretch_width"
    assert viewer.sizing_mode == component.sizing_mode


def test_to_viewer_names_and_kwargs(model):
    viewer = to_viewer(model, names=("name", "age"), sizing_mode="stretch_width")
    assert viewer.__panel__().sizing_mode == "stretch_width"


def test_to_viewer_bases(model, can_observe_field):

    class ExampleParameterized(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(0, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = to_viewer(model, bases=ExampleParameterized)

    assert viewer.name == model.name == "A"
    assert viewer.age == model.age == 0
    assert viewer.weight == model.weight == 1.1

    _assert_is_synced(viewer, model, can_observe_field)


def test_to_rx_all_public_and_relevant(model):
    rxs = to_rx(model)

    names = _get_utils(model).get_public_and_relevant_field_names(model)
    for name, rx in zip(names, rxs):
        assert isinstance(rx, param.reactive.rx)
        assert rx.rx.value == getattr(model, name)


def test_to_rx_all_custom(model, can_observe_field):
    age, weight, name = to_rx(model, "age", "weight", "name")
    assert isinstance(name, param.reactive.rx)
    assert isinstance(age, param.reactive.rx)
    assert isinstance(weight, param.reactive.rx)

    assert name.rx.value == model.name
    assert age.rx.value == model.age
    assert weight.rx.value == model.weight

    if can_observe_field:
        # model synced to reactive
        model.name = "B"
        model.age = 2
        model.weight = 2.2
        assert name.rx.value == model.name
        assert age.rx.value == model.age
        assert weight.rx.value == model.weight

    # reactive synced to viewer
    name.rx.value = "C"
    age.rx.value = 3
    weight.rx.value = 3.3
    assert name.rx.value == model.name
    assert age.rx.value == model.age
    assert weight.rx.value == model.weight


def test_to_rx_subset(model, can_observe_field):
    name, age = to_rx(model, "name", "age")
    assert isinstance(name, param.reactive.rx)
    assert isinstance(age, param.reactive.rx)

    assert name.rx.value == model.name
    assert age.rx.value == model.age

    if can_observe_field:
        # model synced to reactive
        model.name = "B"
        model.age = 2
        assert name.rx.value == model.name
        assert age.rx.value == model.age

    # reactive synced to viewer
    name.rx.value = "C"
    age.rx.value = 3
    assert name.rx.value == model.name
    assert age.rx.value == model.age


def test_to_rx_single(model, can_observe_field):
    age = to_rx(model, "age")
    assert isinstance(age, param.reactive.rx)

    assert age.rx.value == model.age

    if can_observe_field:
        # sync: model -> rx
        model.age = 2
        assert age.rx.value == model.age

    # sync: rx -> model
    age.rx.value = 3
    assert age.rx.value == model.age


def test_wrap_model_names_tuple(model_class, can_observe_field):
    class ExampleWrapper(ModelParameterized):
        _model_class = model_class
        _model_names = ("name", "age")

    parameterized = ExampleWrapper(age=100)

    widget = parameterized.model
    assert parameterized.name == widget.name == "Default Name"
    assert parameterized.age == widget.age == 100

    if can_observe_field:
        # sync: model -> parameterized
        widget.name = "B"
        widget.age = 2
        assert parameterized.name == widget.name
        assert parameterized.age == widget.age

    # sync: parameterized -> model
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    assert parameterized.name == widget.name
    assert parameterized.age == widget.age


def test_wrap_model_names_dict(model_class, can_observe_field):
    class ExampleWrapper(ModelParameterized):
        _model_class = model_class
        _model_names = {"name": "xname", "age": "xage"}

    parameterized = ExampleWrapper(xage=100)

    widget = parameterized.model
    assert parameterized.xname == widget.name == "Default Name"
    assert parameterized.xage == widget.age == 100

    if can_observe_field:
        # sync: model -> parameterized
        widget.name = "B"
        widget.age = 2
        assert parameterized.xname == widget.name
        assert parameterized.xage == widget.age

    # widget synced to viewer
    parameterized.xname = "C"
    parameterized.xage = 3
    assert parameterized.xname == widget.name
    assert parameterized.xage == widget.age


def test_widget_viewer_from_class_and_no_names(model_class, can_observe_field):
    class ExampleViewer(ModelViewer):
        _model_class = model_class

    parameterized = ExampleViewer(age=100)
    assert {"weight", "age", "name", "design", "tags"} <= set(parameterized.param)

    widget = parameterized.model
    assert parameterized.name == widget.name == "Default Name"
    assert parameterized.age == widget.age == 100

    if can_observe_field:
        # sync: model -> parameterized
        widget.name = "B"
        widget.age = 2
        assert parameterized.name == widget.name
        assert parameterized.age == widget.age

    # widget synced to viewer
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    assert parameterized.name == widget.name
    assert parameterized.age == widget.age


def test_widget_viewer_from_class_and_list_names(model_class, can_observe_field):
    class ExampleViewer(ModelViewer):
        _model_class = model_class
        _model_names = ["name", "age"]

    parameterized = ExampleViewer(age=100)

    widget = parameterized.model
    assert parameterized.name == widget.name == "Default Name"
    assert parameterized.age == widget.age == 100

    if can_observe_field:
        # sync: model -> parameterized
        widget.name = "B"
        widget.age = 2
        assert parameterized.name == widget.name
        assert parameterized.age == widget.age

    # widget synced to viewer
    with param.edit_constant(parameterized):
        parameterized.name = "C"
    parameterized.age = 3
    assert parameterized.name == widget.name
    assert parameterized.age == widget.age


def test_widget_viewer_from_class_and_dict_names(model_class, can_observe_field):
    class ExampleViewer(ModelViewer):
        _model_class = model_class
        _model_names = {"name": "xname", "age": "xage"}

    parameterized = ExampleViewer(xage=100)

    widget = parameterized.model
    assert parameterized.xname == widget.name == "Default Name"
    assert parameterized.xage == widget.age == 100

    if can_observe_field:
        # sync: model -> parameterized
        widget.name = "B"
        widget.age = 2
        assert parameterized.xname == widget.name
        assert parameterized.xage == widget.age

    # widget synced to viewer
    parameterized.xname = "C"
    parameterized.xage = 3
    assert parameterized.xname == widget.name
    assert parameterized.xage == widget.age


def test_widget_viewer_from_instance(model_class, can_observe_field):
    class ExampleWidgetViewer(ModelViewer):
        _model_class = model_class

        name = param.String("default", doc="A string parameter")
        age = param.Integer(3, bounds=(0, 10))
        not_trait = param.Parameter(1)

    viewer = ExampleWidgetViewer(height=500, sizing_mode="stretch_width")
    widget = viewer.model
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(viewer.param)

    assert viewer.name == widget.name == "Default Name"
    assert viewer.age == widget.age == 3
    assert viewer.weight == widget.weight == 0.0

    _assert_is_synced(viewer, widget, can_observe_field)


def test_widget_viewer_child_class(model, can_observe_field):
    class ExampleWidgetViewer(ModelViewer):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(3, bounds=(0, 10))
        not_trait = param.Parameter(-2.0)

    viewer = ExampleWidgetViewer(model=model, height=500, sizing_mode="stretch_width")
    assert {"name", "age", "weight", "not_trait", "read_only"} <= set(viewer.param)

    assert viewer.name == model.name == "A"
    assert viewer.age == model.age == 3
    assert viewer.weight == model.weight == 1.1

    _assert_is_synced(viewer, model, can_observe_field)


def test_dont_sync_non_shared_parameter(model):
    class ExampleWidgetViewer(param.Parameterized):
        name = param.String("default", doc="A string parameter")
        age = param.Integer(3, bounds=(0, 10))

    parameterized = ExampleWidgetViewer()
    sync_with_parameterized(model=model, parameterized=parameterized)


def test_dont_sync_non_shared_trait(model):
    class ExampleWidgetViewer(param.Parameterized):
        wealth = param.Integer(3, bounds=(0, 10))

    parameterized = ExampleWidgetViewer()
    sync_with_parameterized(model=model, parameterized=parameterized, names=["wealth"])

def test_model_parameterized_parameters_added_to_instance_not_class(model):
    parameterized_all = ModelParameterized(
        model=model
    )

    parameterized_one = ModelParameterized(
        model=model, names=("age",)
    )

    assert set(parameterized_one.param) < set(parameterized_all.param)

def test_can_create_correct_parameter_type(model_class):
    class ExampleParameterized(ModelParameterized):
        _model_class = model_class

    parameterized = ExampleParameterized()

    assert isinstance(parameterized, param.Parameterized)
    assert isinstance(parameterized.param.name, param.String)
    assert isinstance(parameterized.param.age, param.Integer)
    assert isinstance(parameterized.param.weight, param.Number)
    assert isinstance(parameterized.param.bool_field, param.Boolean)
    assert isinstance(parameterized.param.list_field, param.List)
    assert isinstance(parameterized.param.tuple_field, param.Tuple)
    assert isinstance(parameterized.param.dict_field, param.Dict)
    assert isinstance(parameterized.param.bytes_field, param.Bytes)
    assert isinstance(parameterized.param.callable_field, param.Callable)
    assert isinstance(parameterized.param.literal_field, param.Selector)
