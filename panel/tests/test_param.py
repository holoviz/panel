import os

import param
import pytest

from bokeh.models import (
    Div, Slider, Select, RangeSlider, MultiSelect, Row as BkRow,
    WidgetBox as BkWidgetBox, CheckboxGroup, Toggle, Button,
    TextInput as BkTextInput, Tabs as BkTabs, Column as BkColumn)
from panel.pane import Pane, PaneBase, Matplotlib, Bokeh
from panel.layout import Tabs, Row
from panel.param import Param, ParamMethod, JSONInit

from .test_layout import get_div
from .fixtures import mpl_figure

try:
    import matplotlib as mpl
    mpl.use('Agg')
except:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")


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


def test_param_pane_repr(document, comm):

    class Test(param.Parameterized):
        pass

    assert repr(Pane(Test())) == 'Param(Test)'


def test_param_pane_repr_with_params(document, comm):

    class Test(param.Parameterized):
        a = param.Number()
        b = param.Number()

    assert repr(Pane(Test(), parameters=['a'])) == "Param(Test, parameters=['a'])"


def test_get_model(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    assert isinstance(model, BkColumn)
    assert len(model.children) == 1

    box = model.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 1

    div = box.children[0]
    assert isinstance(div, Div)
    assert div.text == '<b>'+test.name[:-5]+'</b>'


def test_get_model_tabs(document, comm):

    class Test(param.Parameterized):
        pass

    test = Test()
    test_pane = Pane(test, expand_layout=Tabs, _temporary=True)
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
    test.a = ['d']
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


def test_explicit_params(document, comm):
    class Test(param.Parameterized):
        a = param.Boolean(default=False)
        b = param.Integer(default=1)

    test = Test()
    test_pane = Pane(test, parameters=['a'], _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    assert len(model.children[0].children) == 2
    assert isinstance(model.children[0].children[1], CheckboxGroup)


def test_param_precedence(document, comm):
    class Test(param.Parameterized):
        a = param.Number(default=1.2, bounds=(0, 5))

    test = Test()
    test_pane = Pane(test, _temporary=True)

    # Check changing precedence attribute hides and shows widget
    a_param = test.params('a')
    a_param.precedence = -1
    assert test_pane._widgets['a'][0] not in test_pane._widget_box.objects

    a_param.precedence = 1
    assert test_pane._widgets['a'][0] in test_pane._widget_box.objects


def test_expand_param_subobject(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.children[0].children[2]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].active = True
    assert len(model.children) == 2
    _, subpanel = test_pane.layout.objects
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].active = False
    assert len(model.children) == 1
    assert subpanel._callbacks == {}



def test_switch_param_subobject(document, comm):
    class Test(param.Parameterized):
        a = param.ObjectSelector()

    o1 = Test(name='Subobject 1')
    o2 = Test(name='Subobject 2')
    Test.params('a').objects = [o1, o2, 3]
    test = Test(a=o1, name='Nested')
    test_pane = Pane(test, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.children[0].children[2]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].active = True
    assert len(model.children) == 2
    _, subpanel = test_pane.layout.objects
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 3
    div, select, widget = box.children
    assert div.text == '<b>Subobject 1</b>'
    assert isinstance(select, Select)

    # Switch subobject
    test_pane._widgets['a'][0].value = o2    
    _, subpanel = test_pane.layout.objects
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 3
    div, select, widget = box.children
    assert div.text == '<b>Subobject 2</b>'
    assert isinstance(select, Select)

    # Collapse subpanel
    test_pane._widgets['a'][1].active = False
    assert len(model.children) == 1
    assert subpanel._callbacks == {}

    

def test_expand_param_subobject_into_row(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    row = Row()
    test_pane = Pane(test, expand_layout=row, _temporary=True)
    layout = Row(test_pane, row)
    model = layout._get_model(document, comm=comm)

    toggle = model.children[0].children[2]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    test_pane._widgets['a'][1].active = True
    assert len(model.children) == 2
    subpanel = row.objects[0]
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].active = False
    assert len(row.children) == 0
    assert subpanel._callbacks == {}

    
def test_expand_param_subobject_expand(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, _temporary=True, expand=True, expand_button=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.children[0].children[2]
    assert isinstance(toggle, Toggle)

    # Expand subpane
    assert len(model.children) == 2
    _, subpanel = test_pane.layout.objects
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].active = False
    assert len(model.children) == 1
    assert subpanel._callbacks == {}


def test_param_subobject_expand_no_toggle(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, _temporary=True, expand=True,
                     expand_button=False)
    model = test_pane._get_model(document, comm=comm)

    # Assert no toggle was added
    assert len(model.children[0].children) == 2

    # Expand subpane
    assert len(model.children) == 2
    _, subpanel = test_pane.layout.objects
    row = model.children[1]
    assert 'instance' in subpanel._callbacks
    assert isinstance(row, BkColumn)
    assert len(row.children) == 1
    box = row.children[0]
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 2
    div, widget = box.children
    assert div.text == '<b>Nested</b>'
    assert isinstance(widget, BkTextInput)
    

def test_expand_param_subobject_tabs(document, comm):
    class Test(param.Parameterized):
        a = param.Parameter()

    test = Test(a=Test(name='Nested'))
    test_pane = Pane(test, expand_layout=Tabs, _temporary=True)
    model = test_pane._get_model(document, comm=comm)

    toggle = model.tabs[0].child.children[1]
    assert isinstance(toggle, Toggle)

    # Expand subpanel
    test_pane._widgets['a'][1].active = True
    assert len(model.tabs) == 2
    _, subpanel = test_pane.layout.objects
    subtabs = model.tabs[1].child
    assert model.tabs[1].title == 'Nested'
    assert 'instance' in subpanel._callbacks
    assert isinstance(subtabs, BkTabs)
    assert len(subtabs.tabs) == 1
    assert subtabs.tabs[0].title == 'A'

    box = subtabs.tabs[0].child
    assert isinstance(box, BkWidgetBox)
    assert len(box.children) == 1
    widget = box.children[0]
    assert isinstance(widget, BkTextInput)

    # Collapse subpanel
    test_pane._widgets['a'][1].active = False
    assert len(model.tabs) == 1
    assert subpanel._callbacks == {}


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


def test_get_param_method_pane_type():
    assert PaneBase.get_pane_type(View().view) is ParamMethod


def test_param_method_pane(document, comm):
    test = View()
    pane = Pane(test.view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Bokeh)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    inner_row = row.children[0]
    model = inner_row.children[0]
    div = get_div(model)
    assert row.ref['id'] in inner_pane._callbacks
    assert pane._models[row.ref['id']] is inner_row
    assert isinstance(div, Div)
    assert div.text == '0'

    # Update pane
    test.a = 5
    new_model = inner_row.children[0]
    div = get_div(new_model)
    assert inner_pane is pane._pane
    assert div.text == '5'
    assert row.ref['id'] in inner_pane._callbacks
    assert pane._models[row.ref['id']] is inner_row

    # Cleanup pane
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}
    assert inner_pane._callbacks == {}
    assert inner_pane._models == {}


def test_param_method_pane_subobject(document, comm):
    subobject = View(name='Nested', a=42)
    test = View(b=subobject)
    pane = Pane(test.subobject_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Bokeh)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    inner_row = row.children[0]
    model = inner_row.children[0]
    div = get_div(model)

    # Ensure that subobject is being watched
    assert row.ref['id'] in pane._callbacks
    watchers = pane._callbacks[row.ref['id']]
    assert any(w.inst is subobject for w in watchers)
    assert row.ref['id'] in inner_pane._callbacks
    assert pane._models[row.ref['id']] is inner_row
    assert isinstance(div, Div)
    assert div.text == '42'

    # Ensure that switching the subobject triggers update in watchers
    new_subobject = View(name='Nested', a=42)
    test.b = new_subobject
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is inner_row
    watchers = pane._callbacks[row.ref['id']]
    assert not any(w.inst is subobject for w in watchers)
    assert any(w.inst is new_subobject for w in watchers)
    
    # Cleanup pane
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}
    assert inner_pane._callbacks == {}
    assert inner_pane._models == {}

    
@mpl_available
def test_param_method_pane_mpl(document, comm):
    test = View()
    pane = Pane(test.mpl_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Matplotlib)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    inner_row = row.children[0]
    model = inner_row.children[0]
    assert row.ref['id'] in inner_pane._callbacks
    assert pane._models[row.ref['id']] is inner_row
    div = get_div(model)
    text = div.text

    # Update pane
    test.a = 5
    model = inner_row.children[0]
    assert inner_pane is pane._pane
    assert div is get_div(model)
    assert div.text != text
    assert len(inner_pane._callbacks) == 1
    assert row.ref['id'] in inner_pane._callbacks
    assert pane._models[row.ref['id']] is inner_row

    # Cleanup pane
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}
    assert inner_pane._callbacks == {}
    assert inner_pane._models == {}


@mpl_available
def test_param_method_pane_changing_type(document, comm):
    test = View()
    pane = Pane(test.mixed_view)
    inner_pane = pane._pane
    assert isinstance(inner_pane, Matplotlib)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    inner_row = row.children[0]
    model = inner_row.children[0]
    assert row.ref['id'] in inner_pane._callbacks
    
    div = get_div(model)
    text = div.text

    # Update pane
    test.a = 5
    model = inner_row.children[0]
    new_pane = pane._pane
    assert inner_pane._callbacks == {}
    assert isinstance(new_pane, Bokeh)
    div = get_div(model)
    assert isinstance(div, Div)
    assert div.text != text
    assert len(new_pane._callbacks) == 1
    assert row.ref['id'] in new_pane._callbacks

    # Cleanup pane
    new_pane._cleanup(row)
    assert new_pane._callbacks == {}
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
