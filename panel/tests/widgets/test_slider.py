from collections import OrderedDict
from datetime import date, datetime

import pytest

from bokeh.models import (
    Column as BkColumn, Div as BkDiv, Row as BkRow, Slider as BkSlider,
)

from panel import config
from panel.widgets import (
    DateRangeSlider, DateSlider, DiscreteSlider, EditableFloatSlider,
    EditableIntSlider, EditableRangeSlider, FloatSlider, IntSlider,
    RangeSlider, StaticText,
)


def test_float_slider(document, comm):

    slider = FloatSlider(start=0.1, end=0.5, value=0.4, name='Slider')

    widget = slider.get_root(document, comm=comm)

    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 0.1
    assert widget.start == 0.1
    assert widget.end == 0.5
    assert widget.value == 0.4

    slider._process_events({'value': 0.2})
    assert slider.value == 0.2
    slider._process_events({'value_throttled': 0.2})
    assert slider.value_throttled == 0.2

    slider.value = 0.3
    assert widget.value == 0.3

    # Testing throttled mode
    with config.set(throttled=True):
        slider._process_events({'value': 0.4})
        assert slider.value == 0.3  # no change
        slider._process_events({'value_throttled': 0.4})
        assert slider.value == 0.4

        slider.value = 0.5
        assert widget.value == 0.5


def test_int_slider(document, comm):

    slider = IntSlider(start=0, end=3, value=1, name='Slider')

    widget = slider.get_root(document, comm=comm)

    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.value == 1

    slider._process_events({'value': 2})
    assert slider.value == 2
    slider._process_events({'value_throttled': 2})
    assert slider.value_throttled == 2

    slider.value = 0
    assert widget.value == 0

    # Testing that value matches start value if value not set.
    slider_2 = IntSlider(start=1, end=3, name='Slider_2')
    widget_2 = slider_2.get_root(document, comm=comm)
    assert widget_2.value == widget_2.start

    # Testing throttled mode
    with config.set(throttled=True):
        slider._process_events({'value': 1})
        assert slider.value == 0  # no change
        slider._process_events({'value_throttled': 1})
        assert slider.value == 1

        slider.value = 2
        assert widget.value == 2


def test_range_slider(document, comm):

    slider = RangeSlider(start=0., end=3, value=(0, 3), name='Slider')

    widget = slider.get_root(document, comm=comm)

    assert isinstance(widget, slider._widget_type)
    assert widget.title == 'Slider'
    assert widget.step == 0.1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.value == (0, 3)

    slider._process_events({'value': (0, 2)})
    assert slider.value == (0, 2)
    slider._process_events({'value_throttled': (0, 2)})
    assert slider.value_throttled == (0, 2)

    slider.value = (0, 1)
    assert widget.value == (0, 1)

    # Testing throttled mode
    with config.set(throttled=True):
        slider._process_events({'value': (1, 2)})
        assert slider.value == (0, 1)  # no change
        slider._process_events({'value_throttled': (1, 2)})
        assert slider.value == (1, 2)

        slider.value = (2, 3)
        assert widget.value == (2, 3)


def test_date_slider(document, comm):
    date_slider = DateSlider(name='DateSlider',
                             value=date(2018, 9, 4),
                             start=date(2018, 9, 1), end=date(2018, 9, 10))

    widget = date_slider.get_root(document, comm=comm)

    assert isinstance(widget, date_slider._widget_type)
    assert widget.title == 'DateSlider'
    assert widget.value == 1536019200000
    assert widget.start == 1535760000000.0
    assert widget.end == 1536537600000.0

    epoch = datetime(1970, 1, 1)
    widget.value = (datetime(2018, 9, 3)-epoch).total_seconds()*1000
    date_slider._process_events({'value': widget.value})
    assert date_slider.value == date(2018, 9, 3)
    date_slider._process_events({'value_throttled': (datetime(2018, 9, 3)-epoch).total_seconds()*1000})
    assert date_slider.value_throttled == date(2018, 9, 3)

    # Test raw timestamp value:
    date_slider._process_events({'value': (datetime(2018, 9, 4)-epoch).total_seconds()*1000.0})
    assert date_slider.value == date(2018, 9, 4)
    date_slider._process_events({'value_throttled': (datetime(2018, 9, 4)-epoch).total_seconds()*1000.0})
    assert date_slider.value_throttled == date(2018, 9, 4)

    date_slider.value = date(2018, 9, 6)
    assert widget.value == 1536192000000

    # Testing throttled mode
    epoch_time = lambda dt: (dt - epoch).total_seconds() * 1000
    with config.set(throttled=True):
        date_slider._process_events({'value': epoch_time(datetime(2021, 5, 15))})
        assert date_slider.value == date(2018, 9, 6)  # no change
        date_slider._process_events({'value_throttled': epoch_time(datetime(2021, 5, 15))})
        assert date_slider.value == date(2021, 5, 15)

        date_slider.value = date(2021, 5, 12)
        assert widget.value == 1620777600000


def test_date_range_slider(document, comm):
    date_slider = DateRangeSlider(name='DateRangeSlider',
                                  value=(datetime(2018, 9, 2), datetime(2018, 9, 4)),
                                  start=datetime(2018, 9, 1), end=datetime(2018, 9, 10))

    widget = date_slider.get_root(document, comm=comm)

    assert isinstance(widget, date_slider._widget_type)
    assert widget.title == 'DateRangeSlider'
    assert widget.value == (1535846400000, 1536019200000)
    assert widget.start == 1535760000000
    assert widget.end == 1536537600000

    epoch = datetime(1970, 1, 1)
    widget.value = ((datetime(2018, 9, 3)-epoch).total_seconds()*1000,
                    (datetime(2018, 9, 6)-epoch).total_seconds()*1000)
    date_slider._process_events({'value': widget.value})
    assert date_slider.value == (datetime(2018, 9, 3), datetime(2018, 9, 6))
    value_throttled = ((datetime(2018, 9, 3)-epoch).total_seconds()*1000,
                    (datetime(2018, 9, 6)-epoch).total_seconds()*1000)
    date_slider._process_events({'value_throttled': value_throttled})
    assert date_slider.value == (datetime(2018, 9, 3), datetime(2018, 9, 6))

    date_slider.value = (datetime(2018, 9, 4), datetime(2018, 9, 6))
    assert widget.value == (1536019200000, 1536192000000)

    # Testing throttled mode
    epoch_time = lambda dt: (dt - epoch).total_seconds() * 1000
    epoch_times = lambda *dts: tuple(map(epoch_time, dts))
    with config.set(throttled=True):
        date_slider._process_events(
            {'value': epoch_times(datetime(2021, 2, 15), datetime(2021, 5, 15))}
        )
        assert date_slider.value == (datetime(2018, 9, 4), datetime(2018, 9, 6))  # no change
        date_slider._process_events(
            {'value_throttled': epoch_times(datetime(2021, 2, 15), datetime(2021, 5, 15))}
        )
        assert date_slider.value == (datetime(2021, 2, 15), datetime(2021, 5, 15))

        date_slider.value = (datetime(2021, 2, 12), datetime(2021, 5, 12))
        assert widget.value == (1613088000000, 1620777600000)


def test_discrete_slider(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=[0.1, 1, 10, 100])

    box = discrete_slider.get_root(document, comm=comm)

    label = box.children[0]
    widget = box.children[1]
    assert isinstance(label, BkDiv)
    assert isinstance(widget, BkSlider)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1
    assert label.text == 'DiscreteSlider: <b>1</b>'

    # widget.value = 2
    discrete_slider._slider._process_events({'value': 2})
    assert discrete_slider.value == 10
    discrete_slider._slider._process_events({'value_throttled': 2})
    assert discrete_slider.value_throttled == 10

    discrete_slider.value = 100
    assert widget.value == 3

    # Testing throttled mode
    with config.set(throttled=True):
        discrete_slider._slider._process_events({'value': 0.1})
        assert discrete_slider.value == 100  # no change
        discrete_slider._slider._process_events({'value_throttled': 0.1})
        assert discrete_slider.value == 0.1

        discrete_slider.value = 1
        assert widget.value == 1


def test_discrete_slider_label_update(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=[0.1, 1, 10, 100])

    box = discrete_slider.get_root(document, comm=comm)

    discrete_slider.value = 100

    assert box.children[0].text == 'DiscreteSlider: <b>100</b>'


def test_discrete_slider_name_update(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=[0.1, 1, 10, 100])


    box = discrete_slider.get_root(document, comm=comm)

    discrete_slider.name = 'Blah'

    assert box.children[0].text == 'Blah: <b>1</b>'


def test_discrete_slider_no_options(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider')


    box = discrete_slider.get_root(document, comm=comm)

    assert box.children[0].text == 'DiscreteSlider: <b>-</b>'
    assert box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1


    discrete_slider.options = [0, 1]

    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert not box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1


def test_discrete_slider_single_option(document, comm):
    discrete_slider = DiscreteSlider(name='DiscreteSlider', options=[0])


    box = discrete_slider.get_root(document, comm=comm)

    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1


    discrete_slider.options = [0, 1]

    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert not box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1


def test_discrete_slider_disabled(document, comm):
    # Check that the widget can be disabled on instantiation
    discrete_slider = DiscreteSlider(name='DiscreteSlider', options=[0, 1], disabled=True)

    box = discrete_slider.get_root(document, comm=comm)

    # Check that the widget
    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1

    # Check that the widget can be enabled after instantiation
    discrete_slider.disabled = False

    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert not box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1

    # Widget can't be disabled if it has 0 or 1 option only.
    discrete_slider.options = [0]
    discrete_slider.disabled = True

    assert box.children[0].text == 'DiscreteSlider: <b>0</b>'
    assert box.children[1].disabled
    assert box.children[1].start == 0
    assert box.children[1].end == 1


def test_discrete_date_slider(document, comm):
    dates = OrderedDict([('2016-01-0%d' % i, datetime(2016, 1, i)) for i in range(1, 4)])
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=dates['2016-01-02'],
                                     options=dates)

    box = discrete_slider.get_root(document, comm=comm)

    assert isinstance(box, BkColumn)

    label = box.children[0]
    widget = box.children[1]
    assert isinstance(label, BkDiv)
    assert isinstance(widget, BkSlider)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 2
    assert widget.step == 1
    assert label.text == 'DiscreteSlider: <b>2016-01-02</b>'

    # widget.value = 2
    discrete_slider._slider._process_events({'value': 2})
    assert discrete_slider.value == dates['2016-01-03']
    discrete_slider._slider._process_events({'value_throttled': 2})
    assert discrete_slider.value_throttled == dates['2016-01-03']

    discrete_slider.value = dates['2016-01-01']
    assert widget.value == 0

    # Testing throttled mode
    with config.set(throttled=True):
        discrete_slider._slider._process_events({'value': 2})
        assert discrete_slider.value == dates['2016-01-01']  # no change
        discrete_slider._slider._process_events({'value_throttled': 2})
        assert discrete_slider.value == dates['2016-01-03']

        discrete_slider.value = dates['2016-01-02']
        assert widget.value == 1


def test_discrete_slider_options_dict(document, comm):
    options = OrderedDict([('0.1', 0.1), ('1', 1), ('10', 10), ('100', 100)])
    discrete_slider = DiscreteSlider(name='DiscreteSlider', value=1,
                                     options=options)

    box = discrete_slider.get_root(document, comm=comm)

    label = box.children[0]
    widget = box.children[1]
    assert isinstance(label, BkDiv)
    assert isinstance(widget, BkSlider)
    assert widget.value == 1
    assert widget.start == 0
    assert widget.end == 3
    assert widget.step == 1
    assert label.text == 'DiscreteSlider: <b>1</b>'

    # widget.value = 2
    discrete_slider._slider._process_events({'value': 2})
    assert discrete_slider.value == 10
    discrete_slider._slider._process_events({'value_throttled': 2})
    assert discrete_slider.value_throttled == 10

    discrete_slider.value = 100
    assert widget.value == 3

    # Testing throttled mode
    with config.set(throttled=True):
        discrete_slider._slider._process_events({'value': 2})
        assert discrete_slider.value == options['100']  # no change
        discrete_slider._slider._process_events({'value_throttled': 2})
        assert discrete_slider.value == options['10']

        discrete_slider.value = options['1']
        assert widget.value == 1


@pytest.mark.parametrize(
    'editableslider,start,end,step,val1,val2,val3,diff1',
    [
        (EditableFloatSlider, 0.1, 0.5, 0.1, 0.4, 0.2, 0.5, 0.1),
        (EditableIntSlider, 1, 5, 1, 4, 2, 5, 1),
    ],
    ids=["EditableFloatSlider", "EditableIntSlider"]
)
def test_editable_slider(document, comm,
    editableslider, start, end, step, val1, val2, val3, diff1):

    slider = editableslider(start=start, end=end, value=val1, name='Slider')

    widget = slider.get_root(document, comm=comm)

    assert isinstance(widget, BkColumn)

    col_items = widget.children

    assert len(col_items) == 2

    row, slider_widget = col_items

    assert isinstance(slider_widget, editableslider._slider_widget._widget_type)
    assert slider_widget.title == ''
    assert slider_widget.step == step
    assert slider_widget.start == start
    assert slider_widget.end == end
    assert slider_widget.value == val1

    assert isinstance(row, BkRow)

    static_widget, input_widget = row.children

    assert isinstance(static_widget, StaticText._widget_type)
    assert static_widget.text == 'Slider:'

    assert isinstance(input_widget, editableslider._input_widget._widget_type)
    assert input_widget.title == ''
    assert input_widget.step == step
    assert input_widget.value == val1

    slider._process_events({'value': val2})
    assert slider.value == input_widget.value == slider_widget.value == val2
    slider._process_events({'value_throttled': val2})
    assert slider.value_throttled == val2

    # Testing throttled mode
    with config.set(throttled=True):
        slider._process_events({'value': val1})
        assert slider.value == val2 # no change
        slider._process_events({'value_throttled': val1})
        assert slider.value == val1

        slider.value = val3
        assert input_widget.value == slider_widget.value == val3

    slider.name = 'New Slider'

    assert static_widget.text == 'New Slider:'

    # Testing update to fixed start
    slider.fixed_start = slider.value + diff1
    assert slider._slider.start == slider.fixed_start == slider_widget.start
    slider.fixed_start = None

    # Testing update to fixed end
    slider.fixed_end = slider.value - diff1
    assert slider._slider.end == slider.fixed_end == slider_widget.end
    slider.fixed_end = None


@pytest.mark.parametrize(
    'editableslider,start,end,step,val1,val2,val3,diff1',
    [
        (EditableRangeSlider, 0.1, 0.5, 0.1, (0.2, 0.4), (0.2, 0.3), (0.1, 0.5), 0.1),
    ],
    ids=["EditableRangeSlider"]
)
def test_editable_rangeslider(document, comm,
    editableslider, start, end, step, val1, val2, val3, diff1):

    slider = editableslider(start=start, end=end, value=val1, name='Slider')

    widget = slider.get_root(document, comm=comm)

    assert isinstance(widget, BkColumn)

    col_items = widget.children

    assert len(col_items) == 2

    row, slider_widget = col_items

    assert slider_widget.title == ''
    assert slider_widget.step == step
    assert slider_widget.start == start
    assert slider_widget.end == end
    assert slider_widget.value == val1

    assert isinstance(row, BkRow)

    static_widget, input_widget_start, _, input_widget_end = row.children

    assert input_widget_start.title == ''
    assert input_widget_start.step == step
    assert input_widget_start.value == val1[0]
    assert input_widget_end.title == ''
    assert input_widget_end.step == step
    assert input_widget_end.value == val1[1]

    slider._process_events({'value': val2})
    assert slider.value == (input_widget_start.value, input_widget_end.value) == slider_widget.value == val2
    slider._process_events({'value_throttled': val2})
    assert slider.value_throttled == val2

    # Testing throttled mode
    with config.set(throttled=True):
        slider._process_events({'value': val1})
        assert slider.value == val2 # no change
        slider._process_events({'value_throttled': val1})
        assert slider.value == val1

        slider.value = val3
        assert (input_widget_start.value, input_widget_end.value) == slider_widget.value == val3

    slider.name = 'New Slider'

    assert static_widget.text == 'New Slider:'

    # Testing update to fixed start
    slider.fixed_start = slider.value[0] + diff1
    assert slider._slider.start == slider.fixed_start == slider_widget.start
    slider.fixed_start = None

    # Testing update to fixed end
    slider.fixed_end = slider.value[1] - diff1
    assert slider._slider.end == slider.fixed_end == slider_widget.end
    slider.fixed_end = None


@pytest.mark.parametrize(
    "editableslider",
    [EditableFloatSlider, EditableIntSlider],
)
@pytest.mark.parametrize(
    'start,end,fixed_start,fixed_end,val_init,val_update,fail_init,fail_update',
    [
        (1, 5, 0, None, 2, 3, False, False),
        (1, 5, 0, None, 2, -1, False, True),
        (1, 5, 0, None, -1, -1, True, True),
        (1, 5, 0, None, 0, 100, False, False),
    ],
)
def test_editable_slider_bounds(
    editableslider,start,end,fixed_start,fixed_end,val_init,val_update,fail_init,fail_update):

    try:
        slider = editableslider(
            start=start, end=end,
            fixed_start=fixed_start, fixed_end=fixed_end,
            value=val_init, name='Slider'
        )
    except Exception:
        assert fail_init

    try:
        slider.value = val_update
    except Exception:
        assert fail_update


@pytest.mark.parametrize(
    'editableslider,start,end,fixed_start,fixed_end,val_init,val_update,fail_init,fail_update',
    [
        (EditableRangeSlider, 1, 5, 0, None, (2, 5), (3, 5), False, False),
        (EditableRangeSlider, 1, 5, 0, None, (2, 5), (-1, 4), False, True),
        (EditableRangeSlider, 1, 5, 0, None, (-1, 100), (-1, 200), True, True),
        (EditableRangeSlider, 1, 5, 0, None, (1, 5), (0, 100), False, False),
    ],
)
def test_editable_rangeslider_bounds(
    editableslider,start,end,fixed_start,fixed_end,val_init,val_update,fail_init,fail_update):

    try:
        slider = editableslider(
            start=start, end=end,
            fixed_start=fixed_start, fixed_end=fixed_end,
            value=val_init, name='Slider'
        )
    except Exception:
        assert fail_init

    try:
        slider.value = val_update
    except Exception:
        assert fail_update
