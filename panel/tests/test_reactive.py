from functools import partial

import param

from bokeh.models import Div
from panel.layout import Tabs, WidgetBox
from panel.reactive import Reactive
from panel.viewable import Layoutable
from panel.widgets import Checkbox, StaticText, TextInput


def test_link():
    "Link two Reactive objects"

    class ReactiveLink(Reactive):

        a = param.Parameter()

    obj = ReactiveLink()
    obj2 = ReactiveLink()
    obj.link(obj2, a='a')
    obj.a = 1

    assert obj.a == 1
    assert obj2.a == 1


def test_param_rename():
    "Test that Reactive renames params and properties"

    class ReactiveRename(Reactive):

        a = param.Parameter()
    
        _rename = {'a': 'b'}

    obj = ReactiveRename()

    params = obj._process_property_change({'b': 1})
    assert params == {'a': 1}

    properties = obj._process_param_change({'a': 1})
    assert properties == {'b': 1}


def test_link_properties_nb(document, comm):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    obj = ReactiveLink()
    div = Div()

    # Link property and check bokeh js property callback is defined
    obj._link_props(div, ['text'], document, div, comm)
    assert 'text' in div._callbacks

    # Assert callback is set up correctly
    cb = div._callbacks['text'][0]
    assert isinstance(cb, partial)
    assert cb.args == (document, div.ref['id'], comm)
    assert cb.func == obj._comm_change


def test_link_properties_server(document):

    class ReactiveLink(Reactive):

        text = param.String(default='A')

    obj = ReactiveLink()
    div = Div()

    # Link property and check bokeh callback is defined
    obj._link_props(div, ['text'], document, div)
    assert 'text' in div._callbacks

    # Assert callback is set up correctly
    cb = div._callbacks['text'][0]
    assert isinstance(cb, partial)
    assert cb.args == (document, div.ref['id'])
    assert cb.func == obj._server_change


def test_text_input_controls():
    text_input = TextInput()

    controls = text_input.controls()

    assert isinstance(controls, Tabs)
    assert len(controls) == 2
    wb1, wb2 = controls
    assert isinstance(wb1, WidgetBox)
    assert len(wb1) == 4
    name, disabled, text1, text2 = wb1
    if text1.name == 'Placeholder':
        placeholder, value = text1, text2
    else:
        placeholder, value = text2, text1

    assert isinstance(name, StaticText)
    assert isinstance(disabled, Checkbox)
    assert isinstance(value, TextInput)
    assert isinstance(placeholder, TextInput)

    text_input.disabled = True
    assert disabled.value

    text_input.placeholder = "Test placeholder..."
    assert placeholder.value == "Test placeholder..."

    text_input.value = "New value"
    assert value.value == "New value"

    assert isinstance(wb2, WidgetBox)
    assert len(wb2) == len(list(Layoutable.param)) + 1



def test_text_input_controls_explicit():
    text_input = TextInput()

    controls = text_input.controls(['placeholder', 'disabled'])

    assert isinstance(controls, WidgetBox)
    assert len(controls) == 3
    name, disabled, placeholder = controls
    
    assert isinstance(name, StaticText)
    assert isinstance(disabled, Checkbox)
    assert isinstance(placeholder, TextInput)

    text_input.disabled = True
    assert disabled.value

    text_input.placeholder = "Test placeholder..."
    assert placeholder.value == "Test placeholder..."
