"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import absolute_import, division, unicode_literals

from six import string_types

import param
import numpy as np

from bokeh.models import Column as _BkColumn, Div as _BkDiv
from bokeh.models.widgets import (
    DateSlider as _BkDateSlider, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, Slider as _BkSlider)

from ..util import push, value_as_datetime
from .base import Widget



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

    tooltips = param.Boolean(default=True, doc="""
        Whether the slider handle should display tooltips""")

    _widget_type = _BkSlider


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


class DiscreteSlider(_SliderBase):

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    formatter = param.String(default='%.3g')

    def __init__(self, **params):
        super(DiscreteSlider, self).__init__(**params)
        if 'formatter' not in params and all(isinstance(v, (int, np.int_)) for v in self.values):
            self.formatter = '%d'
        if self.value is None and None not in self.values:
            self.value = self.values[0]
        elif self.value not in self.values:
            raise ValueError('Value %s not a valid option, '
                             'ensure that the supplied value '
                             'is one of the declared options.'
                             % self.value)

    @property
    def labels(self):
        title = ('<b>%s:</b> ' % self.name if self.name else '')
        if isinstance(self.options, dict):
            return [title + o for o in self.options]
        else:
            return [title + (o if isinstance(o, string_types) else (self.formatter % o))
                    for o in self.options]
    @property
    def values(self):
        return list(self.options.values()) if isinstance(self.options, dict) else self.options

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = _BkColumn()
        if root is None:
            root = model
        msg = self._process_param_change(self._init_properties())
        div = _BkDiv(text=msg['text'])
        slider = _BkSlider(start=msg['start'], end=msg['end'], value=msg['value'],
                           title=None, step=1, show_value=False, tooltips=None)

        # Link parameters and bokeh model
        self._link_params(model, slider, div, ['value', 'options'], doc, root, comm)
        self._link_props(slider, ['value'], doc, root, comm)

        model.children = [div, slider]
        self._models[root.ref['id']] = model

        return model

    def _link_params(self, model, slider, div, params, doc, root, comm=None):
        from .. import state

        def param_change(*events):
            combined_msg = {}
            for event in events:
                msg = self._process_param_change({event.name: event.new})
                msg = {k: v for k, v in msg.items() if k not in self._active}
                if msg:
                    combined_msg.update(msg)

            if not combined_msg:
                return

            def update_model():
                slider.update(**{k: v for k, v in combined_msg.items()
                                 if k in slider.properties()})
                div.update(**{k: v for k, v in combined_msg.items()
                              if k in div.properties()})

            if comm:
                update_model()
                push(doc, comm)
            elif state.curdoc:
                update_model()
            else:
                doc.add_next_tick_callback(update_model)

        ref = root.ref['id']
        for p in params:
            self._callbacks[ref].append(self.param.watch(param_change, p))

    def _process_param_change(self, msg):
        labels, values = self.labels, self.values
        if 'name' in msg:
            msg['text'] = labels[values.index(self.value)]
        if 'options' in msg:
            msg['start'] = 0
            msg['end'] = len(msg['options']) - 1
            msg['labels'] = labels
            if self.value not in values:
                self.value = values[0]
        if 'value' in msg:
            value = msg['value']
            if value not in values:
                self.value = values[0]
                msg.pop('value')
                return msg
            label = labels[values.index(value)]
            msg['value'] = values.index(value)
            msg['text'] = label
        return msg

    def _process_property_change(self, msg):
        if 'value' in msg:
            msg['value'] = self.values[msg['value']]
        return msg


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
