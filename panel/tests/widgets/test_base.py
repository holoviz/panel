import param
import pytest

from panel.io import block_comm
from panel.layout import Row
from panel.links import CallbackGenerator
from panel.tests.util import check_layoutable_properties
from panel.util import param_watchers
from panel.widgets import (
    Ace, CompositeWidget, Dial, FileDownload, FloatSlider, LinearGauge,
    LoadingSpinner, Terminal, TextInput, ToggleGroup, Tqdm, Widget,
)
from panel.widgets.tables import BaseTable

excluded = (
    Ace, BaseTable, CompositeWidget, Dial, FileDownload, LinearGauge,
    LoadingSpinner, ToggleGroup, Terminal, Tqdm
)

all_widgets = [
    w for w in param.concrete_descendents(Widget).values()
    if not w.__name__.startswith('_') and not issubclass(w, excluded)
]

@pytest.mark.parametrize('widget', all_widgets)
def test_widget_signature(widget):
    from inspect import signature
    parameters = signature(widget).parameters
    if getattr(getattr(widget, '_param__private', object), 'signature', None):
        pytest.skip('Signature already set by Param')
    assert len(parameters) == 1

@pytest.mark.parametrize('widget', all_widgets)
def test_widget_untracked_watchers(widget, document, comm):
    # Ensures internal code correctly detects
    try:
        widg = widget()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    watchers = [
        w for pwatchers in param_watchers(widg).values()
        for awatchers in pwatchers.values() for w in awatchers
    ]
    assert len([wfn for wfn in watchers if wfn not in widg._internal_callbacks and not hasattr(wfn.fn, '_watcher_name')]) == 0

@pytest.mark.parametrize('widget', all_widgets)
def test_widget_linkable_params(widget, document, comm):
    w = widget()
    controls = w.controls(jslink=True)
    layout = Row(w, controls)

    try:
        CallbackGenerator.error = True
        layout.get_root(document, comm)
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

    assert ([(k, v) for k, v in sorted(w.param.values().items()) if k != 'name'] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k != 'name'])


@pytest.mark.parametrize('widget', all_widgets)
def test_widget_clone_override(widget):
    w = widget()
    clone = w.clone(width=50)

    assert ([(k, v) for k, v in sorted(w.param.values().items()) if k not in ['name', 'width']] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k not in ['name', 'width']])
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
    document.callbacks._held_events = document.callbacks._held_events[:-1]

    # Set new value
    with block_comm():
        text.value = '123'

    assert len(document.callbacks._held_events) == 1
    event = document.callbacks._held_events[0]
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


def test_widget_from_param_negative_precedence():
    class Test(param.Parameterized):

        a = param.Parameter(precedence=-1)

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
