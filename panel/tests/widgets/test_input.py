import pytest
from datetime import datetime, date

from bokeh.models.widgets import FileInput as BkFileInput
from panel.widgets import (
    Checkbox, DatePicker, DatetimeInput, DatetimeRangeInput, FileInput,
    LiteralInput, TextInput, StaticText
)


def test_checkbox(document, comm):

    checkbox = Checkbox(value=True, name='Checkbox')

    widget = checkbox.get_root(document, comm=comm)

    assert isinstance(widget, checkbox._widget_type)
    assert widget.labels == ['Checkbox']
    assert widget.active == [0]

    widget.active = []
    checkbox._process_events({'active': []})
    assert checkbox.value == False

    checkbox.value = True
    assert widget.active == [0]


def test_date_picker(document, comm):
    date_picker = DatePicker(name='DatePicker', value=date(2018, 9, 2),
                             start=date(2018, 9, 1), end=date(2018, 9, 10))

    widget = date_picker.get_root(document, comm=comm)

    assert isinstance(widget, date_picker._widget_type)
    assert widget.title == 'DatePicker'
    assert widget.value == '2018-09-02'
    assert widget.min_date == '2018-09-01'
    assert widget.max_date == '2018-09-10'

    widget.value = '2018-09-03'
    date_picker._process_events({'value': '2018-09-03'})
    assert date_picker.value == date(2018, 9, 3)

    date_picker._process_events({'value': date(2018, 9, 5)})
    assert date_picker.value == date(2018, 9, 5)

    date_picker._process_events({'value': date(2018, 9, 6)})
    assert date_picker.value == date(2018, 9, 6)

    date_picker.value = date(2018, 9, 4)
    assert widget.value == '2018-09-04'


def test_file_input(document, comm):
    file_input = FileInput(accept='.txt')

    widget = file_input.get_root(document, comm=comm)

    assert isinstance(widget, BkFileInput)

    file_input._process_events({'mime_type': 'text/plain', 'value': 'U29tZSB0ZXh0Cg==', 'filename': 'testfile'})
    assert file_input.value == b'Some text\n'
    assert file_input.mime_type == 'text/plain'
    assert file_input.accept == '.txt'
    assert file_input.filename == 'testfile'


def test_literal_input(document, comm):

    literal = LiteralInput(value={}, type=dict, name='Literal')

    widget = literal.get_root(document, comm=comm)

    assert isinstance(widget, literal._widget_type)
    assert widget.title == 'Literal'
    assert widget.value == '{}'

    literal._process_events({'value': "{'key': (0, 2)}"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal'

    literal._process_events({'value': "(0, 2)"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal (wrong type)'

    literal._process_events({'value': "invalid"})
    assert literal.value == {'key': (0, 2)}
    assert widget.title == 'Literal (invalid)'

    literal._process_events({'value': "{'key': (0, 3)}"})
    assert literal.value == {'key': (0, 3)}
    assert widget.title == 'Literal'

    with pytest.raises(ValueError):
        literal.value = []


def test_static_text(document, comm):

    text = StaticText(value='ABC', name='Text:')

    widget = text.get_root(document, comm=comm)

    assert isinstance(widget, text._widget_type)
    assert widget.text == '<b>Text:</b>: ABC'

    text.value = 'CBA'
    assert widget.text == '<b>Text:</b>: CBA'

    text.value = '<b>Text:</b>: ABC'
    assert widget.text == '<b>Text:</b>: ABC'


def test_text_input(document, comm):

    text = TextInput(value='ABC', name='Text:')

    widget = text.get_root(document, comm=comm)

    assert isinstance(widget, text._widget_type)
    assert widget.value == 'ABC'
    assert widget.title == 'Text:'

    text._process_events({'value': 'CBA'})
    assert text.value == 'CBA'

    text.value = 'A'
    assert widget.value == 'A'

def test_datetime_input(document, comm):
    dt_input = DatetimeInput(value=datetime(2018, 1, 1),
                             start=datetime(2017, 12, 31),
                             end=datetime(2018, 1, 10),
                             name='Datetime')

    widget = dt_input.get_root(document, comm=comm)

    assert isinstance(widget, dt_input._widget_type)
    assert widget.title == 'Datetime'
    assert widget.value == '2018-01-01 00:00:00'

    dt_input._process_events({'value': '2018-01-01 00:00:01'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime'

    dt_input._process_events({'value': '2018-01-01 00:00:01a'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime (invalid)'

    dt_input._process_events({'value': '2018-01-11 00:00:00'})
    assert dt_input.value == datetime(2018, 1, 1, 0, 0, 1)
    assert widget.title == 'Datetime (out of bounds)'

    dt_input._process_events({'value': '2018-01-02 00:00:01'})
    assert dt_input.value == datetime(2018, 1, 2, 0, 0, 1)
    assert widget.title == 'Datetime'

    with pytest.raises(ValueError):
        dt_input.value = datetime(2017, 12, 30)


def test_datetime_range_input(document, comm):
    dt_input = DatetimeRangeInput(
        value=(datetime(2018, 1, 1), datetime(2018, 1, 3)),
        start=datetime(2017, 12, 31), end=datetime(2018, 1, 10),
        name='Datetime')

    composite = dt_input.get_root(document, comm=comm)
    label, start, end = composite.children

    assert isinstance(composite, dt_input._composite_type._bokeh_model)
    assert label.text == 'Datetime'
    assert start.value == '2018-01-01 00:00:00'
    assert end.value == '2018-01-03 00:00:00'

    dt_input._start._process_events({'value': '2018-01-01 00:00:01'})
    assert dt_input.value == (datetime(2018, 1, 1, 0, 0, 1), datetime(2018, 1, 3))
    assert label.text == 'Datetime'

    dt_input._start._process_events({'value': '2018-01-01 00:00:01a'})
    assert dt_input.value == (datetime(2018, 1, 1, 0, 0, 1), datetime(2018, 1, 3))
    assert label.text == 'Datetime (invalid)'

    dt_input._start._process_events({'value': '2018-01-11 00:00:00'})
    assert dt_input.value == (datetime(2018, 1, 1, 0, 0, 1), datetime(2018, 1, 3))
    assert label.text == 'Datetime (out of bounds)'

    dt_input._end._process_events({'value': '2018-01-11 00:00:00a'})
    assert dt_input.value == (datetime(2018, 1, 1, 0, 0, 1), datetime(2018, 1, 3))
    assert label.text == 'Datetime (out of bounds) (invalid)'

    dt_input._start._process_events({'value': '2018-01-02 00:00:00'})
    dt_input._end._process_events({'value': '2018-01-03 00:00:00'})
    assert dt_input.value == (datetime(2018, 1, 2), datetime(2018, 1, 3))
    assert label.text == 'Datetime'

    dt_input._start._process_events({'value': '2018-01-05 00:00:00'})
    assert dt_input.value == (datetime(2018, 1, 2), datetime(2018, 1, 3))
    assert label.text == 'Datetime (start of range must be <= end)'

    dt_input._start._process_events({'value': '2018-01-01 00:00:00'})
    assert dt_input.value == (datetime(2018, 1, 1), datetime(2018, 1, 3))
    assert label.text == 'Datetime'
