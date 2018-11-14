from bokeh.models import Div as BkDiv, Column as BkColumn, WidgetBox as BkWidgetBox

from panel.interact import interactive
from panel import widgets

from .test_layout import get_div


def test_boolean_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=False)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

def test_string_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a='')
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.TextInput)
    assert widget.value == ''

def test_integer_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=1)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.IntSlider)
    assert widget.value == 1
    assert widget.start == -1
    assert widget.step == 1
    assert widget.end == 3

def test_tuple_int_range_with_step_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4, 2))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.IntSlider)
    assert widget.value == 2
    assert widget.start == 0
    assert widget.step == 2
    assert widget.end == 4

def test_tuple_int_range_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.IntSlider)
    assert widget.value == 2
    assert widget.start == 0
    assert widget.step == 1
    assert widget.end == 4

def test_tuple_float_range_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4, 0.1))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.FloatSlider)
    assert widget.value == 2
    assert widget.start == 0
    assert widget.step == 0.1
    assert widget.end == 4

def test_tuple_float_range_interact_with_default():
    def test(a=3.1):
        return a

    interact_pane = interactive(test, a=(0, 4, 0.1))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.FloatSlider)
    assert widget.value == 3.1
    assert widget.start == 0
    assert widget.step == 0.1
    assert widget.end == 4

def test_tuple_range_interact_with_default_of_different_type():
    def test(a=3.1):
        return a

    interact_pane = interactive(test, a=(0, 4))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.FloatSlider)
    assert widget.value == 3.1
    assert widget.start == 0
    assert widget.end == 4

def test_numeric_list_interact():
    def test(a):
        return a

    interact_pane = interactive(test, a=[1, 3, 5])
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.DiscreteSlider)
    assert widget.value == 1
    assert widget.options == [1, 3, 5]

def test_string_list_interact():
    def test(a):
        return a

    options = ['A', 'B', 'C']
    interact_pane = interactive(test, a=options)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Select)
    assert widget.value == 'A'
    assert widget.options == dict(zip(options, options))

def test_manual_interact():
    def test(a):
        return a

    interact_pane = interactive(test, params={'manual_update': True}, a=False)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False
    assert isinstance(interact_pane._widgets['manual'], widgets.Button)

def test_interact_updates_panel(document, comm):
    def test(a):
        return a

    interact_pane = interactive(test, a=False)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

    column = interact_pane.layout._get_model(document, comm=comm)
    assert isinstance(column, BkColumn)
    div = column.children[1].children[0]
    assert div.text == '<pre>False</pre>'
    
    widget.value = True
    assert div.text == '<pre>True</pre>'

def test_interact_replaces_panel(document, comm):
    def test(a):
        return a if a else BkDiv(text='Test')

    interact_pane = interactive(test, a=False)
    pane = interact_pane._pane
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

    column = interact_pane.layout._get_model(document, comm=comm)
    assert isinstance(column, BkColumn)
    div = get_div(column.children[1].children[0])
    assert div.text == 'Test'
    
    widget.value = True
    assert pane._callbacks == {}
    div = get_div(column.children[1].children[0])
    assert div.text == '<pre>True</pre>'

def test_interact_replaces_model(document, comm):
    def test(a):
        return 'ABC' if a else BkDiv(text='Test')

    interact_pane = interactive(test, a=False)
    pane = interact_pane._pane
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

    column = interact_pane.layout._get_model(document, comm=comm)
    assert isinstance(column, BkColumn)
    box = column.children[1].children[0]
    assert isinstance(box, BkWidgetBox)
    div = box.children[0]
    assert isinstance(div, BkDiv)
    assert div.text == 'Test'
    assert len(interact_pane._callbacks['instance']) == 1
    assert column.ref['id'] in pane._callbacks
    assert pane._models[column.ref['id']] is box
    
    widget.value = True
    assert box.ref['id'] not in pane._callbacks
    assert pane._callbacks == {}
    new_pane = interact_pane._pane
    assert new_pane is not pane
    new_div = column.children[1].children[0]
    assert isinstance(new_div, BkDiv)
    assert new_div.text == '<p>ABC</p>'
    assert len(interact_pane._callbacks['instance']) == 1
    assert column.ref['id'] in new_pane._callbacks
    assert new_pane._models[column.ref['id']] is new_div

    interact_pane._cleanup(column)
    assert len(interact_pane._callbacks) == 1
    assert pane._callbacks == {}
