import param

from bokeh.models import (
    Div, Slider, Select, RangeSlider, MultiSelect, Row as BkRow,
    WidgetBox as BkWidgetBox, CheckboxGroup)
from panel.layout import Row
from panel.panels import Panel
from panel.param import ParamPanel


def test_instantiate_from_class():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Panel(Test), ParamPanel)


def test_instantiate_from_instance():

    class Test(param.Parameterized):

        a = param.Number()

    assert isinstance(Panel(Test()), ParamPanel)


def test_get_model(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

    assert isinstance(model, BkRow)
    assert len(model.children) == 1

    box = model.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 1

    div = box.children[0]
    assert isinstance(div, Div)
    assert div.text == '<b>'+test.name+'</b>'


def test_number_param(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test()
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
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
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
    a_param.constant = False
    test.a = False
    assert checkbox.active == [0]
    assert checkbox.disabled == True


def test_range_param(document, comm):
    class Test(param.Parameterized):
        a = param.Range(default=(0.1, 0.5), bounds=(0, 1.1))

    test = Test()
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
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
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
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
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
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
    test_panel = Panel(test)
    model = test_panel._get_model(document, comm=comm)

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
    test_panel._cleanup(model)
    a_param.constant = False
    a_param.objects = [1, 'c', 'd']
    test.a = 'd'
    assert slider.value == ['c', '1']
    assert slider.options == ['c', 'd', '1'] 
    assert slider.disabled == True
