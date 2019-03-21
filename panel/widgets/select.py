"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import absolute_import, division, unicode_literals

import re

from collections import OrderedDict

import param

from bokeh.models.widgets import (
    AutocompleteInput as _BkAutocompleteInput, CheckboxGroup as _BkCheckboxGroup,
    CheckboxButtonGroup as _BkCheckboxButtonGroup, MultiSelect as _BkMultiSelect,
    RadioButtonGroup as _BkRadioButtonGroup, RadioGroup as _BkRadioBoxGroup,
    Select as _BkSelect)

from ..layout import Column, Row, VSpacer
from ..util import as_unicode, isIn, indexOf
from ..viewable import Layoutable
from .base import Widget, CompositeWidget
from .button import _ButtonBase, Button
from .input import TextInput


class SelectBase(Widget):

    options = param.ClassSelector(default=[], class_=(dict, list))

    __abstract = True

    @property
    def labels(self):
        return [as_unicode(o) for o in self.options]

    @property
    def values(self):
        if isinstance(self.options, dict):
            return list(self.options.values())
        else:
            return self.options

    @property
    def _items(self):
        return dict(zip(self.labels, self.values))


class Select(SelectBase):

    value = param.Parameter(default=None)

    _widget_type = _BkSelect

    _supports_embed = True

    def __init__(self, **params):
        super(Select, self).__init__(**params)
        values = self.values
        if self.value is None and None not in values and values:
            self.value = values[0]

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        labels, values = self.labels, self.values
        if 'value' in msg:
            val = msg['value']
            if isIn(val, values):
                msg['value'] = labels[indexOf(val, values)]
            elif values:
                self.value = self.values[0]
            elif self.value is not None:
                self.value = None

        if 'options' in msg:
            msg['options'] = labels
            val = self.value
            if values:
                if not isIn(val, values):
                    self.value = values[0]
            elif val is not None:
                self.value = None
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            if not self.values:
                pass
            elif msg['value'] is None:
                msg['value'] = self.values[0]
            else:
                msg['value'] = self._items[msg['value']]
        msg.pop('options', None)
        return msg

    def _get_embed_state(self, root, max_opts=3):
        return (self, self._models[root.ref['id']][0], self.values,
                lambda x: x.value, 'value', 'cb_obj.value')


class MultiSelect(Select):

    size = param.Integer(default=4, doc="""
        The number of items displayed at once (i.e. determines the
        widget height).""")

    value = param.List(default=[])

    _widget_type = _BkMultiSelect

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        labels, values = self.labels, self.values
        if 'value' in msg:
            msg['value'] = [labels[indexOf(v, values)] for v in msg['value']
                            if isIn(v, values)]

        if 'options' in msg:
            msg['options'] = labels
            if any(not isIn(v, values) for v in self.value):
                self.value = [v for v in self.value if isIn(v, values)]
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            labels = self.labels
            msg['value'] = [self._items[v] for v in msg['value']
                            if v in labels]
        msg.pop('options', None)
        return msg


class AutocompleteInput(Widget):

    options = param.List(default=[])

    placeholder = param.String(default='')

    value = param.Parameter(default=None)

    _widget_type = _BkAutocompleteInput

    _rename = {'name': 'title', 'options': 'completions'}


class _RadioGroupBase(Select):

    __abstract = True

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        values = self.values
        if 'value' in msg:
            value = msg.pop('value')
            if value in values:
                msg['active'] = indexOf(value, values)
            else:
                if self.value is not None:
                    self.value = None
                msg['active'] = None

        if 'options' in msg:
            msg['labels'] = list(msg.pop('options'))
            value = self.value
            if not isIn(value, values):
                self.value = None
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'active' in msg:
            index = msg.pop('active')
            if index is None:
                msg['value'] = None
            else:
                msg['value'] = list(self.values)[index]
        return msg


class RadioButtonGroup(_RadioGroupBase, _ButtonBase):

    _widget_type = _BkRadioButtonGroup

    _rename = {'name': 'title'}


class RadioBoxGroup(_RadioGroupBase):

    inline = param.Boolean(default=False, doc="""
        Whether the items be arrange vertically (``False``) or
        horizontally in-line (``True``).""")

    _widget_type = _BkRadioBoxGroup


class _CheckGroupBase(Select):

    value = param.List(default=[])

    __abstract = True

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        values = self.values
        if 'value' in msg:
            msg['active'] = [indexOf(v, values) for v in msg.pop('value')
                             if isIn(v, values)]
        if 'options' in msg:
            msg['labels'] = list(msg.pop('options'))
            if any(not isIn(v, values) for v in self.value):
                self.value = [v for v in self.value if isIn(v, values)]
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'active' in msg:
            values = self.values
            msg['value'] = [values[a] for a in msg.pop('active')]
        return msg


class CheckButtonGroup(_CheckGroupBase, _ButtonBase):

    _widget_type = _BkCheckboxButtonGroup

    _rename = {'name': 'title'}


class CheckBoxGroup(_CheckGroupBase):

    inline = param.Boolean(default=False, doc="""
        Whether the items be arrange vertically (``False``) or
        horizontally in-line (``True``).""")

    _widget_type = _BkCheckboxGroup


class ToggleGroup(Select):
    """This class is a factory of ToggleGroup widgets.

    A ToggleGroup is a group of widgets which can be switched 'on' or 'off'.

    Two types of widgets are available through the widget_type argument :
        - 'button' (default)
        - 'box'

    Two different behaviors are available through behavior argument:
        - 'check' (default) : Any number of widgets can be selected. In this case value is a 'list' of objects
        - 'radio' : One and only one widget is switched on. In this case value is an 'object'

    """

    _widgets_type = ['button', 'box']
    _behaviors = ['check', 'radio']

    def __new__(cls, widget_type='button', behavior='check', **params):

        if widget_type not in ToggleGroup._widgets_type:
            raise ValueError('widget_type {} is not valid. Valid options are {}'
                             .format(widget_type, ToggleGroup._widgets_type))
        if behavior not in ToggleGroup._behaviors:
            raise ValueError('behavior {} is not valid. Valid options are {}'
                             .format(widget_type, ToggleGroup._behaviors))

        if behavior == 'check':
            if widget_type == 'button':
                return CheckButtonGroup(**params)
            else:
                return CheckBoxGroup(**params)
        else:
            if isinstance(params.get('value'), list):
                raise ValueError('Radio buttons require a single value, '
                                 'found: %s' % params['value'])
            if widget_type == 'button':
                return RadioButtonGroup(**params)
            else:
                return RadioBoxGroup(**params)


class CrossSelector(CompositeWidget, MultiSelect):
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

        labels, values = self.labels, self.values
        selected = [labels[indexOf(v, values)] for v in kwargs.get('value', [])
                    if isIn(v, values)]
        unselected = [k for k in labels if k not in selected]

        # Define whitelist and blacklist
        layout = dict(sizing_mode=self.sizing_mode, width_policy=self.width_policy,
                      height_policy=self.height_policy, background=self.background)
        width = int((self.width-50)/2)
        self._lists = {
            False: MultiSelect(options=unselected, size=self.size,
                               height=self.height-50, width=width, **layout),
            True: MultiSelect(options=selected, size=self.size,
                              height=self.height-50, width=width, **layout)
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
            False: TextInput(placeholder='Filter available options', width=width),
            True: TextInput(placeholder='Filter selected options', width=width)
        }
        self._search[False].param.watch(self._filter_options, 'value')
        self._search[True].param.watch(self._filter_options, 'value')

        # Define Layout
        blacklist = Column(self._search[False], self._lists[False])
        whitelist = Column(self._search[True], self._lists[True])
        buttons = Column(self._buttons[True], self._buttons[False], width=50)

        self._composite = Row(blacklist, Column(VSpacer(), buttons, VSpacer()), whitelist,
                              css_classes=self.css_classes, margin=self.margin, **layout)

        self._selected = {False: [], True: []}
        self._query = {False: '', True: ''}
        self.param.watch(self._update_layout_params, list(Layoutable.param))


    def _update_layout_params(self, *events):
        for event in events:
            if event.name in ['css_classes']:
                setattr(self._composite, event.name, event.new)
            elif event.name in ['sizing_mode', 'width_policy', 'height_policy',
                                'background', 'margin']:
                setattr(self._composite, event.name, event.new)
                setattr(self._lists[True], event.name, event.new)
                setattr(self._lists[False], event.name, event.new)
            elif event.name == 'height':
                setattr(self._lists[True], event.name, event.new-50)
                setattr(self._lists[False], event.name, event.new-50)
            elif event.name == 'width':
                width = int((event.new-50)/2)
                setattr(self._lists[True], event.name, width)
                setattr(self._lists[False], event.name, width)

        
    @param.depends('size', watch=True)
    def _update_size(self):
        self._lists[False].size = self.size
        self._lists[True].size = self.size

    @param.depends('disabled', watch=True)
    def _update_disabled(self):
        self._buttons[False].disabled = self.disabled
        self._buttons[True].disabled = self.disabled

    @param.depends('value', watch=True)
    def _update_value(self):
        labels, values = self.labels, self.values 
        selected = [labels[indexOf(v, values)] for v in self.value
                    if isIn(v, values)]
        unselected = [k for k in labels if k not in selected]
        self._lists[True].options = selected
        self._lists[True].value = []
        self._lists[False].options = unselected
        self._lists[False].value = []

    @param.depends('options', watch=True)
    def _update_options(self):
        """
        Updates the options of each of the sublists after the options
        for the whole widget are updated.
        """
        self._selected[False] = []
        self._selected[True] = []
        self._lists[True].options = []
        self._lists[True].value = []
        self._lists[False].options = self.labels
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
        other = self._lists[not selected].labels
        labels = self.labels
        options = [k for k in labels if k not in other]
        if not query:
            self._lists[selected].options = options
            self._lists[selected].value = []
        else:
            try:
                match = re.compile(query)
                matches = list(filter(match.search, options))
            except:
                matches = list(options)
            self._lists[selected].options = options if options else []
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

        new = OrderedDict([(k, self._items[k]) for k in self._selected[not selected]])
        old = self._lists[selected].options
        other = self._lists[not selected].options

        merged = OrderedDict([(k, k) for k in list(old)+list(new)])
        leftovers = OrderedDict([(k, k) for k in other if k not in new])
        self._lists[selected].options = merged if merged else {}
        self._lists[not selected].options = leftovers if leftovers else {}
        self.value = [self._items[o] for o in self._lists[True].options if o != '']
        self._apply_filters()

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._composite._get_model(doc, root, parent, comm)
