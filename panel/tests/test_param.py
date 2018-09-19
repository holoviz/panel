import os
import param

from bokeh.models import (
    Div, Slider, Select, RangeSlider, MultiSelect, Row as BkRow,
    WidgetBox as BkWidgetBox, CheckboxGroup, Toggle, Button,
    TextInput as BkTextInput, Tabs as BkTabs)
from panel.pane import Pane
from panel.layout import Tabs
from panel.param import Param, JSONInit


def test_instantiate_from_class():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test), Param)


def test_instantiate_from_parameters():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test.param), Param)


def test_instantiate_from_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test()), Param)


def test_instantiate_from_parameters_on_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Pane(Test().param), Param)


def test_get_model(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    assert isinstance(model, BkRow)
    assert len(model.children) == 1

    box = model.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 1

    div = box.children[0]
    assert isinstance(div, Div)
    assert div.text == '<b>'+test.name+'</b>'


def test_get_model_tabs(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Pane(test, subpanel_layout=Tabs, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 1

    box = model.tabs[0].child
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 0


def test_number_param(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    slider = model.children[0].children[1]
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
    a_param = test.params('a')
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
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    checkbox = model.children[0].children[1]
    assert isinstance(checkbox, CheckboxGroup)
    assert checkbox.labels == ['A']
    assert checkbox.active == []
    assert checkbox.disabled == False

    # Check changing param value updates widget
    test.a = True
    assert checkbox.active == [0]

    # Check changing param attribute updates widget
    a_param = test.params('a')
    a_param.constant = True
    assert checkbox.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    test.a = False
    assert checkbox.active == [0]
    assert checkbox.disabled == True


def test_range_param(document, comm):
    class Test(param.Parameterized):
        a = param.Range(default=(0.1, 0.5), bounds=(0, 1.1))

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    widget = model.children[0].children[1]
    assert isinstance(widget, RangeSlider)
    assert widget.start == 0
    assert widget.end == 1.1
    assert widget.value == (0.1, 0.5)

    # Check changing param value updates widget
    test.a = (0.2, 0.4)
    assert widget.value == (0.2, 0.4)

    # Check changing param attribute updates widget
    a_param = test.params('a')
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
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    slider = model.children[0].children[1]
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
    a_param = test.params('a')
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
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    slider = model.children[0].children[1]
    assert isinstance(slider, Select)
    assert slider.options == ['1', 'b', 'c']
    assert slider.value == 'b'
    assert slider.disabled == False

    # Check changing param value updates widget
    test.a = 1
    assert slider.value == '1'

    # Check changing param attribute updates widget
    a_param = test.params('a')
    a_param.objects = ['c', 'd', '1']
    assert slider.options == ['c', 'd', '1']

    a_param.constant = True
    assert slider.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.objects = [1, 'c', 'd']
    test.a = 'd'
    assert slider.value == '1'
    assert slider.options == ['c', 'd', '1']
    assert slider.disabled == True


def test_list_selector_param(document, comm):
    class Test(param.Parameterized):
        a = param.ListSelector(default=['b', 1], objects=[1, 'b', 'c'])

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    slider = model.children[0].children[1]
    assert isinstance(slider, MultiSelect)
    assert slider.options == ['1', 'b', 'c']
    assert slider.value == ['b', '1']
    assert slider.disabled == False

    # Check changing param value updates widget
    test.a = ['c', 1]
    assert slider.value == ['c', '1']

    # Check changing param attribute updates widget
    a_param = test.params('a')
    a_param.objects = ['c', 'd', '1']
    assert slider.options == ['c', 'd', '1']

    a_param.constant = True
    assert slider.disabled == True

    # Ensure cleanup works
    test_pane._cleanup(model)
    a_param.constant = False
    a_param.objects = [1, 'c', 'd']
    test.a = 'd'
    assert slider.value == ['c', '1']
    assert slider.options == ['c', 'd', '1']
    assert slider.disabled == True


def test_action_param(document, comm):
    class Test(param.Parameterized):
        a = param.Action(lambda x: x.b.append(1))
        b = param.List(default=[])

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    slider = model.children[0].children[1]
    assert isinstance(slider, Button)


def test_expand_param_subobject(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.children[0].children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'].active = True
    assert len(model.children) == 2
    _, subpanel = test_pane._layout.objects
    row = model.children[1]
    assert 'object' in subpanel._callbacks
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'].active = False
    assert len(model.children) == 1
    assert subpanel._callbacks == {}


def test_expand_param_subobject_tabs(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, subpanel_layout=Tabs, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.tabs[0].child.children[0]
    assert isinstance(toggle, Toggle)

    # Expand subpanel
    test_pane._widgets['a'].active = True
    assert len(model.tabs) == 2
    _, subpanel = test_pane._layout.objects
    subtabs = model.tabs[1].child
    assert model.tabs[1].title == 'Nested'
    assert 'object' in subpanel._callbacks
    assert isinstance(subtabs, BkTabs)
    assert len(subtabs.tabs) == 1
    assert subtabs.tabs[0].title == 'Nested'

    box = subtabs.tabs[0].child
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 1
    widget = box.children[0]
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'].active = False
    assert len(model.tabs) == 1
    assert subpanel._callbacks == {}


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
