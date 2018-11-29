"""
Provides a set of reactive widgets which provide bi-directional
communication between the rendered dashboard and the Widget parameters.
"""
from __future__ import absolute_import

import re
import ast
from collections import OrderedDict
from datetime import datetime

import param
import numpy as np
from bokeh.models import WidgetBox as _BkWidgetBox
from bokeh.models.widgets import (
    TextInput as _BkTextInput, Select as _BkSelect, Slider as _BkSlider,
    CheckboxGroup as _BkCheckboxGroup, DateRangeSlider as _BkDateRangeSlider,
    RangeSlider as _BkRangeSlider, DatePicker as _BkDatePicker,
    MultiSelect as _BkMultiSelect, Div as _BkDiv,Button as _BkButton,
    Toggle as _BkToggle, AutocompleteInput as _BkAutocompleteInput,
    CheckboxButtonGroup as _BkCheckboxButtonGroup
)

from .layout import Column, Row, Spacer, WidgetBox # noqa
from .models.widgets import Player as _BkPlayer
from .viewable import Reactive
from .util import as_unicode, push, value_as_datetime, hashable


class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='')

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    __abstract = True

    _widget_type = None

    _rename = {'name': 'title'}

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        super(Widget, self).__init__(**params)

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        return self._process_param_change(properties)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        in_box = isinstance(parent, _BkWidgetBox)
        if not in_box:
            parent = _BkWidgetBox()
        root = parent if root is None else root
        model = self._widget_type(**self._init_properties())

        # Link parameters and bokeh model
        params = [p for p in self.params()]
        properties = list(self._process_param_change(dict(self.get_param_values())))
        self._models[root.ref['id']] = model
        self._link_params(model, params, doc, root, comm)
        self._link_props(model, properties, doc, root, comm)

        if not in_box:
            parent.children = [model]
            return parent

        return model


class TextInput(Widget):

    value = param.String(default='', allow_None=True)

    placeholder = param.String(default='')

    _widget_type = _BkTextInput


class StaticText(Widget):

    value = param.Parameter(default=None)

    _widget_type = _BkDiv

    _format = '<b>{title}</b>: {value}'

    def _process_param_change(self, msg):
        msg = super(StaticText, self)._process_property_change(msg)
        msg.pop('title', None)
        if 'value' in msg:
            text = as_unicode(msg.pop('value'))
            if self.name:
                text = self._format.format(title=self.name, value=text)
            msg['text'] = text
        return msg


class AutocompleteInput(Widget):

    options = param.List(default=[])

    placeholder = param.String(default='')

    value = param.Parameter(default=None)

    _widget_type = _BkAutocompleteInput

    _rename = {'name': 'title', 'options': 'completions'}


class FloatSlider(Widget):

    start = param.Number(default=0.0)

    end = param.Number(default=1.0)

    value = param.Number(default=0.0)

    step = param.Number(default=0.1)

    _widget_type = _BkSlider


class IntSlider(Widget):

    value = param.Integer(default=0)

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)

    _widget_type = _BkSlider


class DatePicker(Widget):

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    _widget_type = _BkDatePicker

    _rename = {'start': 'min_date', 'end': 'max_date', 'name': 'title'}

    def _process_property_change(self, msg):
        msg = super(DatePicker, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = datetime.strptime(msg['value'][4:], '%b %d %Y')
        return msg


class RangeSlider(Widget):

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


class IntRangeSlider(Widget):

    start = param.Integer(default=0)

    end = param.Integer(default=1)

    step = param.Integer(default=1)


class DateRangeSlider(Widget):

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


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'info', 'danger'])

    _rename = {'name': 'label'}


class Button(_ButtonBase):

    clicks = param.Integer(default=0)

    _widget_type = _BkButton

    def on_click(self, callback):
        self.param.watch(callback, 'clicks')


class Toggle(_ButtonBase):

    active = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _widget_type = _BkToggle


class LiteralInput(Widget):
    """
    LiteralInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    type = param.ClassSelector(default=None, class_=type,
                               is_instance=True)

    value = param.Parameter(default=None)

    _widget_type = _BkTextInput

    def __init__(self, **params):
        super(LiteralInput, self).__init__(**params)
        self._state = ''
        self._validate(None)
        self.param.watch(self._validate, 'value')

    def _validate(self, event):
        if self.type is None: return
        new = self.value
        if not isinstance(new, self.type):
            if event:
                self.value = event.old
            raise ValueError('LiteralInput expected %s type but value %s '
                             'is of type %s.' %
                             (self.type.__name__, new, type(new).__name__))

    def _process_property_change(self, msg):
        msg = super(LiteralInput, self)._process_property_change(msg)
        new_state = ''
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = ast.literal_eval(value)
            except:
                new_state = ' (invalid)'
                value = self.value
            else:
                if self.type and not isinstance(value, self.type):
                    new_state = ' (wrong type)'
                    value = self.value
            msg['value'] = value
        msg['name'] = msg.get('title', self.name).replace(self._state, '') + new_state
        self._state = new_state
        return msg

    def _process_param_change(self, msg):
        msg.pop('type', None)
        if 'value' in msg:
            msg['value'] = '' if msg['value'] is None else as_unicode(msg['value'])
        msg['title'] = self.name
        return msg


class DatetimeInput(LiteralInput):
    """
    DatetimeInput allows declaring Python literals using a text
    input widget. Optionally a type may be declared.
    """

    format = param.String(default='%Y-%m-%d %H:%M:%S', doc="""
        Datetime format used for parsing and formatting the datetime.""")

    value = param.Date(default=None)

    start = param.Date(default=None)

    end = param.Date(default=None)

    type = datetime

    def __init__(self, **params):
        super(DatetimeInput, self).__init__(**params)
        self.param.watch(self._validate, 'value')
        self._validate(None)

    def _validate(self, event):
        new = self.value
        if new is not None and ((self.start is not None and self.start > new) or
                                (self.end is not None and self.end < new)):
            value = datetime.strftime(new, self.format)
            start = datetime.strftime(self.start, self.format)
            end = datetime.strftime(self.end, self.format)
            if event:
                self.value = event.old
            raise ValueError('DatetimeInput value must be between {start} and {end}, '
                             'supplied value is {value}'.format(start=start, end=end,
                                                                value=value))

    def _process_property_change(self, msg):
        msg = Widget._process_property_change(self, msg)
        new_state = ''
        if 'value' in msg:
            value = msg.pop('value')
            try:
                value = datetime.strptime(value, self.format)
            except:
                new_state = ' (invalid)'
                value = self.value
            else:
                if value is not None and ((self.start is not None and self.start > value) or
                                          (self.end is not None and self.end < value)):
                    new_state = ' (out of bounds)'
                    value = self.value
            msg['value'] = value
        msg['name'] = msg.get('title', self.name).replace(self._state, '') + new_state
        self._state = new_state
        return msg

    def _process_param_change(self, msg):
        msg = {k: v for k, v in msg.items() if k not in ('type', 'format', 'start', 'end')}
        if 'value' in msg:
            value = msg['value']
            if value is None:
                value = ''
            else:
                value = datetime.strftime(msg['value'], self.format)
            msg['value'] = value
        msg['title'] = self.name
        return msg


class Checkbox(Widget):

    value = param.Boolean(default=False)

    _widget_type = _BkCheckboxGroup

    def _process_property_change(self, msg):
        msg = super(Checkbox, self)._process_property_change(msg)
        if 'active' in msg:
            msg['value'] = 0 in msg.pop('active')
        return msg

    def _process_param_change(self, msg):
        msg = super(Checkbox, self)._process_param_change(msg)
        if 'value' in msg:
             msg['active'] = [0] if msg.pop('value', None) else []
        if 'title' in msg:
            msg['labels'] = [msg.pop('title')]
        return msg


class Select(Widget):

    options = param.Dict(default={})

    value = param.Parameter(default=None)

    _widget_type = _BkSelect

    def __init__(self, **params):
        options = params.get('options', None)
        if isinstance(options, list):
            params['options'] = OrderedDict([(as_unicode(o), o) for o in options])
        super(Select, self).__init__(**params)
        options = list(self.options.values())
        if self.value is None and None not in options and options:
            self.value = options[0]

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {hashable(v): k for k, v in self.options.items()}
        if msg.get('value') is not None:
            msg['value'] = mapping[hashable(msg['value'])]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = self.options[msg['value']]
        msg.pop('options', None)
        return msg


class RadioButtons(Select):

    value = param.List(default=[])

    _widget_type = _BkCheckboxGroup

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = OrderedDict([(hashable(v), k) for k, v in self.options.items()])
        if msg.get('value') is not None:
            msg['active'] = [list(mapping).index(v) for v in msg.pop('value')]
        if 'options' in msg:
            msg['labels'] = list(msg.pop('options'))
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if msg.get('active', []):
            msg['value'] = [list(self.options.values())[a] for a in msg.pop('active')]
        return msg


class ToggleButtons(RadioButtons):

    _widget_type = _BkCheckboxButtonGroup


class MultiSelect(Select):

    size = param.Integer(default=4, doc="""
        The number of items displayed at once (i.e. determines the
        widget height).""")

    value = param.List(default=[])

    _widget_type = _BkMultiSelect

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = {hashable(v): k for k, v in self.options.items()}
        if 'value' in msg:
            msg['value'] = [hashable(mapping[v]) for v in msg['value']]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = [self.options[v] for v in msg['value']]
        msg.pop('options', None)
        return msg


class DiscreteSlider(Widget):

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
        title = '<b>%s</b>: ' % (self.name if self.name else '')
        if isinstance(self.options, dict):
            return [title + o for o in self.options]
        else:
            return [title + (self.formatter % o) for o in self.options]

    @property
    def values(self):
        return list(self.options.values()) if isinstance(self.options, dict) else self.options

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = _BkWidgetBox()
        parent = parent or model
        root = root or parent
        msg = self._init_properties()
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
            else:
                doc.add_next_tick_callback(update_model)

        ref = root.ref['id']
        for p in params:
            self._callbacks[ref].append(self.param.watch(param_change, p))

    def _process_param_change(self, msg):
        title = '<b>%s</b>: ' % (self.name if self.name else '')
        if 'name' in msg:
            msg['text'] = title + self.formatter % self.value
        if 'options' in msg:
            msg['start'] = 0
            msg['end'] = len(msg['options']) - 1
            options = msg['options']
            if isinstance(options, dict):
                msg['labels'] = list(options)
                options = list(options.values())
            else:
                msg['labels'] = [title + (self.formatter % o) for o in options]
            if self.value not in options:
                self.value = options[0]
        if 'value' in msg:
            value = msg['value']
            if value not in self.values:
                self.value = self.values[0]
                msg.pop('value')
                return msg
            label = self.labels[self.values.index(value)]
            msg['value'] = self.values.index(value)
            msg['text'] = label
        return msg

    def _process_property_change(self, msg):
        if 'value' in msg:
            msg['value'] = self.values[msg['value']]
        return msg


class PlayerBase(Widget):

    interval = param.Integer(default=500, doc="Interval between updates")

    loop_policy = param.ObjectSelector(default='once',
                                       objects=['once', 'loop', 'reflect'], doc="""
       Policy used when player hits last frame""")

    step = param.Integer(default=1, doc="""
       Number of frames to step forward and back by on each event.""")

    height = param.Integer(default=250, readonly=True)

    _widget_type = _BkPlayer

    _rename = {'name': None}

    __abstract = True


class Player(PlayerBase):
    """
    The Player provides controls to play and skip through a number of
    frames defined by explicit start and end values.  The speed at
    which the widget plays is defined by the interval, but it is also
    possible to skip frames using the step parameter.
    """

    start = param.Integer(default=0, doc="Lower bound on the slider value")

    end = param.Integer(default=10, doc="Upper bound on the slider value")

    value = param.Integer(default=0, doc="Current player value")

    def __init__(self, **params):
        if 'length' in params:
            if 'start' in params or 'end' in params:
                raise ValueError('Supply either length or start and end to Player not both')
            params['start'] = 0
            params['end'] = params.pop('length')-1
        elif params.get('start', 0) > 0 and not 'value' in params:
            params['value'] = params['start']
        super(Player, self).__init__(**params)


class DiscretePlayer(PlayerBase):
    """
    The DiscretePlayer provides controls to iterate through a list of
    discrete options.  The speed at which the widget plays is defined
    by the interval, but it is also possible to skip items using the
    step parameter."""

    interval = param.Integer(default=500, doc="Interval between updates")

    options = param.ClassSelector(default=[], class_=(dict, list))

    value = param.Parameter()

    _rename = {'name': None, 'options': None}

    def _process_param_change(self, msg):
        options = msg.get('options', self.options)
        if isinstance(options, list):
            values = options
        else:
            values = list(options.values())
        if 'options' in msg:
            msg['start'] = 0
            msg['end'] = len(options) - 1
            if self.value not in values:
                self.value = values[0]
        if 'value' in msg:
            value = msg['value']
            msg['value'] = values.index(value)
        return super(DiscretePlayer, self)._process_param_change(msg)

    def _process_property_change(self, msg):
        options = self.options
        if isinstance(options, list):
            values = options
        else:
            values = list(options.values())
        if 'value' in msg:
            msg['value'] = values[msg['value']]
        return msg


class CrossSelector(MultiSelect):
    """
    A composite widget which allows selecting from a list of items
    by moving them between two lists. Supports filtering values by
    name to select them in bulk.
    """

    width = param.Integer(default=600, doc="""
       The number of options shown at once (note this is the
       only way to control the height of this widget)""")

    height = param.Integer(default=200, doc="""
       The number of options shown at once (note this is the
       only way to control the height of this widget)""")

    size = param.Integer(default=10, doc="""
       The number of options shown at once (note this is the
       only way to control the height of this widget)""")

    def __init__(self, *args, **kwargs):
        super(CrossSelector, self).__init__(**kwargs)
        # Compute selected and unselected values

        mapping = {hashable(v): k for k, v in self.options.items()}
        selected = [mapping[hashable(v)] for v in kwargs.get('value', [])]
        unselected = [k for k in self.options if k not in selected]

        # Define whitelist and blacklist
        width = int((self.width-100)/2)
        self._lists = {
            False: MultiSelect(options=unselected, size=self.size,
                               height=self.height-50, width=width),
            True: MultiSelect(options=selected, size=self.size,
                              height=self.height-50, width=width)
        }
        self._lists[False].param.watch(self._update_selection, 'value')
        self._lists[True].param.watch(self._update_selection, 'value')

        # Define buttons
        self._buttons = {False: Button(name='<<', width=50),
                         True: Button(name='>>', width=50)}

        self._buttons[False].param.watch(self._apply_selection, 'clicks')
        self._buttons[True].param.watch(self._apply_selection, 'clicks')

        # Define search
        self._search = {
            False: TextInput(placeholder='Filter available options'),
            True: TextInput(placeholder='Filter selected options')
        }
        self._search[False].param.watch(self._filter_options, 'value')
        self._search[True].param.watch(self._filter_options, 'value')

        # Define Layout
        blacklist = WidgetBox(self._search[False], self._lists[False], width=width+10)
        whitelist = WidgetBox(self._search[True], self._lists[True], width=width+10)
        buttons = WidgetBox(self._buttons[True], self._buttons[False], width=70)

        self._layout = Row(blacklist, Column(Spacer(height=110), buttons), whitelist)

        self.param.watch(self._update_options, 'options')
        self.param.watch(self._update_value, 'value')
        self.link(self._lists[False], size='size')
        self.link(self._lists[True], size='size')

        self._selected = {False: [], True: []}
        self._query = {False: '', True: ''}

    def _update_value(self, event):
        mapping = {hashable(v): k for k, v in self.options.items()}
        selected = OrderedDict([(mapping[k], mapping[k]) for k in event.new])
        unselected = OrderedDict([(k, k) for k in self.options if k not in selected])
        self._lists[True].options = selected
        self._lists[True].value = []
        self._lists[False].options = unselected
        self._lists[False].value = []

    def _update_options(self, event):
        """
        Updates the options of each of the sublists after the options
        for the whole widget are updated.
        """
        self._selected[False] = []
        self._selected[True] = []
        self._lists[True].options = {}
        self._lists[True].value = []
        self._lists[False].options = OrderedDict([(k, k) for k in event.new])
        self._lists[False].value = []

    def _apply_filters(self):
        self._apply_query(False)
        self._apply_query(True)

    def _filter_options(self, event):
        """
        Filters unselected options based on a text query event.
        """
        selected = event.obj is self._search[True]
        self._query[selected] = event.new
        self._apply_query(selected)

    def _apply_query(self, selected):
        query = self._query[selected]
        other = self._lists[not selected].options
        options = OrderedDict([(k, k) for k in self.options if k not in other])
        if not query:
            self._lists[selected].options = options
            self._lists[selected].value = []
        else:
            try:
                match = re.compile(query)
                matches = list(filter(match.search, options))
            except:
                matches = list(options)
            self._lists[selected].options = options if options else {}
            self._lists[selected].value = [m for m in matches]

    def _update_selection(self, event):
        """
        Updates the current selection in each list.
        """
        selected = event.obj is self._lists[True]
        self._selected[selected] = [v for v in event.new if v != '']

    def _apply_selection(self, event):
        """
        Applies the current selection depending on which button was
        pressed.
        """
        selected = event.obj is self._buttons[True]

        new = OrderedDict([(k, self.options[k]) for k in self._selected[not selected]])
        old = self._lists[selected].options
        other = self._lists[not selected].options

        merged = OrderedDict([(k, k) for k in list(old)+list(new)])
        leftovers = OrderedDict([(k, k) for k in other if k not in new])
        self._lists[selected].options = merged if merged else {}
        self._lists[not selected].options = leftovers if leftovers else {}
        self.value = [self.options[o] for o in self._lists[True].options if o != '']
        self._apply_filters()

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._layout._get_model(doc, root, parent, comm)
