"""
Sliders allow you to select a value from a defined range of values by
moving one or more handle(s).

- The `value` will update when a handle is dragged.
- The `value_throttled`will update when a handle is released.
"""
from __future__ import annotations

import datetime as dt

from typing import (
    TYPE_CHECKING, Any, ClassVar, Mapping, Optional,
)

import numpy as np
import param

from bokeh.models import CustomJS
from bokeh.models.formatters import TickFormatter
from bokeh.models.widgets import (
    DateRangeSlider as _BkDateRangeSlider, DateSlider as _BkDateSlider,
    RangeSlider as _BkRangeSlider, Slider as _BkSlider,
)
from bokeh.models.widgets.sliders import NumericalSlider as _BkNumericalSlider
from param.parameterized import resolve_value

from ..config import config
from ..io import state
from ..io.resources import CDN_DIST
from ..layout import Column, Panel, Row
from ..util import (
    datetime_as_utctimestamp, edit_readonly, param_reprs, value_as_date,
    value_as_datetime,
)
from ..viewable import Layoutable
from ..widgets import FloatInput, IntInput
from .base import CompositeWidget, Widget
from .input import StaticText

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class _SliderBase(Widget):

    bar_color = param.Color(default="#e6e6e6", doc="""""")

    direction = param.ObjectSelector(default='ltr', objects=['ltr', 'rtl'], doc="""
        Whether the slider should go from left-to-right ('ltr') or
        right-to-left ('rtl').""")

    name = param.String(default=None, doc="""
        The name of the widget. Also used as the label of the widget. If not set,
        the widget has no label.""")

    orientation = param.ObjectSelector(default='horizontal', objects=['horizontal', 'vertical'],
        doc="""
        Whether the slider should be oriented horizontally or
        vertically.""")

    show_value = param.Boolean(default=True, doc="""
        Whether to show the widget value as a label or not.""")

    tooltips = param.Boolean(default=True, doc="""
        Whether the slider handle should display tooltips.""")

    _widget_type: ClassVar[type[Model]] = _BkSlider

    __abstract = True

    def __init__(self, **params):
        if 'value' in params and 'value_throttled' in self.param:
            params['value_throttled'] = params['value']
        if 'orientation' == 'vertical':
            params['height'] = self.param.width.default
        super().__init__(**params)

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self, ['value_throttled'])))

    @property
    def _linked_properties(self) -> tuple[str]:
        return super()._linked_properties + ('value_throttled',)

    def _process_property_change(self, msg):
        if config.throttled:
            if "value" in msg:
                del msg["value"]
            if "value_throttled" in msg:
                msg["value"] = msg["value_throttled"]
        return super()._process_property_change(msg)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        if 'value_throttled' in msg:
            del msg['value_throttled']

        return super()._update_model(events, msg, root, model, doc, comm)


class ContinuousSlider(_SliderBase):

    format = param.ClassSelector(class_=(str, TickFormatter,), doc="""
        A custom format string or Bokeh TickFormatter.""")

    _supports_embed: ClassVar[bool] = True

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super().__init__(**params)

    def _get_embed_state(self, root, values=None, max_opts=3):
        ref = root.ref['id']
        w_model, parent = self._models[ref]
        if not isinstance(w_model, _BkNumericalSlider):
            is_composite = True
            parent = w_model
            w_model = w_model.select_one({'type': _BkNumericalSlider})
        else:
            is_composite = False
        _, _, doc, comm = state._views[ref]

        # Compute sampling
        start, end, step = w_model.start, w_model.end, w_model.step
        if values is None:
            span = end-start
            dtype = int if isinstance(step, int) else float
            if (span/step) > (max_opts-1):
                step = dtype(span/(max_opts-1))
            values = [dtype(v) for v in np.arange(start, end+step, step)]
        elif any(v < start or v > end for v in values):
            raise ValueError(f'Supplied embed states for {type(self).__name__} widget outside '
                             'of valid range.')

        # Replace model
        layout_opts = {k: v for k, v in self.param.values().items()
                       if k in Layoutable.param and k != 'name'}

        if is_composite:
            layout_opts['show_value'] = False
        else:
            layout_opts['name'] = self.name

        value = values[np.argmin(np.abs(np.array(values)-self.value))]
        dw = DiscreteSlider(options=values, value=value,  **layout_opts)
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

        return (dw, w_model, values, lambda x: x.value, 'value', 'cb_obj.value')


class FloatSlider(ContinuousSlider):
    """
    The FloatSlider widget allows selecting a floating-point value
    within a set of bounds using a slider.

    Reference: https://panel.holoviz.org/reference/widgets/FloatSlider.html

    :Example:

    >>> FloatSlider(value=0.5, start=0.0, end=1.0, step=0.1, name="Float value")
    """

    start = param.Number(default=0.0, doc="The lower bound.")

    end = param.Number(default=1.0, doc="The upper bound.")

    step = param.Number(default=0.1, doc="The step size.")

    value = param.Number(default=0.0, allow_None=True, doc="""
        The selected floating-point value of the slider. Updated when
        the handle is dragged."""
    )

    value_throttled = param.Number(default=None, constant=True, doc="""
         The value of the slider. Updated when the handle is released.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': 'title', 'value_throttled': None
    }


class IntSlider(ContinuousSlider):
    """
    The IntSlider widget allows selecting an integer value within a
    set of bounds using a slider.

    Reference: https://panel.holoviz.org/reference/widgets/IntSlider.html

    :Example:

    >>> IntSlider(value=5, start=0, end=10, step=1, name="Integer Value")
    """

    start = param.Integer(default=0, doc="""
        The lower bound.""")

    end = param.Integer(default=1, doc="""
        The upper bound.""")

    step = param.Integer(default=1, doc="""
        The step size.""")

    value = param.Integer(default=0, allow_None=True, doc="""
        The selected integer value of the slider. Updated when the handle is dragged.""")

    value_throttled = param.Integer(default=None, constant=True, doc="""
        The value of the slider. Updated when the handle is released""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': 'title', 'value_throttled': None
    }

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = msg['value'] if msg['value'] is None else int(msg['value'])
        if 'value_throttled' in msg:
            throttled = msg['value_throttled']
            msg['value_throttled'] = throttled if throttled is None else int(throttled)
        return msg


class DateSlider(_SliderBase):
    """
    The DateSlider widget allows selecting a value within a set of
    bounds using a slider.  Supports datetime.datetime, datetime.date
    and np.datetime64 values. The step size is fixed at 1 day.

    Reference: https://panel.holoviz.org/reference/widgets/DateSlider.html

    :Example:

    >>> import datetime as dt
    >>> DateSlider(
    ...     value=dt.datetime(2025, 1, 1),
    ...     start=dt.datetime(2025, 1, 1),
    ...     end=dt.datetime(2025, 1, 7),
    ...     name="A datetime value"
    ... )
    """

    value = param.Date(default=None, doc="""
        The selected date value of the slider. Updated when the slider
        handle is dragged. Supports datetime.datetime, datetime.date
        or np.datetime64 types.""")

    value_throttled = param.Date(default=None, constant=True, doc="""
        The value of the slider. Updated when the slider handle is released.""")

    start = param.Date(default=None, doc="""
        The lower bound.""")

    end = param.Date(default=None, doc="""
        The upper bound.""")

    as_datetime = param.Boolean(default=False, doc="""
        Whether to store the date as a datetime.""")

    step = param.Number(default=None, doc="""
        The step parameter in milliseconds.""")

    format = param.String(default=None, doc="""
        Datetime format used for parsing and formatting the date.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': 'title', 'as_datetime': None, 'value_throttled': None
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'value_throttled': None, 'start': None, 'end': None
    }

    _widget_type: ClassVar[type[Model]] = _BkDateSlider

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super().__init__(**params)

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'value' in msg:
            value = msg['value']
            if isinstance(value, dt.datetime):
                value = datetime_as_utctimestamp(value)
            msg['value'] = value
        return msg

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        transform = value_as_datetime if self.as_datetime else value_as_date
        if 'value' in msg:
            msg['value'] = transform(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = transform(msg['value_throttled'])
        return msg


class DiscreteSlider(CompositeWidget, _SliderBase):
    """
    The DiscreteSlider widget allows selecting a value from a discrete
    list or dictionary of values using a slider.

    Reference: https://panel.holoviz.org/reference/widgets/DiscreteSlider.html

    :Example:

    >>> DiscreteSlider(
    ...     value=0,
    ...     options=list([0, 1, 2, 4, 8, 16, 32, 64]),
    ...     name="A discrete value",
    ... )
    """

    value = param.Parameter(doc="""
        The selected value of the slider. Updated when the handle is
        dragged. Must be one of the options.""")

    value_throttled = param.Parameter(constant=True, doc="""
        The value of the slider. Updated when the handle is released.""")

    options = param.ClassSelector(default=[], class_=(dict, list), doc="""
        A list or dictionary of valid options.""")

    formatter = param.String(default='%.3g', doc="""
        A custom format string. Separate from format parameter since
        formatting is applied in Python, not via the bokeh TickFormatter.""")


    _rename: ClassVar[Mapping[str, str | None]] = {'formatter': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'value_throttled': None, 'options': None
    }

    _supports_embed: ClassVar[bool] = True

    _style_params: ClassVar[list[str]] = [
        p for p in list(Layoutable.param) if p != 'name'
    ] + ['orientation']

    _slider_style_params: ClassVar[list[str]] = [
        'bar_color', 'direction', 'disabled', 'orientation'
    ]

    _text_link = """
    var labels = {labels}
    target.text = labels[source.value]
    """

    def __init__(self, **params):
        self._syncing = False
        super().__init__(**params)
        if 'formatter' not in params and all(isinstance(v, (int, np.int_)) for v in self.values):
            self.formatter = '%d'
        if self.value is None and None not in self.values and self.options:
            self.value = self.values[0]
        elif self.value not in self.values and not (self.value is None or self.options):
            raise ValueError(f'Value {self.value} not a valid option, '
                             'ensure that the supplied value '
                             'is one of the declared options.')

        self._text = StaticText(
            margin=(5, 0, 0, 5), styles={'white-space': 'nowrap'}
        )
        self._slider = None
        self._composite = Column(self._text, self._slider)
        self._update_options()
        self.param.watch(self._update_options, ['options', 'formatter', 'name'])
        self.param.watch(self._update_value, 'value')
        self.param.watch(self._update_value, 'value_throttled')
        self.param.watch(self._update_style, self._style_params)

    def _update_options(self, *events):
        values, labels = self.values, self.labels
        if not self.options and self.value is None:
            value = 0
            label = (f'{self.name}: ' if self.name else '') + '<b>-</b>'
        elif self.value not in values:
            value = 0
            self.value = values[0]
            label = labels[value]
        else:
            value = values.index(self.value)
            label = labels[value]
        disabled = True if len(values) in (0, 1) else self.disabled
        end = 1 if disabled else len(self.options)-1

        self._slider = IntSlider(
            start=0, end=end, value=value, tooltips=False,
            show_value=False, margin=(0, 5, 5, 5),
            _supports_embed=False, disabled=disabled,
            **{p: getattr(self, p) for p in self._slider_style_params if p != 'disabled'}
        )
        self._update_style()
        js_code = self._text_link.format(
            labels='['+', '.join([repr(l) for l in labels])+']'
        )
        self._jslink = self._slider.jslink(self._text, code={'value': js_code})
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')
        self.param.watch(self._update_slider_params, self._slider_style_params)
        self._text.value = label
        self._composite[1] = self._slider

    def _update_value(self, event):
        """
        This will update the IntSlider (behind the scene)
        based on changes to the DiscreteSlider (front).

        _syncing options is to avoid infinite loop.

        event.name is either value or value_throttled.
        """

        values = self.values
        if getattr(self, event.name) not in values:
            with param.edit_constant(self):
                setattr(self, event.name, values[0])
            return
        index = self.values.index(getattr(self, event.name))
        if event.name == 'value':
            self._text.value = self.labels[index]
        if self._syncing:
            return
        try:
            self._syncing = True
            with param.edit_constant(self._slider):
                setattr(self._slider, event.name, index)
        finally:
            self._syncing = False

    def _update_style(self, *events):
        style = {p: getattr(self, p) for p in self._style_params}
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
        text_style = {k: v for k, v in style.items()
                      if k not in ('style', 'orientation')}
        text_style['visible'] = self.show_value and text_style['visible']
        self._text.param.update(margin=text_margin, **text_style)
        self._slider.param.update(margin=slider_margin, **style)
        if self.width:
            style['width'] = self.width + l + r
        col_style = {k: v for k, v in style.items()
                     if k != 'orientation'}
        self._composite.param.update(**col_style)

    def _update_slider_params(self, *events):
        style = {e.name: e.new for e in events}
        disabled = style.get('disabled', None)
        if disabled is False:
            if len(self.values) in (0, 1):
                self.param.warning(
                    'A DiscreteSlider can only be disabled if it has more than 1 option.'
                )
                end = 1
                del style['disabled']
            else:
                end = len(self.options) - 1
            style['end'] = end
        self._slider.param.update(**style)

    def _sync_value(self, event):
        """
        This will update the DiscreteSlider (front)
        based on changes to the IntSlider (behind the scene).

        _syncing options is to avoid infinite loop.

        event.name is either value or value_throttled.
        """
        if self._syncing:
            return
        try:
            self._syncing = True
            with param.edit_constant(self):
                setattr(self, event.name, self.values[event.new])
        finally:
            self._syncing = False

    def _get_embed_state(self, root, values=None, max_opts=3):
        model = self._composite[1]._models[root.ref['id']][0]
        if values is None:
            values = self.values
        elif any(v not in self.values for v in values):
            raise ValueError("Supplieed embed states were not found "
                             f"in the {type(self).__name__} widgets' values list.")
        return self, model, values, lambda x: x.value, 'value', 'cb_obj.value'

    @property
    def labels(self):
        """The list of labels to display"""
        title = (self.name + ': ' if self.name else '')
        if isinstance(self.options, dict):
            return [title + (f'<b>{o}</b>') for o in self.options]
        else:
            return [title + ('<b>%s</b>' % (o if isinstance(o, str) else (self.formatter % o)))
                    for o in self.options]
    @property
    def values(self):
        """The list of option values"""
        return list(self.options.values()) if isinstance(self.options, dict) else self.options



class _RangeSliderBase(_SliderBase):

    value = param.Tuple(default=(None, None), length=2, allow_None=False, nested_refs=True, doc="""
        The selected range of the slider. Updated when a handle is dragged.""")

    value_start = param.Parameter(readonly=True, doc="""The lower value of the selected range.""")

    value_end = param.Parameter(readonly=True, doc="""The upper value of the selected range.""")

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = (
                params.get('start', self.start), params.get('end', self.end)
            )
        if params['value'] is not None:
            v1, v2 = params['value']
            params['value_start'], params['value_end'] = resolve_value(v1), resolve_value(v2)
        with edit_readonly(self):
            super().__init__(**params)

    @param.depends('value', watch=True)
    def _sync_values(self):
        vs, ve = self.value
        with edit_readonly(self):
            self.param.update(value_start=vs, value_end=ve)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple(msg['value_throttled'])
        return msg


class RangeSlider(_RangeSliderBase):
    """
    The RangeSlider widget allows selecting a floating-point range
    using a slider with two handles.

    Reference: https://panel.holoviz.org/reference/widgets/RangeSlider.html

    :Example:

    >>> RangeSlider(
    ...     value=(1.0, 1.5), start=0.0, end=2.0, step=0.25, name="A tuple of floats"
    ... )
    """

    value = param.Range(default=(0, 1), allow_None=False, nested_refs=True, doc=
        """The selected range as a tuple of values. Updated when a handle is
        dragged.""")

    value_throttled = param.Range(default=None, constant=True, nested_refs=True, doc="""
        The selected range as a tuple of floating point values. Updated when a handle is
        released""")

    value_start = param.Number(default=0, readonly=True, doc="""
        The lower value of the selected range.""")

    value_end = param.Number(default=1, readonly=True, doc="""
        The upper value of the selected range.""")

    start = param.Number(default=0, doc="""
        The lower bound.""")

    end = param.Number(default=1, doc="""
        The upper bound.""")

    step = param.Number(default=0.1, doc="""
        The step size.""")

    format = param.ClassSelector(class_=(str, TickFormatter,), doc="""
        A format string or bokeh TickFormatter.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'title', 'value_start': None, 'value_end': None, 'value_throttled': None}

    _widget_type: ClassVar[type[Model]] = _BkRangeSlider

    def __init__(self, **params):
        super().__init__(**params)
        values = [self.value[0], self.value[1], self.start, self.end]
        if (all(v is None or isinstance(v, int) for v in values) and
            'step' not in params):
            self.step = 1


class IntRangeSlider(RangeSlider):
    """
    The IntRangeSlider widget allows selecting an integer range using
    a slider with two handles.

    Reference: https://panel.holoviz.org/reference/widgets/IntRangeSlider.html

    :Example:

    >>> IntRangeSlider(
    ...     value=(2, 4), start=0, end=10, step=2, name="A tuple of integers"
    ... )
    """

    start = param.Integer(default=0, doc="""
        The lower bound.""")

    end = param.Integer(default=1, doc="""
        The upper bound.""")

    step = param.Integer(default=1, doc="""
        The step size""")

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple([v if v is None else round(v)
                                  for v in msg['value']])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple([v if v is None else round(v)
                                            for v in msg['value_throttled']])
        return msg


class DateRangeSlider(_SliderBase):
    """
    The DateRangeSlider widget allows selecting a date range using a
    slider with two handles. Supports datetime.datetime, datetime.date
    and np.datetime64 ranges.

    Reference: https://panel.holoviz.org/reference/widgets/DateRangeSlider.html

    :Example:

    >>> import datetime as dt
    >>> DateRangeSlider(
    ...     value=(dt.datetime(2025, 1, 9), dt.datetime(2025, 1, 16)),
    ...     start=dt.datetime(2025, 1, 1),
    ...     end=dt.datetime(2025, 1, 31),
    ...     step=2,
    ...     name="A tuple of datetimes"
    ... )
    """

    value = param.DateRange(default=None, allow_None=False, doc="""
        The selected range as a tuple of values. Updated when one of the handles is
        dragged. Supports datetime.datetime, datetime.date, and np.datetime64 ranges.""")

    value_start = param.Date(default=None, readonly=True, doc="""
        The lower value of the selected range.""")

    value_end = param.Date(default=None, readonly=True, doc="""
        The upper value of the selected range.""")

    value_throttled = param.DateRange(default=None, constant=True, nested_refs=True, doc="""
        The selected range as a tuple of values. Updated one of the handles is released. Supports
        datetime.datetime, datetime.date and np.datetime64 ranges""")

    start = param.Date(default=None, doc="""
        The lower bound.""")

    end = param.Date(default=None, doc="""
        The upper bound.""")

    step = param.Number(default=1, doc="""
        The step size in days. Default is 1 day.""")

    format = param.String(default=None, doc="""
        Datetime format used for parsing and formatting the date.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'value': None, 'value_throttled': None, 'start': None, 'end': None,
        'step': None
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': 'title', 'value_start': None, 'value_end': None,
        'value_throttled': None
    }

    _widget_type: ClassVar[type[Model]] = _BkDateRangeSlider

    _property_conversion = staticmethod(value_as_date)

    def __init__(self, **params):
        if 'value' not in params:
            value_to_None = False
            for attr in ['start', 'end']:
                if params.get(attr, getattr(self, attr)):
                    continue
                self.param.warning(
                    f'Parameter {attr!r} must be set for the widget to be rendered.'
                )
                value_to_None = True
            if value_to_None:
                params['value'] = None
            else:
                params['value'] = (params.get('start', self.start),
                                params.get('end', self.end))
        if params['value'] is not None:
            v1, v2 = params['value']
            params['value_start'], params['value_end'] = resolve_value(v1), resolve_value(v2)
        with edit_readonly(self):
            super().__init__(**params)

    @param.depends('value', watch=True)
    def _sync_values(self):
        vs, ve = self.value
        with edit_readonly(self):
            self.param.update(value_start=vs, value_end=ve)

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if msg.get('value', 'unchanged') is None:
            del msg['value']
        elif 'value' in msg:
            v1, v2 = msg['value']
            if isinstance(v1, dt.datetime):
                v1 = datetime_as_utctimestamp(v1)
            if isinstance(v2, dt.datetime):
                v2 = datetime_as_utctimestamp(v2)
            msg['value'] = (v1, v2)
        if msg.get('value_throttled', 'unchanged') is None:
            del msg['value_throttled']
        return msg

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            v1, v2 = msg['value']
            msg['value'] = (self._property_conversion(v1), self._property_conversion(v2))
        if 'value_throttled' in msg:
            v1, v2 = msg['value_throttled']
            msg['value_throttled'] = (self._property_conversion(v1), self._property_conversion(v2))
        return msg



class DatetimeRangeSlider(DateRangeSlider):

    """
    The DatetimeRangeSlider widget allows selecting a datetime range
    using a slider with two handles. Supports datetime.datetime and
    np.datetime64 ranges.

    Reference: https://panel.holoviz.org/reference/widgets/DatetimeRangeSlider.html

    :Example:

    >>> import datetime as dt
    >>> DatetimeRangeSlider(
    ...     value=(dt.datetime(2025, 1, 9), dt.datetime(2025, 1, 16)),
    ...     start=dt.datetime(2025, 1, 1),
    ...     end=dt.datetime(2025, 1, 31),
    ...     step=10000,
    ...     name="A tuple of datetimes"
    ... )
    """

    step = param.Number(default=60_000, doc="""
        The step size in ms. Default is 1 min.""")

    _property_conversion = staticmethod(value_as_datetime)

    @property
    def _widget_type(self):
        try:
            from bokeh.models import DatetimeRangeSlider
        except ImportError:
            raise ValueError("DatetimeRangeSlider requires bokeh >= 2.4.3") from None
        return DatetimeRangeSlider


class _EditableContinuousSlider(CompositeWidget):
    """
    The EditableFloatSlider extends the FloatSlider by adding a text
    input field to manually edit the value and potentially override
    the bounds.
    """

    editable = param.Boolean(default=True, doc="""
        Whether the value is editable via the text input.""")

    show_value = param.Boolean(default=False, readonly=True, precedence=-1, doc="""
        Whether to show the widget value.""")

    _composite_type: ClassVar[type[Panel]] = Column
    _slider_widget: ClassVar[type[Widget]]
    _input_widget: ClassVar[type[Widget]]
    __abstract = True

    def __init__(self, **params):
        if 'width' not in params and 'sizing_mode' not in params:
            params['width'] = 300
        self._validate_init_bounds(params)
        super().__init__(**params)
        self._label = StaticText(margin=0, align='end')
        self._slider = self._slider_widget(
            value=self.value, margin=(0, 0, 5, 0), sizing_mode='stretch_width',
            tags=['composite']
        )
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')

        self._value_edit = self._input_widget(
            margin=0, align='end', css_classes=['slider-edit'],
            stylesheets=[f'{CDN_DIST}css/editable_slider.css'],
            format=self.format,
        )
        self._value_edit.param.watch(self._sync_value, 'value')
        self._value_edit.param.watch(self._sync_value, 'value_throttled')
        self._value_edit.jscallback(args={'slider': self._slider}, value="""
        if (cb_obj.value < slider.start)
          slider.start = cb_obj.value
        else if (cb_obj.value > slider.end)
          slider.end = cb_obj.value
        """)

        label = Row(self._label, self._value_edit)
        self._composite.extend([label, self._slider])
        self._update_disabled()
        self._update_editable()
        self._update_layout()
        self._update_name()
        self._update_slider()
        self._update_value()
        self._update_bounds()

    def _validate_init_bounds(self, params):
        """
        This updates the default value, start and end
        if outside the fixed_start and fixed_end
        """
        start, end = None, None
        if "start" not in params:
            if "fixed_start" in params:
                start = params["fixed_start"]
            elif "end" in params:
                start = params.get("end") - params.get("step", 1)
            elif "fixed_end" in params:
                start = params.get("fixed_end") - params.get("step", 1)

        if "end" not in params:
            if "fixed_end" in params:
                end = params["fixed_end"]
            elif "start" in params:
                end = params["start"] + params.get("step", 1)
            elif "fixed_start" in params:
                end = params["fixed_start"] + params.get("step", 1)

        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end

        if "value" not in params and "start" in params:
            params["value"] = params["start"]
        if "value" not in params and "end" in params:
            params["value"] = params["end"]

    @param.depends('width', 'height', 'sizing_mode', watch=True)
    def _update_layout(self):
        self._value_edit.sizing_mode = self.sizing_mode
        if self.sizing_mode not in ('stretch_width', 'stretch_both'):
            w = (self.width or 300)//4
            self._value_edit.width = w

    @param.depends('disabled', 'editable', watch=True)
    def _update_editable(self):
        self._value_edit.disabled = (not self.editable) or self.disabled

    @param.depends('disabled', watch=True)
    def _update_disabled(self):
        self._slider.disabled = self.disabled

    @param.depends('name', watch=True)
    def _update_name(self):
        if self.name:
            label = f'{self.name}:'
            margin = (0, 10, 0, 0)
        else:
            label = ''
            margin = (0, 0, 0, 0)
        self._label.param.update(margin=margin, value=label)

    @param.depends('start', 'end', 'step', 'bar_color', 'direction',
                   'show_value', 'tooltips', 'format', watch=True)
    def _update_slider(self):
        self._slider.param.update(
            format=self.format,
            start=self.start,
            end=self.end,
            step=self.step,
            bar_color=self.bar_color,
            direction=self.direction,
            show_value=self.show_value,
            tooltips=self.tooltips
        )
        self._value_edit.step = self.step

    @param.depends('value', watch=True)
    def _update_value(self):
        self._slider.value = self.value
        self._value_edit.value = self.value

    def _sync_value(self, event):
        with param.edit_constant(self):
            self.param.update(**{event.name: event.new})

    @param.depends("start", "end", "fixed_start", "fixed_end", watch=True)
    def _update_bounds(self):
        self.param.value.softbounds = (self.start, self.end)
        self.param.value_throttled.softbounds = (self.start, self.end)
        self.param.value.bounds = (self.fixed_start, self.fixed_end)
        self.param.value_throttled.bounds = (self.fixed_start, self.fixed_end)

        # First changing _slider and then _value_edit,
        # because else _value_edit will change the _slider
        # with the jscallback.
        if self.fixed_start is not None:
            self._slider.start = max(self.fixed_start, self.start)
        if self.fixed_end is not None:
            self._slider.end = min(self.fixed_end, self.end)

        self._value_edit.start = self.fixed_start
        self._value_edit.end = self.fixed_end


class EditableFloatSlider(_EditableContinuousSlider, FloatSlider):
    """
    The EditableFloatSlider widget allows selecting selecting a
    numeric floating-point value within a set of bounds using a slider
    and for more precise control offers an editable number input box.

    Reference: https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html

    :Example:

    >>> EditableFloatSlider(
    ...     value=1.0, start=0.0, end=2.0, step=0.25, name="A float value"
    ... )
    """

    fixed_start = param.Number(default=None, doc="""
        A fixed lower bound for the slider and input.""")

    fixed_end = param.Number(default=None, doc="""
        A fixed upper bound for the slider and input.""")

    _slider_widget: ClassVar[type[Widget]] = FloatSlider
    _input_widget: ClassVar[type[Widget]] = FloatInput


class EditableIntSlider(_EditableContinuousSlider, IntSlider):
    """
    The EditableIntSlider widget allows selecting selecting an integer
    value within a set of bounds using a slider and for more precise
    control offers an editable integer input box.

    Reference: https://panel.holoviz.org/reference/widgets/EditableIntSlider.html

    :Example:

    >>> EditableIntSlider(
    ...     value=2, start=0, end=5, step=1, name="An integer value"
    ... )
    """

    fixed_start = param.Integer(default=None, doc="""
        A fixed lower bound for the slider and input.""")

    fixed_end = param.Integer(default=None, doc="""
       A fixed upper bound for the slider and input.""")

    _slider_widget: ClassVar[type[Widget]] = IntSlider
    _input_widget: ClassVar[type[Widget]] = IntInput


class EditableRangeSlider(CompositeWidget, _SliderBase):
    """
    The EditableRangeSlider widget allows selecting a floating-point
    range using a slider with two handles and for more precise control
    also offers a set of number input boxes.

    Reference: https://panel.holoviz.org/reference/widgets/EditableRangeSlider.html

    :Example:

    >>> EditableRangeSlider(
    ...      value=(1.0, 1.5), start=0.0, end=2.0, step=0.25, name="A tuple of floats"
    ... )
    """

    value = param.Range(default=(0, 1), allow_None=False, doc="""
        Current range value. Updated when a handle is dragged.""")

    value_throttled = param.Range(default=None, constant=True, doc="""
        The value of the slider. Updated when the handle is released.""")

    start = param.Number(default=0., doc="Lower bound of the range.")

    end = param.Number(default=1., doc="Upper bound of the range.")

    fixed_start = param.Number(default=None, doc="""
        A fixed lower bound for the slider and input.""")

    fixed_end = param.Number(default=None, doc="""
        A fixed upper bound for the slider and input.""")

    step = param.Number(default=0.1, doc="Slider and number input step.")

    editable = param.Tuple(default=(True, True), doc="""
        Whether the lower and upper values are editable.""")

    format = param.ClassSelector(default='0.0[0000]', class_=(str, TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    show_value = param.Boolean(default=False, readonly=True, precedence=-1, doc="""
        Whether to show the widget value.""")

    _composite_type: ClassVar[type[Panel]] = Column

    def __init__(self, **params):
        if 'width' not in params and 'sizing_mode' not in params:
            params['width'] = 300
        self._validate_init_bounds(params)
        super().__init__(**params)
        self._label = StaticText(margin=0, align='end')
        self._slider = RangeSlider(margin=(0, 0, 5, 0), show_value=False)
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')
        self._start_edit = FloatInput(
            css_classes=['slider-edit'], stylesheets=[f'{CDN_DIST}css/editable_slider.css'],
            min_width=50, margin=0, format=self.format
        )
        self._end_edit = FloatInput(
            css_classes=['slider-edit'], stylesheets=[f'{CDN_DIST}css/editable_slider.css'],
            min_width=50, margin=(0, 0, 0, 10), format=self.format
        )
        self._start_edit.param.watch(self._sync_start_value, 'value')
        self._start_edit.param.watch(self._sync_start_value, 'value_throttled')
        self._end_edit.param.watch(self._sync_end_value, 'value')
        self._end_edit.param.watch(self._sync_end_value, 'value_throttled')

        sep = StaticText(value='...', margin=(0, 5, 0, 5), align='end')
        edit = Row(self._label, self._start_edit, sep, self._end_edit,
                   sizing_mode='stretch_width', margin=0)
        self._composite.extend([edit, self._slider])
        self._start_edit.jscallback(args={'slider': self._slider, 'end': self._end_edit}, value="""
        // start value always smaller than the end value
        if (cb_obj.value >= end.value) {
          cb_obj.value = end.value
          return
        }
        if (cb_obj.value < slider.start) {
          slider.start = cb_obj.value
        } else if (cb_obj.value > slider.end) {
          slider.end = cb_obj.value
        }
        """)
        self._end_edit.jscallback(args={'slider': self._slider ,'start': self._start_edit}, value="""
        // end value always larger than the start value
        if (cb_obj.value <= start.value) {
          cb_obj.value = start.value
          return
        }
        if (cb_obj.value < slider.start) {
          slider.start = cb_obj.value
        } else if (cb_obj.value > slider.end) {
          slider.end = cb_obj.value
        }
        """)
        self._update_editable()
        self._update_disabled()
        self._update_layout()
        self._update_name()
        self._update_slider()
        self._update_value()
        self._update_bounds()

    def _validate_init_bounds(self, params):
        """
        This updates the default value, start and end
        if outside the fixed_start and fixed_end
        """
        start, end = None, None
        if "start" not in params:
            if "fixed_start" in params:
                start = params["fixed_start"]
            elif "end" in params:
                start = params.get("end") - params.get("step", 1)
            elif "fixed_end" in params:
                start = params.get("fixed_end") - params.get("step", 1)

        if "end" not in params:
            if "fixed_end" in params:
                end = params["fixed_end"]
            elif "start" in params:
                end = params["start"] + params.get("step", 1)
            elif "fixed_start" in params:
                end = params["fixed_start"] + params.get("step", 1)

        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end

        if "value" not in params and "start" in params:
            start = params["start"]
            end = params.get("end", start + params.get("step", 1))
            params["value"] = (start, end)
        if "value" not in params and "end" in params:
            end = params["end"]
            start = params.get("start", end - params.get("step", 1))
            params["value"] = (start, end)

    @param.depends('disabled', watch=True)
    def _update_disabled(self):
        self._slider.disabled = self.disabled

    @param.depends('disabled', 'editable', watch=True)
    def _update_editable(self):
        self._start_edit.disabled = (not self.editable[0]) or self.disabled
        self._end_edit.disabled = (not self.editable[1]) or self.disabled

    @param.depends('name', watch=True)
    def _update_name(self):
        if self.name:
            label = f'{self.name}:'
            margin = (0, 10, 0, 0)
        else:
            label = ''
            margin = (0, 0, 0, 0)
        self._label.param.update(margin=margin, value=label)

    @param.depends('width', 'height', 'sizing_mode', watch=True)
    def _update_layout(self):
        self._start_edit.sizing_mode = self.sizing_mode
        self._end_edit.sizing_mode = self.sizing_mode
        if self.sizing_mode not in ('stretch_width', 'stretch_both'):
            w = (self.width or 300)//4
            self._start_edit.width = w
            self._end_edit.width = w

    @param.depends('start', 'end', 'step', 'bar_color', 'direction',
                   'show_value', 'tooltips', 'name', 'format', watch=True)
    def _update_slider(self):
        self._slider.param.update(
            format=self.format,
            start=self.start,
            end=self.end,
            step=self.step,
            bar_color=self.bar_color,
            direction=self.direction,
            show_value=self.show_value,
            tooltips=self.tooltips
        )
        self._start_edit.step = self.step
        self._end_edit.step = self.step

    @param.depends('value', watch=True)
    def _update_value(self):
        self._slider.value = self.value
        self._start_edit.value = self.value[0]
        self._end_edit.value = self.value[1]

    def _sync_value(self, event):
        with param.edit_constant(self):
            self.param.update(**{event.name: event.new})

    def _sync_start_value(self, event):
        if event.name == 'value':
            end = self.value[1] if self.value else self.end
        else:
            end = self.value_throttled[1] if self.value_throttled else self.end
        with param.edit_constant(self):
            self.param.update(
                **{event.name: (event.new, end)}
            )

    def _sync_end_value(self, event):
        if event.name == 'value':
            start = self.value[0] if self.value else self.start
        else:
            start = self.value_throttled[0] if self.value_throttled else self.start
        with param.edit_constant(self):
            self.param.update(
                **{event.name: (start, event.new)}
            )

    @param.depends("start", "end", "fixed_start", "fixed_end", watch=True)
    def _update_bounds(self):
        self.param.value.softbounds = (self.start, self.end)
        self.param.value_throttled.softbounds = (self.start, self.end)
        self.param.value.bounds = (self.fixed_start, self.fixed_end)
        self.param.value_throttled.bounds = (self.fixed_start, self.fixed_end)

        # First changing _slider and then _value_edit,
        # because else _value_edit will change the _slider
        # with the jscallback.
        if self.fixed_start is not None:
            self._slider.start = max(self.fixed_start, self.start)
        if self.fixed_end is not None:
            self._slider.end = min(self.fixed_end, self.end)

        self._start_edit.start = self.fixed_start
        self._start_edit.end = self.fixed_end
        self._end_edit.start = self.fixed_start
        self._end_edit.end = self.fixed_end
