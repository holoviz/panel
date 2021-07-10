"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from six import string_types

import param
import numpy as np

from bokeh.models import CustomJS
from bokeh.models.formatters import TickFormatter
from bokeh.models.widgets import (
    DateSlider as _BkDateSlider, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, Slider as _BkSlider)

from ..config import config
from ..io import state
from ..util import (
    edit_readonly, param_reprs, unicode_repr, value_as_datetime, value_as_date
)
from ..viewable import Layoutable
from ..layout import Column, Row
from .base import Widget, CompositeWidget
from .input import IntInput, FloatInput, StaticText


class _SliderBase(Widget):

    bar_color = param.Color(default="#e6e6e6", doc="""
        Color of the slider bar as a hexidecimal RGB value.""")

    direction = param.ObjectSelector(default='ltr', objects=['ltr', 'rtl'],
                                     doc="""
        Whether the slider should go from left-to-right ('ltr') or
        right-to-left ('rtl')""")

    orientation = param.ObjectSelector(default='horizontal',
                                       objects=['horizontal', 'vertical'], doc="""
        Whether the slider should be oriented horizontally or
        vertically.""")

    show_value = param.Boolean(default=True, doc="""
        Whether to show the widget value.""")

    tooltips = param.Boolean(default=True, doc="""
        Whether the slider handle should display tooltips.""")

    _widget_type = _BkSlider

    __abstract = True

    def __init__(self, **params):
        if 'value' in params and 'value_throttled' in self.param:
            params['value_throttled'] = params['value']
        super().__init__(**params)

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self, ['value_throttled'])))

    def _process_property_change(self, msg):
        if config.throttled:
            if "value" in msg:
                del msg["value"]
            if "value_throttled" in msg:
                msg["value"] = msg["value_throttled"]
        return super()._process_property_change(msg)

    def _update_model(self, events, msg, root, model, doc, comm):
        if 'value_throttled' in msg:
            del msg['value_throttled']

        return super()._update_model(events, msg, root, model, doc, comm)


class ContinuousSlider(_SliderBase):

    format = param.ClassSelector(class_=string_types+(TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    _supports_embed = True

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super().__init__(**params)

    def _get_embed_state(self, root, values=None, max_opts=3):
        ref = root.ref['id']
        w_model, parent = self._models[ref]
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
            raise ValueError('Supplied embed states for %s widget outside '
                             'of valid range.' % type(self).__name__)

        # Replace model
        layout_opts = {k: v for k, v in self.param.get_param_values()
                       if k in Layoutable.param and k != 'name'}
        dw = DiscreteSlider(options=values, name=self.name, **layout_opts)
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

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    value_throttled = param.Number(default=None, constant=True)

    step = param.Number(default=0.1)

    _rename = {'name': 'title'}


class IntSlider(ContinuousSlider):

    value = param.Integer(default=0)

    value_throttled = param.Integer(default=None, constant=True)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    _rename = {'name': 'title'}

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = msg['value'] if msg['value'] is None else int(msg['value'])
        if 'value_throttled' in msg:
            throttled = msg['value_throttled']
            msg['value_throttled'] = throttled if throttled is None else int(throttled)
        return msg


class DateSlider(_SliderBase):

    value = param.Date(default=None)

    value_throttled = param.Date(default=None, constant=True)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _rename = {'name': 'title'}

    _source_transforms = {'value': None, 'value_throttled': None, 'start': None, 'end': None}

    _widget_type = _BkDateSlider

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = params.get('start', self.start)
        super().__init__(**params)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = value_as_date(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = value_as_date(msg['value_throttled'])
        return msg


class DiscreteSlider(CompositeWidget, _SliderBase):

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    value_throttled = param.Parameter(constant=True)

    formatter = param.String(default='%.3g')

    _source_transforms = {'value': None, 'value_throttled': None, 'options': None}

    _rename = {'formatter': None}

    _supports_embed = True

    _text_link = """
    var labels = {labels}
    target.text = labels[source.value]
    """

    _style_params = [p for p in list(Layoutable.param) if p != 'name'] + ['orientation']

    def __init__(self, **params):
        self._syncing = False
        super().__init__(**params)
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
        self.param.watch(self._update_value, 'value')
        self.param.watch(self._update_value, 'value_throttled')
        self.param.watch(self._update_style, self._style_params)

    def _update_options(self, *events):
        values, labels = self.values, self.labels
        if self.value not in values:
            value = 0
            self.value = values[0]
        else:
            value = values.index(self.value)

        self._slider = IntSlider(
            start=0, end=len(self.options)-1, value=value, tooltips=False,
            show_value=False, margin=(0, 5, 5, 5),
            orientation=self.orientation,
            _supports_embed=False
        )
        self._update_style()
        js_code = self._text_link.format(
            labels='['+', '.join([unicode_repr(l) for l in labels])+']'
        )
        self._jslink = self._slider.jslink(self._text, code={'value': js_code})
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')
        self._text.value = labels[value]
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
        if self._syncing:
            return
        try:
            self._syncing = True
            with param.edit_constant(self._slider):
                setattr(self._slider, event.name, index)
            if event.name == 'value':
                with param.discard_events(self._text):
                    self._text.value = self.labels[index]
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
        self._text.param.set_param(margin=text_margin, **text_style)
        self._slider.param.set_param(margin=slider_margin, **style)
        if self.width:
            style['width'] = self.width + l + r
        col_style = {k: v for k, v in style.items()
                     if k != 'orientation'}
        self._composite.param.set_param(**col_style)

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
                             "in the %s widgets' values list." % type(self).__name__)
        return self, model, values, lambda x: x.value, 'value', 'cb_obj.value'

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



class _RangeSliderBase(_SliderBase):

    value = param.Tuple(length=2)

    value_start = param.Parameter(readonly=True)

    value_end = param.Parameter(readonly=True)

    __abstract = True

    def __init__(self, **params):
        if 'value' not in params:
            params['value'] = (params.get('start', self.start),
                               params.get('end', self.end))
        params['value_start'], params['value_end'] = params['value']
        with edit_readonly(self):
            super().__init__(**params)

    @param.depends('value', watch=True)
    def _sync_values(self):
        vs, ve = self.value
        with edit_readonly(self):
            self.param.set_param(value_start=vs, value_end=ve)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple(msg['value'])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple(msg['value_throttled'])
        return msg


class RangeSlider(_RangeSliderBase):

    format = param.ClassSelector(class_=string_types+(TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    value = param.Range(default=(0, 1))

    value_start = param.Number(default=0, readonly=True)

    value_end = param.Number(default=1, readonly=True)

    value_throttled = param.Range(default=None, constant=True)

    start = param.Number(default=0)

    end = param.Number(default=1)

    step = param.Number(default=0.1)

    _rename = {'name': 'title', 'value_start': None, 'value_end': None}

    _widget_type = _BkRangeSlider

    def __init__(self, **params):
        super().__init__(**params)
        values = [self.value[0], self.value[1], self.start, self.end]
        if (all(v is None or isinstance(v, int) for v in values) and
            'step' not in params):
            self.step = 1


class IntRangeSlider(RangeSlider):

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = tuple([v if v is None else int(v)
                                  for v in msg['value']])
        if 'value_throttled' in msg:
            msg['value_throttled'] = tuple([v if v is None else int(v)
                                            for v in msg['value_throttled']])
        return msg


class DateRangeSlider(_RangeSliderBase):

    value = param.Tuple(default=(None, None), length=2)

    value_start = param.Date(default=None, readonly=True)

    value_end = param.Date(default=None, readonly=True)

    value_throttled = param.Tuple(default=None, length=2, constant=True)

    start = param.Date(default=None)

    end = param.Date(default=None)

    step = param.Number(default=1)

    _source_transforms = {'value': None, 'value_throttled': None,
                         'start': None, 'end': None, 'step': None}

    _rename = {'name': 'title', 'value_start': None, 'value_end': None}

    _widget_type = _BkDateRangeSlider

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if msg.get('value') == (None, None):
            del msg['value']
        if msg.get('value_throttled') == (None, None):
            del msg['value_throttled']
        return msg

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            v1, v2 = msg['value']
            msg['value'] = (value_as_datetime(v1), value_as_datetime(v2))
        if 'value_throttled' in msg:
            v1, v2 = msg['value_throttled']
            msg['value_throttled'] = (value_as_datetime(v1), value_as_datetime(v2))
        return msg


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

    _composite_type = Column
    _slider_widget = None
    _input_widget = None
    __abstract = True

    def __init__(self, **params):
        if not 'width' in params and not 'sizing_mode' in params:
            params['width'] = 300
        super().__init__(**params)
        self._label = StaticText(margin=0, align='end')
        self._slider = self._slider_widget(
            value=self.value, margin=(0, 0, 5, 0), sizing_mode='stretch_width'
        )
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')

        self._value_edit = self._input_widget(
            margin=0, align='end', css_classes=['slider-edit']
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
        self._update_editable()
        self._update_layout()
        self._update_name()
        self._update_slider()
        self._update_value()

    @param.depends('width', 'height', 'sizing_mode', watch=True)
    def _update_layout(self):
        self._value_edit.sizing_mode = self.sizing_mode
        if self.sizing_mode not in ('stretch_width', 'stretch_both'):
            w = (self.width or 300)//4
            self._value_edit.width = w

    @param.depends('editable', watch=True)
    def _update_editable(self):
        self._value_edit.disabled = not self.editable

    @param.depends('name', watch=True)
    def _update_name(self):
        if self.name:
            label = f'{self.name}:'
            margin = (0, 10, 0, 0)
        else:
            label = ''
            margin = (0, 0, 0, 0)
        self._label.param.set_param(**{'margin': margin, 'value': label})

    @param.depends('start', 'end', 'step', 'bar_color', 'direction',
                   'show_value', 'tooltips', 'format', watch=True)
    def _update_slider(self):
        self._slider.param.set_param(**{
            'format': self.format,
            'start': self.start,
            'end': self.end,
            'step': self.step,
            'bar_color': self.bar_color,
            'direction': self.direction,
            'show_value': self.show_value,
            'tooltips': self.tooltips
        })
        self._value_edit.step = self.step

    @param.depends('value', watch=True)
    def _update_value(self):
        self._slider.value = self.value
        self._value_edit.value = self.value

    def _sync_value(self, event):
        with param.edit_constant(self):
            self.param.set_param(**{event.name: event.new})


class EditableFloatSlider(_EditableContinuousSlider, FloatSlider):

    _slider_widget = FloatSlider
    _input_widget = FloatInput


class EditableIntSlider(_EditableContinuousSlider, IntSlider):

    _slider_widget = IntSlider
    _input_widget = IntInput


class EditableRangeSlider(CompositeWidget, _SliderBase):
    """
    The EditableRangeSlider extends the RangeSlider by adding text
    input fields to manually edit the range and potentially override
    the bounds.
    """

    editable = param.Tuple(default=(True, True), doc="""
        Whether the lower and upper values are editable.""")

    end = param.Number(default=1., doc="Upper bound of the range.")

    format = param.ClassSelector(default='0.0[0000]', class_=string_types+(TickFormatter,), doc="""
        Allows defining a custom format string or bokeh TickFormatter.""")

    show_value = param.Boolean(default=False, readonly=True, precedence=-1, doc="""
        Whether to show the widget value.""")

    start = param.Number(default=0., doc="Lower bound of the range.")

    step = param.Number(default=0.1, doc="Slider and number input step.")

    value = param.Range(default=(0, 1), doc="Current range value.")

    value_throttled = param.Range(default=None, constant=True)

    _composite_type = Column

    def __init__(self, **params):
        if not 'width' in params and not 'sizing_mode' in params:
            params['width'] = 300
        super().__init__(**params)
        self._label = StaticText(margin=0, align='end')
        self._slider = RangeSlider(margin=(0, 0, 5, 0), show_value=False)
        self._slider.param.watch(self._sync_value, 'value')
        self._slider.param.watch(self._sync_value, 'value_throttled')
        self._start_edit = FloatInput(min_width=50, margin=0, format=self.format,
                                      css_classes=['slider-edit'])
        self._end_edit = FloatInput(min_width=50, margin=(0, 0, 0, 10), format=self.format,
                                    css_classes=['slider-edit'])
        self._start_edit.param.watch(self._sync_start_value, 'value')
        self._start_edit.param.watch(self._sync_start_value, 'value_throttled')
        self._end_edit.param.watch(self._sync_end_value, 'value')
        self._end_edit.param.watch(self._sync_end_value, 'value_throttled')

        sep = StaticText(value='...', margin=(0, 2, 0, 2), align='end')
        edit = Row(self._label, self._start_edit, sep, self._end_edit,
                   sizing_mode='stretch_width', margin=0)
        self._composite.extend([edit, self._slider])
        self._slider.jscallback(args={'start': self._start_edit, 'end': self._end_edit}, value="""
        let [min, max] = cb_obj.value
        start.value = min
        end.value = max
        """)
        self._start_edit.jscallback(args={'slider': self._slider}, value="""
        if (cb_obj.value < slider.start) {
          slider.start = cb_obj.value
        } else if (cb_obj.value > slider.end) {
          slider.end = cb_obj.value
        }
        """)
        self._end_edit.jscallback(args={'slider': self._slider}, value="""
        if (cb_obj.value < slider.start) {
          slider.start = cb_obj.value
        } else if (cb_obj.value > slider.end) {
          slider.end = cb_obj.value
        }
        """)
        self._update_editable()
        self._update_layout()
        self._update_name()
        self._update_slider()
        self._update_value()

    @param.depends('editable', watch=True)
    def _update_editable(self):
        self._start_edit.disabled = not self.editable[0]
        self._end_edit.disabled = not self.editable[1]

    @param.depends('name', watch=True)
    def _update_name(self):
        if self.name:
            label = f'{self.name}:'
            margin = (0, 10, 0, 0)
        else:
            label = ''
            margin = (0, 0, 0, 0)
        self._label.param.set_param(**{'margin': margin, 'value': label})

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
        self._slider.param.set_param(**{
            'format': self.format,
            'start': self.start,
            'end': self.end,
            'step': self.step,
            'bar_color': self.bar_color,
            'direction': self.direction,
            'show_value': self.show_value,
            'tooltips': self.tooltips,
        })
        self._start_edit.step = self.step
        self._end_edit.step = self.step

    @param.depends('value', watch=True)
    def _update_value(self):
        self._slider.value = self.value
        self._start_edit.value = self.value[0]
        self._end_edit.value = self.value[1]

    def _sync_value(self, event):
        with param.edit_constant(self):
            self.param.set_param(**{event.name: event.new})

    def _sync_start_value(self, event):
        end = self.value[1] if event.name == 'value' else self.value_throttled[1]
        with param.edit_constant(self):
            self.param.set_param(
                **{event.name: (event.new, end)}
            )

    def _sync_end_value(self, event):
        start = self.value[0] if event.name == 'value' else self.value_throttled[0]
        with param.edit_constant(self):
            self.param.set_param(
                **{event.name: (start, event.new)}
            )
