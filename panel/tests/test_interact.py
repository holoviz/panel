from datetime import date

from bokeh.models import Column as BkColumn, Div as BkDiv

from panel import widgets
from panel.interact import interactive
from panel.models import HTML as BkHTML
from panel.pane import HTML


def test_interact_title():
    def test(a):
        return a

    interact_pane = interactive(test, a=False, params={'name': 'Test'})
    html = interact_pane.widget_box[0]
    assert isinstance(html, HTML)
    assert html.object == '<h2>Test</h2>'

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

def test_tuple_range_interact_with_step_and_value():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4, 1, 0))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.IntSlider)
    assert widget.value == 0
    assert widget.start == 0
    assert widget.step == 1
    assert widget.end == 4

def test_tuple_float_range_interact_with_step_and_value():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4, .1, 0))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.FloatSlider)
    assert widget.value == 0
    assert widget.start == 0
    assert widget.step == .1
    assert widget.end == 4

def test_tuple_range_interact_with_no_step_and_value():
    def test(a):
        return a

    interact_pane = interactive(test, a=(0, 4, None, 0))
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.IntSlider)
    assert widget.value == 0
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
    assert widget.options == options

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

    column = interact_pane.layout.get_root(document, comm=comm)
    assert isinstance(column, BkColumn)
    div = column.children[1].children[0]
    assert div.text == '&lt;pre&gt;False&lt;/pre&gt;'

    widget.value = True
    assert div.text == '&lt;pre&gt;True&lt;/pre&gt;'

def test_interact_replaces_panel(document, comm):
    def test(a):
        return a if a else BkDiv(text='Test')

    interact_pane = interactive(test, a=False)
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

    column = interact_pane.layout.get_root(document, comm=comm)
    assert isinstance(column, BkColumn)
    div = column.children[1].children[0]
    assert div.text == 'Test'

    widget.value = True
    div = column.children[1].children[0]
    assert div.text == '&lt;pre&gt;True&lt;/pre&gt;'

def test_interact_replaces_model(document, comm):
    def test(a):
        return 'ABC' if a else BkDiv(text='Test')

    interact_pane = interactive(test, a=False)
    pane = interact_pane._pane
    widget = interact_pane._widgets['a']
    assert isinstance(widget, widgets.Checkbox)
    assert widget.value == False

    column = interact_pane.layout.get_root(document, comm=comm)
    assert isinstance(column, BkColumn)
    div = column.children[1].children[0]
    assert isinstance(div, BkDiv)
    assert div.text == 'Test'
    assert pane._models[column.ref['id']][0] is div

    widget.value = True
    new_pane = interact_pane._pane
    assert new_pane is not pane
    new_div = column.children[1].children[0]
    assert isinstance(new_div, BkHTML)
    assert new_div.text.endswith('&lt;p&gt;ABC&lt;/p&gt;\n')
    assert new_pane._models[column.ref['id']][0] is new_div

    interact_pane._cleanup(column)
    assert len(interact_pane._internal_callbacks) == 6
    # Note one of the callbacks is Viewable._set_background
    # the counter should be reduced when this function is removed.


def test_interact_throttled():
    slider_dict = {
        "DateSlider": dict(start=date(2018, 9, 1), end=date(2018, 9, 10)),
        "DateRangeSlider": dict(
            start=date(2018, 9, 1),
            end=date(2018, 9, 10),
            value=(date(2018, 9, 2), date(2018, 9, 4)),
        ),
        "DiscreteSlider": dict(
            options=[0.1, 1, 10, 100],
            value=1,
        ),
        "FloatSlider": dict(start=1, end=10, value=5),
        "IntSlider": dict(start=1, end=10, value=5),
        "IntRangeSlider": dict(start=1, end=10, value=(2, 5)),
        "RangeSlider": dict(start=1, end=10, value=(2, 5)),
    }

    func = lambda x: repr(x)
    throttled = True

    for slider, kwargs in slider_dict.items():
        widget = getattr(widgets, slider)(**kwargs)
        try:
            interactive(func, x=widget, throttled=throttled)
            assert True
        except Exception as e:
            assert False, e
