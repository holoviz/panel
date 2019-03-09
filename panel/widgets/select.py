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
from ..util import as_unicode, hashable
from .base import Widget
from .button import _ButtonBase, Button
from .input import TextInput



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
            hash_val = hashable(msg['value'])
            if hash_val in mapping:
                msg['value'] = mapping[hash_val]
            else:
                msg['value'] = list(self.options)[0]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            if msg['value'] is None:
                msg['value'] = None
            else:
                msg['value'] = self.options[msg['value']]
        msg.pop('options', None)
        return msg


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
            msg['value'] = [hashable(mapping[v]) for v in msg['value']
                            if v in mapping]
        if 'options' in msg:
            msg['options'] = list(msg['options'])
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = [self.options[v] for v in msg['value']]
        msg.pop('options', None)
        return msg


class AutocompleteInput(Widget):

    options = param.List(default=[])

    placeholder = param.String(default='')

    value = param.Parameter(default=None)

    _widget_type = _BkAutocompleteInput

    _rename = {'name': 'title', 'options': 'completions'}


class _RadioGroupBase(Select):

    def _process_param_change(self, msg):
        msg = super(Select, self)._process_param_change(msg)
        mapping = OrderedDict([(hashable(v), k) for k, v in self.options.items()])
        if msg.get('value') is not None:
            msg['active'] = list(mapping).index(msg.pop('value'))
        if 'options' in msg:
            msg['labels'] = list(msg.pop('options'))
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(Select, self)._process_property_change(msg)
        if 'active' in msg:
            msg['value'] = list(self.options.values())[msg.pop('active')]
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
        if 'active' in msg:
            msg['value'] = [list(self.options.values())[a] for a in msg.pop('active')]
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
        width = int((self.width-50)/2)
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
            False: TextInput(placeholder='Filter available options', width=width),
            True: TextInput(placeholder='Filter selected options', width=width)
        }
        self._search[False].param.watch(self._filter_options, 'value')
        self._search[True].param.watch(self._filter_options, 'value')

        # Define Layout
        blacklist = Column(self._search[False], self._lists[False])
        whitelist = Column(self._search[True], self._lists[True])
        buttons = Column(self._buttons[True], self._buttons[False], width=50)

        self._layout = Row(blacklist, Column(VSpacer(), buttons, VSpacer()), whitelist)

        self.param.watch(self._update_options, 'options')
        self.param.watch(self._update_value, 'value')
        self.link(self._lists[False], size='size')
        self.link(self._lists[True], size='size')

        self._selected = {False: [], True: []}
        self._query = {False: '', True: ''}

    @param.depends('disabled', watch=True)
    def _update_disabled(self):
        self._buttons[False].disabled = self.disabled
        self._buttons[True].disabled = self.disabled

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
