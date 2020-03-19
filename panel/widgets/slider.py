"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import absolute_import, division, unicode_literals

from six import string_types

import param
import numpy as np

from bokeh.models import CustomJS
from bokeh.models.widgets import (
    DateSlider as _BkDateSlider, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, Slider as _BkSlider)

from ..config import config
from ..io import state
from ..util import unicode_repr, value_as_datetime, value_as_date
from ..viewable import Layoutable
from .base import Widget, CompositeWidget
from ..layout import Column
from .input import StaticText


class _SliderBase(Widget):

    bar_color = param.Color(default="#e6e6e6", doc="""
        Color of the slider bar as a hexidecimal RGB value.""")

    callback_policy = param.ObjectSelector(
        default='continuous', objects=['continuous', 'throttle', 'mouseup'], doc="""
        DEPRECATED: Policy to determine when slider events are triggered:

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


class ContinuousSlider(_SliderBase):

    _supports_embed = True

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super(ContinuousSlider, self).__init__(**params)

    def _get_embed_state(self, root, max_opts=3):
        ref = root.ref['id']
        w_model, parent = self._models[ref]
        _, _, doc, comm = state._views[ref]

        # Compute sampling
        start, end, step = w_model.start, w_model.end, w_model.step
        span = end-start
        dtype = int if isinstance(step, int) else float
        if (span/step) > (max_opts-1):
            step = dtype(span/(max_opts-1))
        vals = [dtype(v) for v in np.arange(start, end+step, step)]

        # Replace model
        layout_opts = {k: v for k, v in self.param.get_param_values()
                       if k in Layoutable.param and k != 'name'}
        dw = DiscreteSlider(options=vals, name=self.name, **layout_opts)
        dw.link(self, value='value')
        self._models.pop(ref)
        index = parent.children.index(w_model)
        with config.set(embed=True):
            w_model = dw._get_model(doc, root, parent, comm)
        link = CustomJS(code=dw._jslink.code['value'], args={
            'source': w_model.children[1], 'target': w_model.children[0]})
        parent.children[index] = w_model
        w_model = w_model.children[1]
        w_model.js_on_change('value', link)

        return (dw, w_model, vals, lambda x: x.value, 'value', 'cb_obj.value')


class FloatSlider(ContinuousSlider):

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    value_throttled = param.Number(default=None)

    step = param.Number(default=0.1)


class IntSlider(ContinuousSlider):

    value = param.Integer(default=0)

    value_throttled = param.Integer(default=None)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    def _process_property_change(self, msg):
        msg = super(_SliderBase, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = msg['value'] if msg['value'] is None else int(msg['value'])
        if 'value_throttled' in msg:
            throttled = msg['value_throttled']
            msg['value_throttled'] = throttled if throttled is None else int(throttled)
        return msg


class DateSlider(_SliderBase):

    value = param.Date(default=None)

    value_throttled = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _source_transforms = {'value': None, 'value_throttled': None, 'start': None, 'end': None}

    _widget_type = _BkDateSlider

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super(DateSlider, self).__init__(**params)

    def _process_property_change(self, msg):
        msg = super(_SliderBase, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = value_as_date(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = value_as_date(msg['value_throttled'])
        return msg


class DiscreteSlider(CompositeWidget, _SliderBase):

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    value_throttled = param.Parameter()

    formatter = param.String(default='%.3g')

    _source_transforms = {'value': None, 'value_throttled': None, 'options': None}

    _rename = {'formatter': None}

    _supports_embed = True

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

        self._text = StaticText(margin=(5, 0, 0, 5), style={'white-space': 'nowrap'})
        self._slider = None
        self._composite = Column(self._text, self._slider)
        self._update_options()
        self.param.watch(self._update_options, ['options', 'formatter'])
        self.param.watch(self._update_value, ['value'])
        self.param.watch(self._update_style, [p for p in Layoutable.param if p !='name'])

    def _update_options(self, *events):
        values, labels = self.values, self.labels
        if self.value not in values:
            value = 0
            self.value = values[0]
        else:
            value = values.index(self.value)

        self._slider = IntSlider(
            start=0, end=len(self.options)-1, value=value, tooltips=False,
            show_value=False, margin=(0, 5, 5, 5), _supports_embed=False
        )
        self._update_style()
        js_code = self._text_link.format(
            labels='['+', '.join([unicode_repr(l) for l in labels])+']'
        )
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

    def _update_style(self, *events):
        style = {p: getattr(self, p) for p in Layoutable.param if p != 'name'}
        margin = style.pop('margin')
        if isinstance(margin, tuple):
            if len(margin) == 2:
                t = b = margin[0]
                r = l = margin[1]
            else:
                t, r, b, l = margin
        else:
            t = r = b = l = margin
        text_margin = (t, 0, 0, l)
        slider_margin = (0, r, b, l)
        self._text.param.set_param(
            margin=text_margin, **{k: v for k, v in style.items() if k != 'style'})
        self._slider.param.set_param(margin=slider_margin, **style)
        if self.width:
            style['width'] = self.width + l + r
        self._composite.param.set_param(**style)

    def _sync_value(self, event):
        if self._syncing:
            return
        try:
            self._syncing = True
            self.value = self.values[event.new]
        finally:
            self._syncing = False

    def _get_embed_state(self, root, max_opts=3):
        model = self._composite[1]._models[root.ref['id']][0]
        return self, model, self.values, lambda x: x.value, 'value', 'cb_obj.value'

    @property
    def labels(self):
        title = (self.name + ': ' if self.name else '')
        if isinstance(self.options, dict):
            return [title + ('<b>%s</b>' % o) for o in self.options]
        else:
            return [title + ('<b>%s</b>' % (o if isinstance(o, string_types) else (self.formatter % o)))
                    for o in self.options]
    @property
    def values(self):
        return list(self.options.values()) if isinstance(self.options, dict) else self.options


class RangeSlider(_SliderBase):

    value = param.NumericTuple(default=(0, 1), length=2)

    value_throttled = param.NumericTuple(default=None, length=2)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _widget_type = _BkRangeSlider

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = (params.get('start', self.start),
                               params.get('end', self.end))
        super(RangeSlider, self).__init__(**params)
        values = [self.value[0], self.value[1], self.start, self.end]
        if (all(v is None or isinstance(v, int) for v in values) and
            'step' not in params):
            self.step = 1

    def _process_property_change(self, msg):
        msg = super(RangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple(msg['value_throttled'])
        return msg


class IntRangeSlider(RangeSlider):

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    def _process_property_change(self, msg):
        msg = super(RangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple([v if v is None else int(v)
                                  for v in msg['value']])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple([v if v is None else int(v)
                                            for v in msg['value_throttled']])
        return msg


class DateRangeSlider(_SliderBase):

    value = param.Tuple(default=(None, None), length=2)

    value_throttled = param.Tuple(default=None, length=2)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _source_transforms = {'value': None, 'value_throttled': None,
                         'start': None, 'end': None, 'step': None}

    _widget_type = _BkDateRangeSlider

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = (params.get('start', self.start),
                               params.get('end', self.end))
        super(DateRangeSlider, self).__init__(**params)

    def _process_property_change(self, msg):
        msg = super(DateRangeSlider, self)._process_property_change(msg)
        if 'value' in msg:
            v1, v2 = msg['value']
            msg['value'] = (value_as_datetime(v1), value_as_datetime(v2))
        if 'value_throttled' in msg:
            v1, v2 = msg['value_throttled']
            msg['value_throttled'] = (value_as_datetime(v1), value_as_datetime(v2))
        return msg
