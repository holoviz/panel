from __future__ import absolute_import, division, unicode_literals

import param
import pytest

from panel.io import block_comm
from panel.widgets import (
    CompositeWidget, DataFrame, FileDownload, TextInput, ToggleGroup, Widget
)
from panel.tests.util import check_layoutable_properties, py3_only

all_widgets = [w for w in param.concrete_descendents(Widget).values()
               if not w.__name__.startswith('_') and
               not issubclass(w, (CompositeWidget, DataFrame, FileDownload, ToggleGroup))]


@py3_only
@pytest.mark.parametrize('widget', all_widgets)
def test_widget_signature(widget):
    from inspect import signature
    parameters = signature(widget).parameters
    assert len(parameters) == 1


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
    widget.value = '123'
    document._held_events = document._held_events[:-1]

    # Set new value
    with block_comm():
        text.value = '123'

    assert len(document._held_events) == 1
    event = document._held_events[0]
    assert event.attr == 'value'
    assert event.model is widget
    assert event.new == '123'
