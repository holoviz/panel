from datetime import datetime, date
from collections import OrderedDict

from bokeh.models import Div as BkDiv, Slider as BkSlider, Column as BkColumn

from panel import config
from panel.widgets import (DateSlider, DateRangeSlider, DiscreteSlider,
                           FloatSlider, IntSlider, RangeSlider)


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

    discrete_slider.value = 100

    box = discrete_slider.get_root(document, comm=comm)

    assert box.children[0].text == 'DiscreteSlider: <b>100</b>'


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
