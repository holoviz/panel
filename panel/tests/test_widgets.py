import pytest

from collections import OrderedDict
from datetime import datetime

from bokeh.layouts import WidgetBox
from bokeh.models import Div as BkDiv, Slider as BkSlider
from panel.models.widgets import Player as BkPlayer
from panel.util import block_comm
from panel.widgets import (
    TextInput, StaticText, FloatSlider, IntSlider, RangeSlider,
    LiteralInput, Checkbox, Select, MultiSelect, Button, Toggle,
    DatePicker, DateRangeSlider, DiscreteSlider, DatetimeInput,
    RadioButtons, ToggleButtons, CrossSelector, DiscretePlayer
)


def test_text_input(document, comm):

    text = TextInput(value='ABC', name='Text:')

    box = text._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, text._widget_type)
    assert widget.value == 'ABC'
    assert widget.title == 'Text:'

    text._comm_change({'value': 'CBA'})
    assert text.value == 'CBA'

    text.value = 'A'
    assert widget.value == 'A'
    assert repr(text) == "TextInput(name='Text:', value='A')"


def test_widget_triggers_events(document, comm):
    """
    Ensure widget events don't get swallowed in comm mode
    """
    text = TextInput(value='ABC', name='Text:')

    box = text._get_root(document, comm=comm)
    widget = box.children[0]
    document.add_root(box)
    document.hold()

    # Simulate client side change
    widget.value = '123'
    document._held_events = document._held_events[:-1]

    # Set new value
    with block_comm():
        text.value = '123'

    assert len(document._held_events) == 1
    event = document._held_events[0]
    assert event.model is widget
    assert event.attr == 'value'
    assert event.new == '123'


def test_static_text(document, comm):

    text = StaticText(value='ABC', name='Text:')

    box = text._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, text._widget_type)
    assert widget.text == '<b>Text:</b>: ABC'

    text.value = 'CBA'
    assert widget.text == '<b>Text:</b>: CBA'
    assert repr(text) == "StaticText(name='Text:', value='CBA')"


def test_float_slider(document, comm):

    slider = FloatSlider(start=0.1, end=0.5, value=0.4, name='Slider')

    box = slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 0.1
    assert widget.start == 0.1
    assert widget.end == 0.5
    assert widget.value == 0.4

    slider._comm_change({'value': 0.2})
    assert slider.value == 0.2

    slider.value = 0.3
    assert widget.value == 0.3
    assert repr(slider) == "FloatSlider(end=0.5, name='Slider', start=0.1, value=0.3)"


def test_int_slider(document, comm):

    slider = IntSlider(start=0, end=3, value=1, name='Slider')

    box = slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.value == 1

    slider._comm_change({'value': 2})
    assert slider.value == 2

    slider.value = 0
    assert widget.value == 0
    assert repr(slider) == "IntSlider(end=3, name='Slider')"


def test_range_slider(document, comm):

    slider = RangeSlider(start=0., end=3, value=(0, 3), name='Slider')

    box = slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 0.1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.value == (0, 3)

    slider._comm_change({'value': (0, 2)})
    assert slider.value == (0, 2)

    slider.value = (0, 1)
    assert widget.value == (0, 1)
    assert repr(slider) == "RangeSlider(end=3, name='Slider', start=0.0, value=(0, 1))"


def test_literal_input(document, comm):

    literal = LiteralInput(value={}, type=dict, name='Literal')

    box = literal._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, literal._widget_type)
    assert widget.title == 'Literal'
    assert widget.value == '{}'

    literal._comm_change({'value': "{'key': (0, 2)}"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal'

    literal._comm_change({'value': "(0, 2)"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal (wrong type)'

    literal._comm_change({'value': "invalid"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal (invalid)'

    literal._comm_change({'value': "{'key': (0, 3)}"})
    assert literal.value == {'key': (0, 3)}
    assert widget.title == 'Literal'

    with pytest.raises(ValueError):
        literal.value = []


def test_datetime_input(document, comm):
    dt_input = DatetimeInput(value=datetime(2018, 1, 1),
                             start=datetime(2017, 12, 31),
                             end=datetime(2018, 1, 10),
                             name='Datetime')

    box = dt_input._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, dt_input._widget_type)
    assert widget.title == 'Datetime'
    assert widget.value == '2018-01-01 00:00:00'

    dt_input._comm_change({'value': '2018-01-01 00:00:01'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime'

    dt_input._comm_change({'value': '2018-01-01 00:00:01a'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime (invalid)'

    dt_input._comm_change({'value': '2018-01-11 00:00:00'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime (out of bounds)'

    dt_input._comm_change({'value': '2018-01-02 00:00:01'})
    assert dt_input.value == datetime(2018, 1, 2, 0, 0, 1)
    assert widget.title == 'Datetime'

    with pytest.raises(ValueError):
        dt_input.value = datetime(2017, 12, 30)


def test_checkbox(document, comm):

    checkbox = Checkbox(value=True, name='Checkbox')

    box = checkbox._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, checkbox._widget_type)
    assert widget.labels == ['Checkbox']
    assert widget.active == [0]

    widget.active = []
    checkbox._comm_change({'active': []})
    assert checkbox.value == False

    checkbox.value = True
    assert widget.active == [0]


def test_select_list_constructor():
    select = Select(options=['A', 1], value=1)
    assert select.options == {'A': 'A', '1': 1}


def test_select(document, comm):
    opts = {'A': 'a', '1': 1}
    select = Select(options=opts, value=opts['1'], name='Select')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == '1'
    assert widget.options == ['A', '1']

    widget.value = '1'
    select._comm_change({'value': 'A'})
    assert select.value == opts['A']

    widget.value = '1'
    select._comm_change({'value': '1'})
    assert select.value == opts['1']

    select.value = opts['A']
    assert widget.value == 'A'


def test_select_mutables(document, comm):
    opts = OrderedDict([('A', [1,2,3]), ('B', [2,4,6]), ('C', dict(a=1,b=2))])
    select = Select(options=opts, value=opts['B'], name='Select')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == 'B'
    assert widget.options == ['A', 'B', 'C']

    widget.value = 'B'
    select._comm_change({'value': 'A'})
    assert select.value == opts['A']

    widget.value = 'B'
    select._comm_change({'value': 'B'})
    assert select.value == opts['B']

    select.value = opts['A']
    assert widget.value == 'A'


def test_multi_select(document, comm):
    select = MultiSelect(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                         value=[object, 1], name='Select')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == ['C', '1']
    assert widget.options == ['A', '1', 'C']

    widget.value = ['1']
    select._comm_change({'value': ['1']})
    assert select.value == [1]

    widget.value = ['A', 'C']
    select._comm_change({'value': ['A', 'C']})
    assert select.value == ['A', object]

    select.value = [object, 'A']
    assert widget.value == ['C', 'A']


def test_toggle_buttons(document, comm):
    select = ToggleButtons(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                           value=[1, object], name='ToggleButtons')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.active == [1, 2]
    assert widget.labels == ['A', '1', 'C']

    widget.active = [2]
    select._comm_change({'active': [2]})
    assert select.value == [object]

    widget.active = [0, 2]
    select._comm_change({'active': [0, 2]})
    assert select.value == ['A', object]

    select.value = [object, 'A']
    assert widget.active == [2, 0]


def test_radio_buttons(document, comm):
    select = RadioButtons(options=OrderedDict([('A', 'A'), ('1', 1), ('C', object)]),
                          value=[1, object], name='RadioButtons')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.active == [1, 2]
    assert widget.labels == ['A', '1', 'C']

    widget.active = [1]
    select._comm_change({'active': [1]})
    assert select.value == [1]

    widget.active = [0, 2]
    select._comm_change({'active': [0, 2]})
    assert select.value == ['A', object]

    select.value = [object, 'A']
    assert widget.active == [2, 0]
    

def test_button(document, comm):
    button = Button(name='Button')

    box = button._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, button._widget_type)
    assert widget.clicks == 0
    assert widget.label == 'Button'

    widget.clicks = 1
    button._comm_change({'clicks': widget.clicks})
    assert button.clicks == 1


def test_toggle(document, comm):
    toggle = Toggle(name='Toggle', active=True)

    box = toggle._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, toggle._widget_type)
    assert widget.active == True
    assert widget.label == 'Toggle'

    widget.active = False
    toggle._comm_change({'active': widget.active})
    assert toggle.active == False

    toggle.active = True
    assert widget.active == True


def test_date_picker(document, comm):
    date_picker = DatePicker(name='DatePicker', value=datetime(2018, 9, 2),
                             start=datetime(2018, 9, 1), end=datetime(2018, 9, 10))

    box = date_picker._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, date_picker._widget_type)
    assert widget.title == 'DatePicker'
    assert widget.value == datetime(2018, 9, 2)
    assert widget.min_date == datetime(2018, 9, 1)
    assert widget.max_date == datetime(2018, 9, 10)

    widget.value = 'Mon Sep 03 2018'
    date_picker._comm_change({'value': 'Mon Sep 03 2018'})
    assert date_picker.value == datetime(2018, 9, 3)

    date_picker.value = datetime(2018, 9, 4)
    assert widget.value == date_picker.value


def test_date_range_slider(document, comm):
    date_slider = DateRangeSlider(name='DateRangeSlider',
                                  value=(datetime(2018, 9, 2), datetime(2018, 9, 4)),
                                  start=datetime(2018, 9, 1), end=datetime(2018, 9, 10))

    box = date_slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, date_slider._widget_type)
    assert widget.title == 'DateRangeSlider'
    assert widget.value == (datetime(2018, 9, 2), datetime(2018, 9, 4))
    assert widget.start == datetime(2018, 9, 1)
    assert widget.end == datetime(2018, 9, 10)

    epoch = datetime(1970, 1, 1)
    widget.value = ((datetime(2018, 9, 3)-epoch).total_seconds()*1000,
                    (datetime(2018, 9, 6)-epoch).total_seconds()*1000)
    date_slider._comm_change({'value': widget.value})
    assert date_slider.value == (datetime(2018, 9, 3), datetime(2018, 9, 6))

    date_slider.value = (datetime(2018, 9, 4), datetime(2018, 9, 6))
    assert widget.value == date_slider.value



def test_discrete_slider(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=[0.1, 1, 10, 100])

    box = discrete_slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    label = box.children[0]
    widget = box.children[1]
    assert isinstance(label, BkDiv)
    assert isinstance(widget, BkSlider)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1
    assert label.text == '<b>DiscreteSlider</b>: 1'

    widget.value = 2
    discrete_slider._comm_change({'value': 2})
    assert discrete_slider.value == 10
    assert label.text == '<b>DiscreteSlider</b>: 10'

    discrete_slider.value = 100
    assert widget.value == 3
    assert label.text == '<b>DiscreteSlider</b>: 100'



def test_discrete_slider_options_dict(document, comm):
    options = OrderedDict([('0.1', 0.1), ('1', 1), ('10', 10), ('100', 100)])
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=options)

    box = discrete_slider._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    label = box.children[0]
    widget = box.children[1]
    assert isinstance(label, BkDiv)
    assert isinstance(widget, BkSlider)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1
    assert label.text == '<b>DiscreteSlider</b>: 1'

    widget.value = 2
    discrete_slider._comm_change({'value': 2})
    assert discrete_slider.value == 10
    assert label.text == '<b>DiscreteSlider</b>: 10'

    discrete_slider.value = 100
    assert widget.value == 3
    assert label.text == '<b>DiscreteSlider</b>: 100'



def test_cross_select_constructor(document, comm):
    cross_select = CrossSelector(options=['A', 'B', 'C', 1, 2, 3], value=['A', 1])

    assert cross_select._lists[True].options == {'A': 'A', '1': '1'}
    assert cross_select._lists[False].options == {'B': 'B', 'C': 'C', '2': '2', '3': '3'}

    # Change selection
    cross_select.value = ['B', 2]
    assert cross_select._lists[True].options == {'B': 'B', '2': '2'}
    assert cross_select._lists[False].options == {'A': 'A', 'C': 'C', '1': '1', '3': '3'}

    # Change options
    cross_select.options = {'D': 'D', '4': 4}
    assert cross_select._lists[True].options == {}
    assert cross_select._lists[False].options == {'D': 'D', '4': '4'}

    # Query unselected item
    cross_select._search[False].value = 'D'
    assert cross_select._lists[False].value == ['D']

    # Move queried item
    cross_select._buttons[True].param.trigger('clicks')
    assert cross_select._lists[False].options == {'4': '4'}
    assert cross_select._lists[False].value == []
    assert cross_select._lists[True].options == {'D': 'D'}
    assert cross_select._lists[False].value == []

    # Query selected item
    cross_select._search[True].value = 'D'
    cross_select._buttons[False].param.trigger('clicks')
    assert cross_select._lists[False].options == {'D': 'D', '4': '4'}
    assert cross_select._lists[False].value == ['D']
    assert cross_select._lists[True].options == {}

    # Clear query
    cross_select._search[False].value = ''
    assert cross_select._lists[False].value == []


def test_discrete_player(document, comm):
    discrete_player = DiscretePlayer(name='DiscretePlayer', value=1,
                                     options=[0.1, 1, 10, 100])

    box = discrete_player._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, BkPlayer)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1

    widget.value = 2
    discrete_player._comm_change({'value': 2})
    assert discrete_player.value == 10

    discrete_player.value = 100
    assert widget.value == 3
