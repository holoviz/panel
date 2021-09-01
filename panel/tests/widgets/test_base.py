import param
import pytest

from panel.io import block_comm
from panel.layout import Row
from panel.links import CallbackGenerator
from panel.util import doc_event_obj
from panel.widgets import (
    CompositeWidget, Dial, FileDownload, FloatSlider, TextInput,
    Terminal, ToggleGroup, Tqdm, Widget
)
from panel.widgets.tables import BaseTable
from panel.tests.util import check_layoutable_properties

excluded = (
    BaseTable, CompositeWidget, Dial, FileDownload, ToggleGroup, Terminal,
    Tqdm
)

all_widgets = [
    w for w in param.concrete_descendents(Widget).values()
    if not w.__name__.startswith('_') and not issubclass(w, excluded)
]

@pytest.mark.parametrize('widget', all_widgets)
def test_widget_signature(widget):
    from inspect import signature
    parameters = signature(widget).parameters
    assert len(parameters) == 1


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_linkable_params(widget):
    w = widget()
    controls = w.controls(jslink=True)
    layout = Row(w, controls)

    try:
        CallbackGenerator.error = True
        layout.get_root()
    finally:
        CallbackGenerator.error = False


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_layout_properties(widget, document, comm):
    w = widget()
    model = w.get_root(document, comm)
    check_layoutable_properties(w, model)


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_disabled_properties(widget, document, comm):
    w = widget(disabled=True)

    model = w.get_root(document, comm)

    assert model.disabled == True
    model.disabled = False
    assert model.disabled == False


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_clone(widget):
    w = widget()
    clone = w.clone()

    assert ([(k, v) for k, v in sorted(w.param.get_param_values()) if k != 'name'] ==
            [(k, v) for k, v in sorted(clone.param.get_param_values()) if k != 'name'])


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_clone_override(widget):
    w = widget()
    clone = w.clone(width=50)

    assert ([(k, v) for k, v in sorted(w.param.get_param_values()) if k not in ['name', 'width']] ==
            [(k, v) for k, v in sorted(clone.param.get_param_values()) if k not in ['name', 'width']])
    assert clone.width == 50
    assert w.width is widget.width


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_model_cache_cleanup(widget, document, comm):
    w = widget()

    model = w.get_root(document, comm)

    assert model.ref['id'] in w._models
    assert w._models[model.ref['id']] == (model, None)

    w._cleanup(model)
    assert w._models == {}


def test_widget_triggers_events(document, comm):
    """
    Ensure widget events don't get swallowed in comm mode
    """
    text = TextInput(value='ABC', name='Text:')

    widget = text.get_root(document, comm=comm)
    document.add_root(widget)
    document.hold()

    # Simulate client side change
    event_obj = doc_event_obj(document)
    event_obj._held_events = event_obj._held_events[:-1]

    # Set new value
    with block_comm():
        text.value = '123'

    assert len(event_obj._held_events) == 1
    event = event_obj._held_events[0]
    assert event.attr == 'value'
    assert event.model is widget
    assert event.new == '123'


def test_widget_from_param_cls():
    class Test(param.Parameterized):

        a = param.Parameter()

    widget = TextInput.from_param(Test.param.a)
    assert isinstance(widget, TextInput)
    assert widget.name == 'A'

    Test.a = 'abc'
    assert widget.value == 'abc'

    widget.value = 'def'
    assert Test.a == 'def'


def test_widget_from_param_instance():
    class Test(param.Parameterized):

        a = param.Parameter()

    test = Test()
    widget = TextInput.from_param(test.param.a)
    assert isinstance(widget, TextInput)
    assert widget.name == 'A'

    test.a = 'abc'
    assert widget.value == 'abc'

    widget.value = 'def'
    assert test.a == 'def'


def test_widget_from_param_instance_with_kwargs():
    class Test(param.Parameterized):

        a = param.Number(default=3.14)

    test = Test()
    widget = FloatSlider.from_param(test.param.a, start=0.3, end=5.2)
    assert isinstance(widget, FloatSlider)
    assert widget.name == 'A'
    assert widget.start == 0.3
    assert widget.end == 5.2
    assert widget.value == 3.14

    test.a = 1.57
    assert widget.value == 1.57

    widget.value = 4.3
    assert test.a == 4.3

