from collections import OrderedDict
from datetime import datetime

from bokeh.layouts import WidgetBox
from bokeh.models import Div as BkDiv, Slider as BkSlider
from panel.widgets import (
    TextInput, StaticText, FloatSlider, IntSlider, RangeSlider,
    LiteralInput, Checkbox, Select, MultiSelect, Button, Toggle,
    DatePicker, DateRangeSlider, DiscreteSlider
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


def test_static_text(document, comm):

    text = StaticText(value='ABC', name='Text:')

    box = text._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, text._widget_type)
    assert widget.text == '<b>Text:</b>: ABC'

    text.value = 'CBA'
    assert widget.text == '<b>Text:</b>: CBA'


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


def test_range_slider(document, comm):

    slider = RangeSlider(start=0, end=3, value=(0, 3), name='Slider')

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
    select = Select(options={'A': 'A', '1': 1}, value=1, name='Select')

    box = select._get_model(document, comm=comm)

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, select._widget_type)
    assert widget.title == 'Select'
    assert widget.value == '1'
    assert widget.options == ['A', '1']

    widget.value = '1'
    select._comm_change({'value': 'A'})
    assert select.value == 'A'

    widget.value = '1'
    select._comm_change({'value': '1'})
    assert select.value == 1

    select.value = 'A'
    assert widget.value == 'A'


def test_multi_select(document, comm):
    select = MultiSelect(options={'A': 'A', '1': 1, 'C': object},
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
