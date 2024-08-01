import asyncio
import os

import pandas as pd
import param
import pytest

from bokeh.models import (
    AutocompleteInput as BkAutocompleteInput, Button as BkButton,
    Checkbox as BkCheckbox, Column as BkColumn, Div, MultiSelect,
    RangeSlider as BkRangeSlider, Row as BkRow, Select, Slider, Tabs as BkTabs,
    TextInput, TextInput as BkTextInput, Toggle,
)
from packaging.version import Version

from panel import config
from panel.depends import bind
from panel.io.state import set_curdoc, state
from panel.layout import Row, Tabs
from panel.models import HTML as BkHTML
from panel.pane import (
    HTML, Bokeh, Markdown, Matplotlib, PaneBase, Str, panel,
)
from panel.param import (
    JSONInit, Param, ParamFunction, ParamMethod, Skip,
)
from panel.tests.util import (
    async_wait_until, mpl_available, mpl_figure, wait_until,
)
from panel.widgets import (
    AutocompleteInput, Button, Checkbox, DatePicker, DatetimeInput,
    EditableFloatSlider, EditableRangeSlider, LiteralInput, NumberInput,
    RangeSlider,
)


def Pane(obj, **kwargs):
    return PaneBase.get_pane_type(obj, **kwargs)(obj, **kwargs)


def test_instantiate_from_class():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test), Param)


def test_instantiate_from_parameter():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test.param.a), Param)


def test_instantiate_from_parameters():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test.param), Param)


def test_instantiate_from_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test()), Param)


def test_instantiate_from_parameter_on_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test().param.a), Param)


def test_instantiate_from_parameters_on_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test().param), Param)


def test_param_pane_repr(document, comm):

    class Test(param.Parameterized):
        pass

    assert repr(Param(Test())) == 'Param(Test)'


def test_param_pane_repr_with_params(document, comm):

    class Test(param.Parameterized):
        a = param.Number()
        b = param.Number()

    assert repr(Param(Test(), parameters=['a'])) == "Param(Test, parameters=['a'])"

    # With a defined name.
    test_pane = Param(Test(), parameters=['a'], name='Another')
    assert repr(test_pane) == "Param(Test, name='Another', parameters=['a'])"


def test_get_root(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 1

    html = model.children[0]
    assert isinstance(html, Div)
    assert html.text == '<b>'+test.name[:-5]+'</b>'


def test_single_param(document, comm):

    class Test(param.Parameterized):
        a = param.Parameter(default=0)

    test = Test()
    test_pane = Param(test.param.a)
    model = test_pane.get_root(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 1

    widget = model.children[0]
    assert isinstance(widget, TextInput)
    assert widget.value == '0'


def test_get_root_tabs(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Param(test, expand_layout=Tabs)
    model = test_pane.get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 1

    box = model.tabs[0].child
    assert isinstance(box, BkColumn)
    assert len(box.children) == 0


def test_number_param(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    slider = model.children[1]
    assert isinstance(slider, Slider)
    assert slider.value == 1.2
    assert slider.start == 0
    assert slider.end == 5
    assert slider.step == 0.1
    assert slider.disabled == False

    # Check changing param value updates widget
    test.a = 3.3
    assert slider.value == 3.3

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.bounds = (0.1, 5.5)
    assert slider.start == 0.1
    assert slider.end == 5.5

    a_param.constant = True
    assert slider.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.bounds = (-0.1, 3.8)
    test.a = 0.5
    assert slider.value == 3.3
    assert slider.start == 0.1
    assert slider.end == 5.5
    assert slider.disabled == True


def test_boolean_param(document, comm):
    class Test(param.Parameterized):
        a = param.Boolean(default=False)

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    checkbox = model.children[1]
    assert isinstance(checkbox, BkCheckbox)
    assert checkbox.label == 'A'
    assert checkbox.active == False
    assert checkbox.disabled == False

    # Check changing param value updates widget
    test.a = True
    assert checkbox.active == True

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.constant = True
    assert checkbox.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    test.a = False
    assert checkbox.active == True
    assert checkbox.disabled == True


def test_range_param(document, comm):
    class Test(param.Parameterized):
        a = param.Range(default=(0.1, 0.5), bounds=(0, 1.1))

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    widget = model.children[1]
    assert isinstance(widget, BkRangeSlider)
    assert widget.start == 0
    assert widget.end == 1.1
    assert widget.value == (0.1, 0.5)

    # Check changing param value updates widget
    test.a = (0.2, 0.4)
    assert widget.value == (0.2, 0.4)

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.bounds = (0.1, 0.6)
    assert widget.start == 0.1
    assert widget.end == 0.6
    a_param.constant = True
    assert widget.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.bounds = (-1, 1)
    test.a = (0.05, 0.2)
    assert widget.value == (0.2, 0.4)
    assert widget.start == 0.1
    assert widget.end == 0.6
    assert widget.disabled == True


def test_integer_param(document, comm):
    class Test(param.Parameterized):
        a = param.Integer(default=2, bounds=(0, 5))

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    slider = model.children[1]
    assert isinstance(slider, Slider)
    assert slider.value == 2
    assert slider.start == 0
    assert slider.end == 5
    assert slider.step == 1
    assert slider.disabled == False

    # Check changing param value updates widget
    test.a = 3
    assert slider.value == 3

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.bounds = (1, 6)
    assert slider.start == 1
    assert slider.end == 6

    a_param.constant = True
    assert slider.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.bounds = (-1, 7)
    test.a = 1
    assert slider.value == 3
    assert slider.start == 1
    assert slider.end == 6
    assert slider.disabled == True


def test_object_selector_param(document, comm):
    class Test(param.Parameterized):
        a = param.ObjectSelector(default='b', objects=[1, 'b', 'c'])

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    select = model.children[1]
    assert isinstance(select, Select)
    assert select.options == [('1','1'), ('b','b'), ('c','c')]
    assert select.value == 'b'
    assert select.disabled == False

    # Check changing param value updates widget
    test.a = 1
    assert select.value == '1'

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.objects = ['c', 'd', 1]
    assert select.options == [('c','c'), ('d','d'), ('1','1')]

    a_param.constant = True
    assert select.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.objects = [1, 'c', 'd']
    test.a = 'd'
    assert select.value == '1'
    assert select.options == [('c','c'), ('d','d'), ('1','1')]
    assert select.disabled == True


def test_list_selector_param(document, comm):
    class Test(param.Parameterized):
        a = param.ListSelector(default=['b', 1], objects=[1, 'b', 'c'])

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    slider = model.children[1]
    assert isinstance(slider, MultiSelect)
    assert slider.options == ['1', 'b', 'c']
    assert slider.value == ['b', '1']
    assert slider.disabled == False

    # Check changing param value updates widget
    test.a = ['c', 1]
    assert slider.value == ['c', '1']

    # Check changing param attribute updates widget
    a_param = test.param['a']
    a_param.objects = ['c', 'd', 1]
    assert slider.options == ['c', 'd', '1']

    a_param.constant = True
    assert slider.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.objects = [1, 'c', 'd']
    test.a = ['d']
    assert slider.value == ['c', '1']
    assert slider.options == ['c', 'd', '1']
    assert slider.disabled == True


def test_action_param(document, comm):
    class Test(param.Parameterized):
        a = param.Action(default=lambda x: setattr(x, 'b', 2))
        b = param.Number(default=1)

    test = Test()
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    button = model.children[1]
    assert isinstance(button, BkButton)

    # Check that the action is actually executed
    pn_button = test_pane.layout[1]
    pn_button.clicks = 1

    assert test.b == 2


def test_number_param_overrides(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=0.1, bounds=(0, 1.1))

    test = Test()
    test_pane = Param(test, widgets={'a': {'value': 0.3, 'start': 0.1, 'end': 1.0}})
    model = test_pane.get_root(document, comm=comm)

    widget = model.children[1]
    assert isinstance(widget, Slider)
    assert widget.start == 0.1
    assert widget.end == 1.
    assert widget.value == 0.3


def test_object_selector_param_overrides(document, comm):
    class Test(param.Parameterized):
        a = param.ObjectSelector(default='b', objects=[1, 'b', 'c'])

    test = Test()
    test_pane = Param(test, widgets={'a': {'options': ['b', 'c'], 'value': 'c'}})
    model = test_pane.get_root(document, comm=comm)

    select = model.children[1]
    assert isinstance(select, Select)
    assert select.options == ['b', 'c']
    assert select.value == 'c'
    assert select.disabled == False


def test_number_input_none_support():
    class Test(param.Parameterized) :
        number = param.Number(default=0, allow_None=True)
        none = param.Number(default=None, allow_None=True)

    test_widget = Param(Test())
    assert test_widget[1].value == 0
    assert test_widget[2].value is None


def test_explicit_params(document, comm):
    class Test(param.Parameterized):
        a = param.Boolean(default=False)
        b = param.Integer(default=1)

    test = Test()
    test_pane = Param(test, parameters=['a'])
    model = test_pane.get_root(document, comm=comm)

    assert len(model.children) == 2
    assert isinstance(model.children[1], BkCheckbox)


def test_param_name_update(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test(name='A')
    test_pane = Param(test)

    model = test_pane.get_root(document, comm=comm)
    assert model.children[0].text == '<b>A</b>'

    test_pane.object = Test(name='B')
    assert model.children[0].text == '<b>B</b>'


def test_param_precedence(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test()
    test_pane = Param(test)

    # Check changing precedence attribute hides and shows widget
    a_param = test.param['a']
    a_param.precedence = -1
    assert test_pane._widgets['a'] not in test_pane._widget_box.objects

    a_param.precedence = 1
    assert test_pane._widgets['a'] in test_pane._widget_box.objects

    a_param.precedence = None
    assert test_pane._widgets['a'] in test_pane._widget_box.objects


def test_hide_constant(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), constant=True)

    test = Test()
    test_pane = Param(test, parameters=['a'], hide_constant=True)
    model = test_pane.get_root(document, comm=comm)

    slider = model.children[1]
    assert not slider.visible

    test.param.a.constant = False

    assert slider.visible


def test_param_label(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), label='A')
        b = param.Action(label='B')

    test = Test()
    test_pane = Param(test)

    # Check updating label changes widget name
    a_param = test.param['a']
    a_param.label = 'B'
    assert test_pane._widgets['a'].name == 'B'

    b_param = test.param['b']
    b_param.label = 'C'
    assert test_pane._widgets['b'].name == 'C'


def test_param_widget_type(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), label='A')
        b = param.Number(default=1.2, bounds=(0, 5), label='B')

    test = Test()
    test_pane = Param(test, widgets={'b': {'widget_type': EditableFloatSlider}})


    # Check that b is displayed with an EditableFloatSlider
    wa = test_pane._widgets['a']
    wb = test_pane._widgets['b']
    assert not isinstance(wa, EditableFloatSlider)
    assert isinstance(wb, EditableFloatSlider)
    assert wb.value == 1.2
    assert (wb.fixed_start, wb.fixed_end) == (0, 5)
    assert wb.name == 'B'


def test_param_throttled(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), label='A')
        b = param.Number(default=1.2, bounds=(0, 5), label='B')

    test = Test()
    try:
        param.parameterized.warnings_as_exceptions = True
        test_pane = Param(test, widgets={'b': {'throttled': True}})
    finally:
        param.parameterized.warnings_as_exceptions = False

    model = test_pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    _, ma, mb = model.children

    ma.value = 1
    assert ma.value == 1
    assert ma.value_throttled == 1.2
    assert test.a == 1

    test.a = 2
    assert ma.value == 2
    assert ma.value_throttled == 1.2
    assert test.a == 2

    # `test.b` is linked to `mb.value_throttled` instead of `mb.value` when throttled
    test_pane._widgets['b']._process_events({'value_throttled': 3})
    assert mb.value != 3
    assert test.b == 3

    test_pane._widgets['b']._process_events({'value': 4})
    assert test.b == 3
    assert mb.value == 4

    test.b = 5
    assert mb.value == 5
    assert test_pane._widgets['b'].value == 5
    assert test_pane._widgets['b'].value_throttled == 5


def test_param_onkeyup(document, comm):
    class Test(param.Parameterized):
        a = param.String(default='1.2', label='A')
        b = param.String(default='1.2', label='B')

    test = Test()
    try:
        param.parameterized.warnings_as_exceptions = True
        test_pane = Param(test, widgets={'b': {'onkeyup': True}})
    finally:
        param.parameterized.warnings_as_exceptions = False

    model = test_pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    _, ma, mb = model.children

    ma.value = '1'
    assert ma.value == '1'
    assert ma.value_input == ''
    assert test.a == '1'

    test.a = '2'
    assert ma.value == '2'
    assert ma.value_input == ''
    assert test.a == '2'

    # `test.b` is linked to `mb.value_input` instead of `mb.value` when onkeyup
    test_pane._widgets['b']._process_events({'value_input': '3'})
    assert mb.value != '3'
    assert test.b == '3'

    test_pane._widgets['b']._process_events({'value': '4'})
    assert test.b == '3'
    assert mb.value == '4'


def test_param_event_parameter(document, comm):

    l = []
    class Test(param.Parameterized):
        e = param.Event()

        @param.depends('e', watch=True)
        def incr(self):
            l.append(1)

    test = Test()
    test_pane = Param(test)

    test_pane._widgets['e']._process_events({'clicks': 1})

    # Check that a watcher was set on the button that depends on e
    assert l == [1]


def test_param_precedence_ordering(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), precedence=-1)
        b = param.Boolean(default=True, precedence=1)

    test = Test()
    test_pane = Param(test)

    # Check changing precedence attribute hides and shows widget
    a_param = test.param['a']
    a_param.precedence = 2
    assert test_pane._widget_box.objects == [test_pane._widgets[w] for w in ('_title', 'b', 'a')]

    a_param.precedence = 1
    assert test_pane._widget_box.objects == [test_pane._widgets[w] for w in ('_title', 'a', 'b')]


def test_param_step(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5), step=0.1)

    test = Test()
    test_pane = Param(test)
    assert test_pane._widgets['a'].step == 0.1

    a_param = test.param['a']
    a_param.step = 0.25
    assert test_pane._widgets['a'].step == 0.25


def test_replace_param_object(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10))

    pane = Param()

    model = pane.get_root(document, comm=comm)

    assert model.children == []

    pane.object = Test()

    assert len(model.children) == 2
    title, widget = model.children

    assert isinstance(title, Div)
    assert title.text == '<b>Test</b>'

    assert isinstance(widget, Slider)
    assert widget.start == 0
    assert widget.end == 10

    # Check when object is from parameters
    pane.object = Test().param

    assert len(model.children) == 2
    title, widget = model.children

    assert isinstance(title, Div)
    assert title.text == '<b>Test</b>'

    assert isinstance(widget, Slider)
    assert widget.start == 0
    assert widget.end == 10

    # Check when object is None
    pane.object = None

    assert len(model.children) == 0


def test_set_name(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10))
        b = param.String(default='A')

    pane = Param(Test(), name='First')

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    title, slider, text = model.children
    assert isinstance(title, Div)
    # Check setting name displays in as a title
    assert title.text == '<b>First</b>'
    assert isinstance(slider, Slider)
    assert isinstance(text, TextInput)

    pane.name = 'Second'

    assert len(model.children) == 3
    title, _, _ = model.children
    assert isinstance(title, Div)
    # Check the title updates with name
    assert title.text == '<b>Second</b>'


def test_set_parameters(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10))
        b = param.String(default='A')

    pane = Param(Test())

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    title, slider, text = model.children
    assert isinstance(title, Div)
    assert isinstance(slider, Slider)
    assert isinstance(text, TextInput)

    pane.parameters = ['b']

    assert len(model.children) == 2
    title, text = model.children
    assert isinstance(title, Div)
    assert isinstance(text, TextInput)


def test_trigger_parameters(document, comm):
    class Test(param.Parameterized):
        a = param.ListSelector(objects=[1,2,3,4], default=list())

    t = Test()
    t.a.append(4)

    pane = Param(t.param.a)

    t.a.append(1)
    t.param.trigger('a')

    assert pane[0].value == [4, 1]


def test_set_display_threshold(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10), precedence=1)
        b = param.String(default='A', precedence=2)

    pane = Param(Test())

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    title, slider, text = model.children
    assert isinstance(title, Div)
    assert isinstance(slider, Slider)
    assert isinstance(text, TextInput)

    pane.display_threshold = 1.5

    assert len(model.children) == 2
    title, text = model.children
    assert isinstance(title, Div)
    assert isinstance(text, TextInput)


def test_set_widgets(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1, bounds=(0, 10), precedence=1)
        b = param.String(default='A', precedence=2)

    pane = Param(Test())

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 3
    title, slider, text = model.children
    assert isinstance(title, Div)
    assert isinstance(slider, Slider)
    assert isinstance(text, TextInput)

    pane.widgets = {'a': LiteralInput(value=1, type=(float, int))}

    assert len(model.children) == 3
    title, number, text = model.children
    assert isinstance(title, Div)
    assert isinstance(number, TextInput)
    assert isinstance(text, TextInput)

    pane.widgets = {'a': {'height':100}}

    assert len(model.children) == 3
    title, number, text = model.children
    assert isinstance(title, Div)
    assert isinstance(number, Slider)
    assert number.height == 100
    assert isinstance(text, TextInput)

    pane.widgets = {'a': {'type': LiteralInput, 'height':100}}

    assert len(model.children) == 3
    title, number, text = model.children
    assert isinstance(title, Div)
    assert isinstance(number, TextInput)
    assert number.height == 100
    assert isinstance(text, TextInput)


def test_set_widgets_throttled(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=0, bounds=(0, 10), precedence=1)

    test = Test()
    pane = Param(test)
    model = pane.get_root(document, comm=comm)

    pane.widgets = {"a": {"throttled": False}}
    assert len(model.children) == 2
    _, number = model.children

    number.value = 1
    assert number.value == 1
    assert number.value_throttled != 1
    assert test.a == 1

    test.a = 2
    assert number.value == 2
    assert number.value_throttled != 2
    assert test.a == 2

    # By setting throttled to true,
    # `test.a` is linked to `number.value_throttled`
    # instead of `number.value`.
    pane.widgets = {"a": {"throttled": True}}
    assert len(model.children) == 2
    _, number = model.children

    pane._widgets['a']._process_events({'value_throttled': 3})
    assert number.value != 3
    assert test.a == 3

    pane._widgets['a']._process_events({'value': 4})
    assert test.a == 3
    assert number.value == 4

    test.a = 5
    assert number.value == 5
    assert pane._widgets['a'].value == 5
    assert pane._widgets['a'].value_throttled == 5


def test_set_show_name(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10))

    pane = Param(Test())

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 2
    title, widget = model.children
    assert isinstance(title, Div)
    assert isinstance(widget, Slider)

    pane.show_name = False

    assert len(model.children) == 1
    assert isinstance(model.children[0], Slider)


def test_set_show_labels(document, comm):
    class Test(param.Parameterized):
        a = param.Number(bounds=(0, 10))

    pane = Param(Test())

    model = pane.get_root(document, comm=comm)

    assert len(model.children) == 2
    title, widget = model.children
    assert isinstance(title, Div)
    assert isinstance(widget, Slider)
    assert widget.title == 'A'

    pane.show_labels = False

    assert len(model.children) == 2
    assert isinstance(model.children[1], Slider)
    assert model.children[1].title == ''


def test_expand_param_subobject(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    toggle = model.children[1].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].value = True
    assert len(model.children) == 3
    _, _, subpanel = test_pane.layout.objects
    col = model.children[2]
    assert isinstance(col, BkColumn)
    assert isinstance(col, BkColumn)
    assert len(col.children) == 2
    div, widget = col.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].value = False
    assert len(model.children) == 2


def test_switch_param_subobject(document, comm):
    class Test(param.Parameterized):
        a = param.ObjectSelector()

    o1 = Test(name='Subobject 1')
    o2 = Test(name='Subobject 2')
    Test.param['a'].objects = [o1, o2, 3]
    test = Test(a=o1, name='Nested')
    test_pane = Param(test)
    model = test_pane.get_root(document, comm=comm)

    toggle = model.children[1].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].value = True
    assert len(model.children) == 3
    _, _, subpanel = test_pane.layout.objects
    col = model.children[2]
    assert isinstance(col, BkColumn)
    assert len(col.children) == 2
    div, row = col.children
    assert div.text == '<b>Subobject 1</b>'
    assert isinstance(row.children[0], Select)

    # Switch subobject
    test_pane._widgets['a'][0].value = o2
    _, _, subpanel = test_pane.layout.objects
    col = model.children[2]
    assert isinstance(col, BkColumn)
    assert len(col.children) == 2
    div, row = col.children
    assert div.text == '<b>Subobject 2</b>'
    assert isinstance(row.children[0], Select)

    # Collapse subpanel
    test_pane._widgets['a'][1].value = False
    assert len(model.children) == 2
    assert subpanel._models == {}


def test_expand_param_subobject_into_row(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    row = Row()
    test_pane = Param(test, expand_layout=row)
    layout = Row(test_pane, row)
    model = layout.get_root(document, comm=comm)

    toggle = model.children[0].children[1].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].value = True
    assert len(model.children) == 2
    subpanel = row.objects[0]
    row = model.children[1]
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkColumn)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].value = False
    assert len(row.children) == 0
    assert subpanel._models == {}


def test_expand_param_subobject_expand(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Param(test, expand=True, expand_button=True)
    model = test_pane.get_root(document, comm=comm)

    toggle = model.children[1].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    assert len(model.children) == 3
    _, _, subpanel = test_pane.layout.objects
    col = model.children[2]
    assert isinstance(col, BkColumn)
    assert len(col.children) == 2
    div, widget = col.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].value = False
    assert len(model.children) == 2
    assert subpanel._models == {}


def test_param_subobject_expand_no_toggle(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Param(test, expand=True,
                     expand_button=False)
    model = test_pane.get_root(document, comm=comm)

    # Assert no toggle was added
    assert len(model.children) == 3

    # Expand subpane
    _, _, subpanel = test_pane.layout.objects
    div, widget = model.children[2].children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)


def test_expand_param_subobject_tabs(document, comm):
    class Test(param.Parameterized):
        abc = param.Parameter()

    test = Test(abc=Test(name='Nested'), name='A')
    test_pane = Param(test, expand_layout=Tabs)
    model = test_pane.get_root(document, comm=comm)

    toggle = model.tabs[0].child.children[0].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpanel
    test_pane._widgets['abc'][1].value = True
    assert len(model.tabs) == 2
    _, subpanel = test_pane.layout.objects
    subtabs = model.tabs[1].child
    assert model.tabs[1].title == 'Abc'
    assert isinstance(subtabs, BkTabs)
    assert len(subtabs.tabs) == 1
    assert subtabs.tabs[0].title == 'Nested'

    box = subtabs.tabs[0].child
    assert isinstance(box, BkColumn)
    assert len(box.children) == 1
    widget = box.children[0]
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['abc'][1].value = False
    assert len(model.tabs) == 1


def test_param_js_callbacks(document, comm):
    class JsButton(param.Parameterized):
        param_btn = param.Action(default=lambda self: print('Action Python Response'), label='Action')  # noqa: T201

    param_button = Param(JsButton())
    code = "console.log('Action button clicked')"
    param_button[1].js_on_click(code=code)

    model = param_button.get_root(document, comm=comm)

    button = model.children[1]
    assert len(button.js_event_callbacks) == 1
    callbacks = button.js_event_callbacks
    assert 'button_click' in callbacks
    assert len(callbacks['button_click']) == 1
    assert code in callbacks['button_click'][0].code


def test_param_calendar_date_mapping():

    class Test(param.Parameterized):

        a = param.CalendarDate()

    assert isinstance(Param(Test().param).layout[1], DatePicker)


def test_param_date_mapping():

    class Test(param.Parameterized):

        a = param.Date()

    assert isinstance(Param(Test().param).layout[1], DatetimeInput)


class View(param.Parameterized):

    a = param.Integer(default=0)

    b = param.Parameter()

    @param.depends('a')
    def view(self):
        return Div(text='%d' % self.a)

    @param.depends('b.param')
    def subobject_view(self):
        return Div(text='%d' % self.b.a)

    @param.depends('a')
    def mpl_view(self):
        return mpl_figure()

    @param.depends('a')
    def mixed_view(self):
        return self.view() if (self.a % 2) else self.mpl_view()


def test_get_param_function_pane_type():
    test = View()

    def view(a):
        return Div(text='%d' % a)

    assert PaneBase.get_pane_type(view) is not ParamFunction
    assert PaneBase.get_pane_type(param.depends(test.param.a)(view)) is ParamFunction


def test_param_function_pane(document, comm):
    test = View()

    @param.depends(test.param.a)
    def view(a):
        return Div(text='%d' % a)

    pane = panel(view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Bokeh)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is row
    assert isinstance(model, Div)
    assert model.text == '0'

    # Update pane
    test.a = 5
    new_model = row.children[0]
    assert inner_pane is pane._pane
    assert new_model.text == '5'
    assert pane._models[row.ref['id']][0] is row

    # Cleanup pane
    pane._cleanup(row)
    assert pane._models == {}
    assert inner_pane._models == {}


def test_resolve_param_function_pane_when_defer_load(document, comm):
    def view():
        return Div(text='blah')

    pane = panel(view, defer_load=True)
    assert isinstance(pane, ParamFunction)


def test_param_function_pane_defer_load(document, comm):
    test = View()

    @param.depends(test.param.a)
    def view(a):
        return Div(text='%d' % a)

    pane = panel(view, defer_load=True)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Str)

    # Ensure pane thinks page is not loaded
    state._loaded[document] = False

    # Create pane
    with set_curdoc(document):
        row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is row
    assert isinstance(model, BkHTML)
    assert model.text == '&lt;pre&gt; &lt;/pre&gt;'

    # Test on_load
    state._on_load(document)
    model = row.children[0]
    assert isinstance(model, Div)
    assert model.text == '0'

    # Cleanup pane
    pane._cleanup(row)
    assert pane._models == {}
    assert inner_pane._models == {}

class ParameterizedMock(param.Parameterized):
        run = param.Event()

        @param.depends("run")
        def click_view(self):
            return "click..."

def test_param_function_pane_config_defer_load():
    # When
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.defer_load == config.defer_load

    # When
    config.defer_load = not config.defer_load
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.defer_load == config.defer_load

    # When
    config.defer_load = not config.defer_load
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.defer_load == config.defer_load

    # Clean Up
    config.defer_load = config.param.defer_load.default

def test_param_function_pane_config_loading_indicator():
    # When
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.loading_indicator==config.loading_indicator

    # When
    config.loading_indicator=not config.loading_indicator
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.loading_indicator==config.loading_indicator

    # When
    config.loading_indicator=not config.loading_indicator
    app = ParameterizedMock()
    test = ParamMethod(app.click_view)
    # Then
    assert test.loading_indicator==config.loading_indicator

    # Clean Up
    config.loading_indicator=config.param.loading_indicator.default

def test_param_function_pane_update(document, comm):
    test = View()

    objs = {
        0: HTML("012"),
        1: HTML("123")
    }

    @param.depends(test.param.a)
    def view(a):
        return objs[a]

    pane = panel(view)
    inner_pane = pane._pane
    assert inner_pane is objs[0]
    assert inner_pane.object is objs[0].object
    assert not pane._internal

    test.a = 1

    assert pane._pane is not inner_pane
    assert not pane._internal

    objs[0].param.watch(print, ['object'])

    test.a = 0

    assert pane._pane is inner_pane
    assert not pane._internal


def test_get_param_method_pane_type():
    assert PaneBase.get_pane_type(View().view) is ParamMethod


def test_param_method_pane(document, comm):
    test = View()
    pane = panel(test.view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Bokeh)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is row
    assert isinstance(model, Div)
    assert model.text == '0'

    # Update pane
    test.a = 5
    new_model = row.children[0]
    assert inner_pane is pane._pane
    assert new_model.text == '5'
    assert pane._models[row.ref['id']][0] is row

    # Cleanup pane
    pane._cleanup(row)
    assert pane._models == {}
    assert inner_pane._models == {}


def test_param_method_pane_subobject(document, comm):
    subobject = View(name='Nested', a=42)
    test = View(b=subobject)
    pane = panel(test.subobject_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Bokeh)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, Div)
    assert model.text == '42'

    # Ensure that subobject is being watched
    watchers = pane._internal_callbacks
    assert any(w.inst is subobject for w in watchers)
    assert pane._models[row.ref['id']][0] is row

    # Ensure that switching the subobject triggers update in watchers
    new_subobject = View(name='Nested', a=42)
    test.b = new_subobject
    assert pane._models[row.ref['id']][0] is row
    watchers = pane._internal_callbacks
    assert not any(w.inst is subobject for w in watchers)
    assert any(w.inst is new_subobject for w in watchers)

    # Cleanup pane
    pane._cleanup(row)
    assert pane._models == {}
    assert inner_pane._models == {}


@mpl_available
def test_param_method_pane_mpl(document, comm):
    test = View()
    pane = panel(test.mpl_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Matplotlib)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is row
    text = model.text

    # Update pane
    test.a = 5
    new_model = row.children[0]
    assert inner_pane is pane._pane
    assert new_model is model
    assert new_model.text != text
    assert pane._models[row.ref['id']][0] is row

    # Cleanup pane
    pane._cleanup(row)
    assert pane._models == {}
    assert inner_pane._models == {}


@mpl_available
def test_param_method_pane_changing_type(document, comm):
    test = View()
    pane = panel(test.mixed_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Matplotlib)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    model = row.children[0]
    text = model.text
    assert text.startswith('&lt;img src=')

    # Update pane
    test.a = 5
    new_model = row.children[0]
    new_pane = pane._pane
    assert isinstance(new_pane, Bokeh)
    assert isinstance(new_model, Div)
    assert new_model.text != text

    # Cleanup pane
    new_pane._cleanup(row)
    assert new_pane._models == {}


def test_jsoninit_class_from_env_var():
    os.environ['PARAM_JSON_INIT'] = '{"a": 1}'

    json_init = JSONInit()

    class Test(param.Parameterized):
        a = param.Integer()

    json_init(Test)

    assert Test.a == 1
    del os.environ['PARAM_JSON_INIT']


def test_jsoninit_instance_from_env_var():
    os.environ['PARAM_JSON_INIT'] = '{"a": 2}'

    json_init = JSONInit()

    class Test(param.Parameterized):
        a = param.Integer()

    test = Test()
    json_init(test)

    assert test.a == 2
    del os.environ['PARAM_JSON_INIT']

def test_change_object_and_keep_parameters():
    """Test that https://github.com/holoviz/panel/issues/1581 is solved"""
    # Given
    class TextModel(param.Parameterized):
        text = param.String()
        param2 = param.String()

    class TextView(param.Parameterized):
        text = param.ClassSelector(class_=TextModel)
        text_pane = param.Parameter()

        def __init__(self, **params):
            params["text"] = TextModel(text="Original Text")
            super().__init__(**params)

            self.text_pane = Param(
                self.text, parameters=["text"]
            )

        @param.depends("text", watch=True)
        def _update_text_pane(self, *_):
            self.text_pane.object = self.text

    view = TextView()
    assert view.text_pane.parameters==["text"]

    # When
    view.text = TextModel(text="New TextModel")
    # Then
    assert view.text_pane.parameters==["text"]


def test_rerender_bounded_widget_when_bounds_set_and_unset():
    class Test(param.Parameterized):
        num = param.Range()

    test = Test()
    p = Param(test)

    assert isinstance(p._widgets['num'], LiteralInput)
    assert p._widgets['num'] in p._widget_box

    test.param.num.bounds = (0, 5)

    assert isinstance(p._widgets['num'], RangeSlider)
    assert p._widgets['num'] in p._widget_box

    test.param.num.bounds = (None, 5)

    assert isinstance(p._widgets['num'], LiteralInput)
    assert p._widgets['num'] in p._widget_box


def test_numberinput_bounds():

    class Test(param.Parameterized):
        num = param.Number(default=5, bounds=(0, 5))

    test = Test()
    p = Param(test, widgets={'num': NumberInput})

    numinput = p.layout[1]

    assert numinput.start == 0
    assert numinput.end == 5


def test_set_widget_autocompleteinput(document, comm):

    class Test(param.Parameterized):
        # Testing with default='' and check_on_set=False since this feels
        # like the most sensible default config for Selector -> AutocompleteInput
        choice = param.Selector(default='', objects=['a', 'b'], check_on_set=False)

    test = Test()
    test_pane = Param(test, widgets={'choice': AutocompleteInput})

    model = test_pane.get_root(document, comm=comm)

    autocompleteinput = model.children[1]
    assert isinstance(autocompleteinput, BkAutocompleteInput)
    assert autocompleteinput.completions == ['a', 'b', '']
    assert autocompleteinput.value == ''
    assert autocompleteinput.disabled == False

    # Check changing param value updates widget
    test.choice = 'b'
    assert autocompleteinput.value == 'b'

    # Check changing param attribute updates widget
    test.param['choice'].objects = ['c', 'd']
    assert autocompleteinput.completions == ['c', 'd']
    assert autocompleteinput.value == ''


def test_set_widget_autocompleteinput_empty_objects(document, comm):

    class Test(param.Parameterized):
        # Testing with default='' and check_on_set=False since this feels
        # like the most sensible default config for Selector -> AutocompleteInput
        choice = param.Selector(default='', objects=[], check_on_set=False)

    test = Test()
    test_pane = Param(test, widgets={'choice': AutocompleteInput})

    model = test_pane.get_root(document, comm=comm)

    autocompleteinput = model.children[1]
    assert isinstance(autocompleteinput, BkAutocompleteInput)
    assert autocompleteinput.completions == ['']
    assert autocompleteinput.value == ''
    assert autocompleteinput.disabled == False


def test_sorted():
    class MyClass(param.Parameterized):
        valueb = param.Integer(label="zzz")
        valuez = param.String(label="aaa")
        valuea = param.Integer(label="bbb")

    my_class = MyClass()
    _, input1, input2, input3 = Param(my_class, sort=True)
    assert input1.name=="aaa"
    assert input2.name=="bbb"
    assert input3.name=="zzz"

def test_sorted_func():
    class MyClass(param.Parameterized):
        valueb = param.Integer(label="bac")
        valuez = param.String(label="acb")
        valuea = param.Integer(label="cba")

    my_class = MyClass()
    def sort_func(x):
        return x[1].label[::-1]
    _, input1, input2, input3 = Param(my_class, sort=sort_func)
    assert input1.name=="cba"
    assert input2.name=="acb"
    assert input3.name=="bac"


def test_param_editablerangeslider_with_bounds():
    class Test(param.Parameterized):
        i = param.Range(default=(1, 2), softbounds=(1, 5), bounds=(0, 10))

    t = Test()
    w = EditableRangeSlider.from_param(t.param.i)

    if Version(param.__version__) >= Version('2.0.0a3'):
        msg = r"Range parameter 'EditableRangeSlider\.value' lower bound must be in range \[0, 10\], not -1\."
    elif Version(param.__version__) >= Version('2.0.0a2'):
        msg = r"Attribute 'bound' of Range parameter 'EditableRangeSlider\.value' must be in range '\[0, 10\]'"
    else:
        msg = r"Range parameter 'value''s lower bound must be in range \[0, 10\]"
    with pytest.raises(ValueError, match=msg):
        w.value = (-1, 2)

    assert w.value == (1, 2)


def test_from_param_with_ref_as_option():
    class Test(param.Parameterized):
        s = param.String(default='A')

        @param.depends('s')
        def ref(self):
            return [self.s] + ['B']

    t = Test()
    w = AutocompleteInput.from_param(t.param.s, options=t.ref)

    assert w.options == ['A', 'B']

    t.s = 'C'

    assert w.options == ['C', 'B']


def test_paramfunction_bare_emits_warning(caplog):

    def foo():
        return 'bar'

    # Emits a Param warning
    ParamFunction(foo)

    log_record = caplog.records[0]

    assert log_record.levelname == 'WARNING'
    assert "The function 'foo' does not have any dependencies and will never update" in log_record.message


def test_paramfunction_bare_lazy_no_warning(caplog):

    def foo():
        return 'bar'

    # No warning should be emitted when the ParamFunction is lazy
    ParamFunction(foo, lazy=True)

    for log_record in caplog.records:
        assert "The function 'foo' does not have any dependencies and will never update" not in log_record.message


def test_param_editablefloatslider_with_bounds():
    class Test(param.Parameterized):
        i = param.Number(default=1, softbounds=(1, 5), bounds=(0, 10))


    t = Test()
    w = EditableFloatSlider.from_param(t.param.i)

    if Version(param.__version__) > Version('2.0.0a2'):
        msg = "Number parameter 'EditableFloatSlider.value' must be at least 0, not -1"
    else:
        msg = "Parameter 'value' must be at least 0, not -1"
    with pytest.raises(ValueError, match=msg):
        w.value = -1

    assert w.value == 1


def test_param_function_inplace_dataframe_update(document, comm):
    number = NumberInput(value=0)

    def layout(value):
        return pd.DataFrame({
            'x': [0, 1, 2],
            'y': [0, 1, value]
        })

    pane = ParamFunction(bind(layout, number), inplace=True)

    root = pane.get_root(document, comm)

    model = root.children[0]

    html_table = model.text
    assert html_table.startswith("&lt;table class=&quot;dataframe panel-df&quot;&gt;\n  &lt;thead&gt;\n")

    number.value = 314

    assert model is root.children[0]
    assert model.text != html_table
    assert '314' in model.text

    html_table = model.text
    number.param.trigger('value')
    assert model.text is html_table


def test_param_function_recursive_update(document, comm):
    checkbox = Checkbox(value=False)

    def layout(value):
        return Row(Markdown(f"{value}"))

    pane = ParamFunction(bind(layout, checkbox), inplace=True)

    root = pane.get_root(document, comm)

    layout = root.children[0]

    assert layout.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'

    checkbox.value = True

    assert layout is root.children[0]
    assert layout.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'


def test_param_function_recursive_update_multiple(document, comm):
    checkbox = Checkbox(value=False)

    def layout(value):
        return Row(Markdown(f"{value}"), Markdown(f"{not value}"))

    layout = ParamFunction(bind(layout, checkbox), inplace=True)

    root = layout.get_root(document, comm)

    layout = root.children[0]

    assert layout.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'
    assert layout.children[1].text == '&lt;p&gt;True&lt;/p&gt;\n'

    checkbox.value = True

    assert layout is root.children[0]
    assert layout.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'
    assert layout.children[1].text == '&lt;p&gt;False&lt;/p&gt;\n'


@pytest.mark.flaky(max_runs=3)
def test_param_generator(document, comm):
    checkbox = Checkbox(value=False)

    def function(value):
        yield Markdown(f"{value}")

    pane = ParamFunction(bind(function, checkbox))

    root = pane.get_root(document, comm)

    wait_until(lambda: root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n', timeout=10_000)

    checkbox.value = True

    wait_until(lambda: root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n')


@pytest.mark.flaky(max_runs=3)
def test_param_generator_append(document, comm):
    checkbox = Checkbox(value=False)

    def function(value):
        yield Markdown(f"{value}")
        yield Markdown(f"{not value}")

    pane = ParamFunction(bind(function, checkbox), generator_mode='append')

    root = pane.get_root(document, comm)

    wait_until(lambda: len(root.children) == 2, timeout=10_000)
    assert root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'
    assert root.children[1].text == '&lt;p&gt;True&lt;/p&gt;\n'

    checkbox.value = True

    wait_until(lambda: len(root.children) == 2)
    wait_until(lambda: (
        (root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n') and
        (root.children[1].text == '&lt;p&gt;False&lt;/p&gt;\n')
    ))

async def test_param_async_generator(document, comm):
    checkbox = Checkbox(value=False)

    async def function(value):
        yield Markdown(f"{value}")

    pane = ParamFunction(bind(function, checkbox))

    root = pane.get_root(document, comm)

    await async_wait_until(lambda: root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n')

    checkbox.value = True

    await async_wait_until(lambda: root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n')

async def test_param_async_generator_append(document, comm):
    checkbox = Checkbox(value=False)

    async def function(value):
        yield Markdown(f"{value}")
        await asyncio.sleep(0.01)
        yield Markdown(f"{not value}")

    pane = ParamFunction(bind(function, checkbox), generator_mode='append')

    root = pane.get_root(document, comm)

    await async_wait_until(lambda: len(root.children) == 1, interval=10)
    await async_wait_until(lambda: root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n')
    await async_wait_until(lambda: len(root.children) == 2, interval=10)
    assert root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'
    assert root.children[1].text == '&lt;p&gt;True&lt;/p&gt;\n'

    checkbox.value = True

    await async_wait_until(lambda: len(root.children) == 1, interval=10)
    assert root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'
    await async_wait_until(lambda: len(root.children) == 2, interval=10)
    assert root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'
    assert root.children[1].text == '&lt;p&gt;False&lt;/p&gt;\n'


@pytest.mark.flaky(max_runs=3)
def test_param_generator_multiple(document, comm):
    checkbox = Checkbox(value=False)

    def function(value):
        yield Markdown(f"{value}")
        yield Markdown(f"{not value}")

    pane = ParamFunction(bind(function, checkbox))

    root = pane.get_root(document, comm)

    wait_until(lambda: root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n', timeout=10_000)

    checkbox.value = True

    wait_until(lambda: root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n')

async def test_param_async_generator_multiple(document, comm):
    checkbox = Checkbox(value=False)

    async def function(value):
        yield Markdown(f"{value}")
        await asyncio.sleep(0.1)
        yield Markdown(f"{not value}")

    pane = ParamFunction(bind(function, checkbox))

    root = pane.get_root(document, comm)

    assert root.children[0].text == '&lt;pre&gt; &lt;/pre&gt;'
    await asyncio.sleep(0.1)
    assert root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'
    await asyncio.sleep(0.1)
    assert root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'

    checkbox.value = True

    assert root.children[0].text == '&lt;p&gt;True&lt;/p&gt;\n'
    await asyncio.sleep(0.2)
    assert root.children[0].text == '&lt;p&gt;False&lt;/p&gt;\n'

async def test_param_async_generator_abort(document, comm):
    number = NumberInput(value=0)

    async def function(value):
        yield Markdown(f"{value}")
        await asyncio.sleep(0.1)
        yield Markdown(f"{value + 1}")

    pane = ParamFunction(bind(function, number))

    root = pane.get_root(document, comm)

    assert root.children[0].text == '&lt;pre&gt; &lt;/pre&gt;'
    await asyncio.sleep(0.01)
    assert root.children[0].text == '&lt;p&gt;0&lt;/p&gt;\n'

    number.value = 5

    await asyncio.sleep(0.01)
    assert root.children[0].text == '&lt;p&gt;5&lt;/p&gt;\n'
    await asyncio.sleep(0.1)
    assert root.children[0].text == '&lt;p&gt;6&lt;/p&gt;\n'


def test_skip_param(document, comm):
    checkbox = Checkbox(value=False)
    button = Button()

    def layout(value, click):
        if not click:
            raise Skip()
        return Markdown(f"{value}")

    layout = ParamFunction(bind(layout, checkbox, button))

    root = layout.get_root(document, comm)

    div = root.children[0]
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'
    checkbox.value = True
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'
    button.param.trigger('value')
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'

async def test_async_skip_param(document, comm):
    checkbox = Checkbox(value=False)
    button = Button()

    async def layout(value, click):
        if not click:
            raise Skip()
        return Markdown(f"{value}")

    layout = ParamFunction(bind(layout, checkbox, button))

    root = layout.get_root(document, comm)

    div = root.children[0]
    await asyncio.sleep(0.01)
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'
    checkbox.value = True
    await asyncio.sleep(0.01)
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'
    button.param.trigger('value')
    await asyncio.sleep(0.01)
    assert div.text == '&lt;pre&gt; &lt;/pre&gt;'
