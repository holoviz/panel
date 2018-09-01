from bokeh.layouts import WidgetBox
from bokeh.models import (
    TextInput as BkTextInput, Div, Slider, RangeSlider as BkRangeSlider,
    CheckboxGroup, Select as BkSelect, MultiSelect as BkMultiSelect
)
from panel.widgets import (
    TextInput, StaticText, FloatSlider, IntSlider, RangeSlider,
    LiteralInput, Checkbox, Select, MultiSelect
)


def test_text_input(document, comm):

    text = TextInput(value='ABC', name='Text:')

    box = text._get_model(document, comm=comm) 

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, BkTextInput)
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
    assert isinstance(widget, Div)
    assert widget.text == '<b>Text:</b>: ABC'

    text.value = 'CBA'
    assert widget.text == '<b>Text:</b>: CBA'


def test_float_slider(document, comm):

    slider = FloatSlider(start=0.1, end=0.5, value=0.4, name='Slider')

    box = slider._get_model(document, comm=comm) 

    assert isinstance(box, WidgetBox)

    widget = box.children[0]
    assert isinstance(widget, Slider)
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
    assert isinstance(widget, Slider)
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
    assert isinstance(widget, BkRangeSlider)
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
    assert isinstance(widget, BkTextInput)
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
    assert isinstance(widget, CheckboxGroup)
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
    assert isinstance(widget, BkSelect)
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
    assert isinstance(widget, BkMultiSelect)
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
