"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import absolute_import, division, unicode_literals

from six import string_types

import param
import numpy as np

from bokeh.models.widgets import (
    DateSlider as _BkDateSlider, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, Slider as _BkSlider)

from ..util import value_as_datetime
from .base import Widget, CompositeWidget
from ..layout import Column
from .input import StaticText


class _SliderBase(Widget):

    bar_color = param.Color(default="#e6e6e6", doc="""
        Color of the slider bar as a hexidecimal RGB value.""")

    callback_policy = param.ObjectSelector(
        default='continuous', objects=['continuous', 'throttle', 'mouseup'], doc="""
        Policy to determine when slider events are triggered:

        * "continuous": the callback will be executed immediately for each movement of the slider
        * "throttle": the callback will be executed at most every ``callback_throttle`` milliseconds.
        * "mouseup": the callback will be executed only once when the slider is released.
        """)

    callback_throttle = param.Integer(default=200, doc="""
        Number of milliseconds to pause between callback calls as the slider is moved.""")

    direction = param.ObjectSelector(default='ltr', objects=['ltr', 'rtl'],
                                     doc="""
        Whether the slider should go from left-to-right ('ltr') or right-to-left ('rtl')""")

    orientation = param.ObjectSelector(default='horizontal',
                                       objects=['horizontal', 'vertical'], doc="""
        Whether the slider should be oriented horizontally or vertically.""")

    show_value = param.Boolean(default=True, doc="""
        Whether to show the widget value""")

    tooltips = param.Boolean(default=True, doc="""
        Whether the slider handle should display tooltips""")

    _widget_type = _BkSlider

    __abstract = True


class FloatSlider(_SliderBase):

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    step = param.Number(default=0.1)


class IntSlider(_SliderBase):

    value = param.Integer(default=0)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)


class DateSlider(_SliderBase):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = _BkDateSlider


class DiscreteSlider(CompositeWidget, _SliderBase):

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    formatter = param.String(default='%.3g')

    _rename = {'formatter': None}

    _text_link = """
    var labels = {labels}
    target.text = labels[source.value]
    """

    def __init__(self, **params):
        self._syncing = False
        super(DiscreteSlider, self).__init__(**params)
        if 'formatter' not in params and all(isinstance(v, (int, np.int_)) for v in self.values):
            self.formatter = '%d'
        if self.value is None and None not in self.values and self.options:
            self.value = self.values[0]
        elif self.value not in self.values:
            raise ValueError('Value %s not a valid option, '
                             'ensure that the supplied value '
                             'is one of the declared options.'
                             % self.value)

        self._text = StaticText(margin=(5, 0, 0, 5))
        self._slider = IntSlider()
        self._composite = Column(self._text, self._slider)
        self._update_options()
        self.param.watch(self._update_options, ['options', 'formatter'])
        self.param.watch(self._update_value, ['value'])

    def _update_options(self, *events):
        values, labels = self.values, self.labels
        if self.value not in values:
            value = 0
            self.value = values[0]
        else:
            value = values.index(self.value)
        self._slider = IntSlider(start=0, end=len(self.options)-1, value=value,
                                 show_value=False, margin=(0, 5, 5, 5))
        js_code = self._text_link.format(labels=repr(self.labels))
        self._jslink = self._slider.jslink(self._text, code={'value': js_code})
        self._slider.param.watch(self._sync_value, 'value')
        self._text.value = labels[value]
        self._composite[1] = self._slider

    def _update_value(self, event):
        values = self.values
        if self.value not in values:
            self.value = values[0]
            return
        index = self.values.index(self.value)
        if self._syncing:
            return
        try:
            self._syncing = True
            self._slider.value = index
        finally:
            self._syncing = False

    def _sync_value(self, event):
        if self._syncing:
            return
        try:
            self._syncing = True
            self.value = self.values[event.new]
        finally:
            self._syncing = False

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._composite._get_model(doc, root, parent, comm)

    @property
    def labels(self):
        title = (self.name + ': ' if self.name else '')
        if isinstance(self.options, dict):
            return [title + ('<b>%s</b> ' % o) for o in self.options]
        else:
            return [title + ('<b>%s</b> ' % (o if isinstance(o, string_types) else (self.formatter % o)))
                    for o in self.options]
    @property
    def values(self):
        return list(self.options.values()) if isinstance(self.options, dict) else self.options



class RangeSlider(_SliderBase):

    value = param.NumericTuple(default=(0, 1), length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = _BkRangeSlider

    def __init__(self, **params):
        super(RangeSlider, self).__init__(**params)
        values = [self.value[0], self.value[1], self.start, self.end]
        if (all(v is None or isinstance(v, int) for v in values) and
            'step' not in params):
            self.step = 1

    def _process_property_change(self, msg):
        msg = super(RangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        return msg


class IntRangeSlider(RangeSlider):

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)


class DateRangeSlider(_SliderBase):

    value = param.Tuple(default=None, length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _widget_type = _BkDateRangeSlider

    def _process_property_change(self, msg):
        msg = super(DateRangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            v1, v2 = msg['value']
            msg['value'] = (value_as_datetime(v1), value_as_datetime(v2))
        return msg
