"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
import re

from collections import OrderedDict
import itertools

import param

from bokeh.models.widgets import (
    AutocompleteInput as _BkAutocompleteInput, CheckboxGroup as _BkCheckboxGroup,
    CheckboxButtonGroup as _BkCheckboxButtonGroup, MultiSelect as _BkMultiSelect,
    RadioButtonGroup as _BkRadioButtonGroup, RadioGroup as _BkRadioBoxGroup,
    MultiChoice as _BkMultiChoice
)

from ..layout import Column, VSpacer
from ..models import SingleSelect as _BkSingleSelect, CustomSelect
from ..util import isIn, indexOf
from .base import Widget, CompositeWidget
from .button import _ButtonBase, Button
from .input import TextInput, TextAreaInput


class SelectBase(Widget):

    options = param.ClassSelector(default=[], class_=(dict, list))

    __abstract = True

    @property
    def labels(self):
        return [str(o) for o in self.options]

    @property
    def values(self):
        if isinstance(self.options, dict):
            return list(self.options.values())
        else:
            return self.options

    @property
    def _items(self):
        return OrderedDict(zip(self.labels, self.values))



class SingleSelectBase(SelectBase):

    value = param.Parameter(default=None)

    _supports_embed = True

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        values = self.values
        if self.value is None and None not in values and values:
            self.value = values[0]

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        labels, values = self.labels, self.values
        unique = len(set(self.unicode_values)) == len(labels)
        if 'value' in msg:
            val = msg['value']
            if isIn(val, values):
                unicode_values = self.unicode_values if unique else labels
                msg['value'] = unicode_values[indexOf(val, values)]
            elif values:
                self.value = self.values[0]
            else:
                self.value = None
                msg['value'] = ''

        if 'options' in msg:
            if isinstance(self.options, dict):
                if unique:
                    options = [(v, l) for l,v in zip(labels, self.unicode_values)]
                else:
                    options = labels
                msg['options'] = options
            else:
                msg['options'] = self.unicode_values
            val = self.value
            if values:
                if not isIn(val, values):
                    self.value = values[0]
            else:
                self.value = None
        return msg

    @property
    def unicode_values(self):
        return [str(v) for v in self.values]

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'value' in msg:
            if not self.values:
                pass
            elif msg['value'] == '':
                msg['value'] = self.values[0] if self.values else None
            else:
                if isIn(msg['value'], self.unicode_values):
                    idx = indexOf(msg['value'], self.unicode_values)
                else:
                    idx = indexOf(msg['value'], self.labels)
                msg['value'] = self._items[self.labels[idx]]
        msg.pop('options', None)
        return msg

    def _get_embed_state(self, root, values=None, max_opts=3):
        if values is None:
            values = self.values
        elif any(v not in self.values for v in values):
            raise ValueError("Supplied embed states were not found "
                             "in the %s widgets values list." %
                             type(self).__name__)
        return (self, self._models[root.ref['id']][0], values,
                lambda x: x.value, 'value', 'cb_obj.value')


class Select(SingleSelectBase):
    """
    The `Select` widget allows selecting a value from a list or dictionary of
    `options` by selecting it from a dropdown menu or selection area.

    It falls into the broad category of single-value, option-selection widgets
    that provide a compatible API and include the `RadioBoxGroup`,
    `AutocompleteInput` and `DiscreteSlider` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/Select.html

    :Example:

    >>> Select(name='Study', options=['Biology', 'Chemistry', 'Physics'])
    """

    disabled_options = param.List(default=[], doc="""
        Optional list of ``options`` that are disabled, i.e. unusable and
        un-clickable. If ``options`` is a dictionary the list items must be
        dictionary values.""")

    groups = param.Dict(default=None, doc="""
        Dictionary whose keys are used to visually group the options
        and whose values are either a list or a dictionary of options
        to select from. Mutually exclusive with ``options``  and valid only
        if ``size`` is 1.""")

    size = param.Integer(default=1, bounds=(1, None), doc="""
        Declares how many options are displayed at the same time.
        If set to 1 displays options as dropdown otherwise displays
        scrollable area.""")

    _source_transforms = {'size': None, 'groups': None}

    @property
    def _widget_type(self):
        return CustomSelect if self.size == 1 else _BkSingleSelect

    def __init__(self, **params):
        super().__init__(**params)
        if self.size == 1:
            self.param.size.constant = True
        self._callbacks.extend([
            self.param.watch(
                self._validate_options_groups,
                ['options', 'groups']
            ),
            self.param.watch(
                self._validate_disabled_options,
                ['options', 'disabled_options', 'value']
            ),
        ])
        self._validate_options_groups()
        self._validate_disabled_options()

    def _validate_disabled_options(self, *events):
        if self.disabled_options and self.disabled_options == self.values:
            raise ValueError(
                f'All the options of a {type(self).__name__} '
                'widget cannot be disabled.'
            )
        not_in_opts = [
            dopts
            for dopts in self.disabled_options
            if dopts not in (self.values or [])
        ]
        if not_in_opts:
            raise ValueError(
                f'Cannot disable non existing options of {type(self).__name__}: {not_in_opts}'
            )
        if len(events) == 1:
            if events[0].name == 'value' and self.value in self.disabled_options:
                raise ValueError(
                    f'Cannot set the value of {type(self).__name__} to '
                    f'{self.value!r} as it is a disabled option.'
                )
            elif events[0].name == 'disabled_options' and self.value in self.disabled_options:
                raise ValueError(
                    f'Cannot set disabled_options of {type(self).__name__} to a list that '
                    f'includes the current value {self.value!r}.'
                )
        if self.value in self.disabled_options:
            raise ValueError(
                f'Cannot initialize {type(self).__name__} with value {self.value!r} '
                'as it is one of the disabled options.'
            )


    def _validate_options_groups(self, *events):
        if self.options and self.groups:
            raise ValueError(
                f'{type(self).__name__} options and groups parameters '
                'are mutually exclusive.'
            )
        if self.size > 1 and self.groups:
            raise ValueError(
                f'{type(self).__name__} with size > 1 doe not support the'
                ' `groups` parameter, use `options` instead.'
            )

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if msg.get('size') == 1:
            msg.pop('size')
        groups = msg.pop('groups', None)
        if groups is not None:
            if (all(isinstance(values, dict) for values in groups.values()) is False
               and  all(isinstance(values, list) for values in groups.values()) is False):
                raise ValueError(
                    'The values of the groups dictionary must be all of '
                    'the dictionary or the list type.'
                )
            labels, values = self.labels, self.values
            unique = len(set(self.unicode_values)) == len(labels)
            if groups:
                if isinstance(next(iter(self.groups.values())), dict):
                    if unique:
                        options = {
                            group: [(str(value), label) for label, value in subd.items()]
                            for group, subd in groups.items()
                        }
                    else:
                        options = {
                            group: [str(v) for v in self.groups[group]]
                            for group in groups.keys()
                        }
                    msg['options'] = options
                else:
                    msg['options'] = {
                        group: [(str(value), str(value)) for value in values]
                        for group, values in groups.items()
                    }
            val = self.value
            if values:
                if not isIn(val, values):
                    self.value = values[0]
            else:
                self.value = None
        return msg

    @property
    def labels(self):
        if self.options:
            return super().labels
        else:
            if not self.groups:
                return {}
            else:
                return list(map(str, itertools.chain(*self.groups.values())))

    @property
    def values(self):
        if self.options:
            return super().values
        else:
            if not self.groups:
                return []
            if isinstance(next(iter(self.groups.values())), dict):
                return [v for subd in self.groups.values() for v in subd.values()]
            else:
                return list(itertools.chain(*self.groups.values()))


class _MultiSelectBase(SingleSelectBase):

    value = param.List(default=[])

    _supports_embed = False

    def _process_param_change(self, msg):
        msg = super(SingleSelectBase, self)._process_param_change(msg)
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
        msg = super(SingleSelectBase, self)._process_property_change(msg)
        if 'value' in msg:
            labels = self.labels
            msg['value'] = [self._items[v] for v in msg['value']
                            if v in labels]
        msg.pop('options', None)
        return msg


class MultiSelect(_MultiSelectBase):
    """
    The `MultiSelect` widget allows selecting multiple values from a list of
    `options`.

    It falls into the broad category of multi-value, option-selection widgets
    that provide a compatible API and include the`CrossSelector`,
    `CheckBoxGroup` and `CheckButtonGroup` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/MultiSelect.html

    :Example:

    >>> MultiSelect(
    ...     name='Frameworks', value=['Bokeh', 'Panel'],
    ...     options=['Bokeh', 'Dash', 'Panel', 'Streamlit', 'Voila'], size=8
    ... )
    """

    size = param.Integer(default=4, doc="""
        The number of items displayed at once (i.e. determines the
        widget height).""")

    _widget_type = _BkMultiSelect


class MultiChoice(_MultiSelectBase):
    """
    The `MultiChoice` widget allows selecting multiple values from a list of
    `options`.

    It falls into the broad category of multi-value, option-selection widgets
    that provide a compatible API and include the `MultiSelect`,
    `CrossSelector`, `CheckBoxGroup` and `CheckButtonGroup` widgets.

    The `MultiChoice` widget provides a much more compact UI than
    `MultiSelect`.

    Reference: https://panel.holoviz.org/reference/widgets/MultiChoice.html

    :Example:

    >>> MultiChoice(
    ...     name='Favourites', value=['Panel', 'hvPlot'],
    ...     options=['Panel', 'hvPlot', 'HoloViews', 'GeoViews', 'Datashader', 'Param', 'Colorcet'],
    ...     max_items=2
    ... )
    """

    delete_button = param.Boolean(default=True, doc="""
        Whether to display a button to delete a selected option.""")

    max_items = param.Integer(default=None, bounds=(1, None), doc="""
        Maximum number of options that can be selected.""")

    option_limit = param.Integer(default=None, bounds=(1, None), doc="""
        Maximum number of options to display at once.""")

    search_option_limit = param.Integer(default=None, bounds=(1, None), doc="""
        Maximum number of options to display at once if search string is entered.""")

    placeholder = param.String(default='', doc="""
        String displayed when no selection has been made.""")

    solid = param.Boolean(default=True, doc="""
        Whether to display widget with solid or light style.""")

    _widget_type = _BkMultiChoice


_AutocompleteInput_rename = {'name': 'title', 'options': 'completions'}


class AutocompleteInput(Widget):
    """
    The `MultiChoice` widget allows selecting multiple values from a list of
    `options`.

    It falls into the broad category of multi-value, option-selection widgets
    that provide a compatible API and include the `MultiSelect`,
    `CrossSelector`, `CheckBoxGroup` and `CheckButtonGroup` widgets.

    The `MultiChoice` widget provides a much more compact UI than
    `MultiSelect`.

    Reference: https://panel.holoviz.org/reference/widgets/AutocompleteInput.html

    :Example:

    >>> AutocompleteInput(
    ...     name='Study', options=['Biology', 'Chemistry', 'Physics'],
    ...     placeholder='Write your study here ...'
    ... )
    """

    case_sensitive = param.Boolean(default=True, doc="""
        Enable or disable case sensitivity.""")

    min_characters = param.Integer(default=2, doc="""
        The number of characters a user must type before
        completions are presented.""")

    options = param.List(default=[], doc="""
        A list of completion strings. This will be used to guide the
        user upon typing the beginning of a desired value.""")

    placeholder = param.String(default='', doc="""
        Placeholder for empty input field.""")

    restrict = param.Boolean(default=True, doc="""
        Set to False in order to allow users to enter text that is not
        present in the list of completion strings.""")

    value = param.String(default='', allow_None=True, doc="""
      Initial or entered text value updated when <enter> key is pressed.""")

    value_input = param.String(default='', allow_None=True, doc="""
      Initial or entered text value updated on every key press.""")

    _widget_type = _BkAutocompleteInput

    _rename = _AutocompleteInput_rename

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        if 'completions' in msg:
            if self.restrict and not isIn(self.value, msg['completions']):
                msg['value'] = self.value = ''
        return msg


class _RadioGroupBase(SingleSelectBase):

    _supports_embed = False

    _rename = {'name': None, 'options': 'labels', 'value': 'active'}

    _source_transforms = {'value': "source.labels[value]"}

    _target_transforms = {'value': "target.labels.indexOf(value)"}

    __abstract = True

    def _process_param_change(self, msg):
        msg = super(SingleSelectBase, self)._process_param_change(msg)
        values = self.values
        if 'active' in msg:
            value = msg['active']
            if value in values:
                msg['active'] = indexOf(value, values)
            else:
                if self.value is not None:
                    self.value = None
                msg['active'] = None

        if 'labels' in msg:
            msg['labels'] = self.labels
            value = self.value
            if not isIn(value, values):
                self.value = None
        return msg

    def _process_property_change(self, msg):
        msg = super(SingleSelectBase, self)._process_property_change(msg)
        if 'value' in msg:
            index = msg['value']
            if index is None:
                msg['value'] = None
            else:
                msg['value'] = list(self.values)[index]
        return msg

    def _get_embed_state(self, root, values=None, max_opts=3):
        if values is None:
            values = self.values
        elif any(v not in self.values for v in values):
            raise ValueError("Supplied embed states were not found in "
                             "the %s widgets values list." %
                             type(self).__name__)
        return (self, self._models[root.ref['id']][0], values,
                lambda x: x.active, 'active', 'cb_obj.active')



class RadioButtonGroup(_RadioGroupBase, _ButtonBase):
    """
    The `RadioButtonGroup` widget allows selecting from a list or dictionary
    of values using a set of toggle buttons.

    It falls into the broad category of single-value, option-selection widgets
    that provide a compatible API and include the `RadioBoxGroup`, `Select`,
    and `DiscreteSlider` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/RadioButtonGroup.html

    :Example:

    >>> RadioButtonGroup(
    ...     name='Plotting library', options=['Matplotlib', 'Bokeh', 'Plotly'],
    ...     button_type='success'
    ... )
    """

    orientation = param.Selector(default='horizontal',
        objects=['horizontal', 'vertical'], doc="""
        Button group orientation, either 'horizontal' (default) or 'vertical'.""")

    _widget_type = _BkRadioButtonGroup

    _supports_embed = True



class RadioBoxGroup(_RadioGroupBase):
    """
    The `RadioBoxGroup` widget allows selecting from a list or dictionary of
    values using a set of checkboxes.

    It falls into the broad category of single-value, option-selection widgets
    that provide a compatible API and include the `RadioButtonGroup`, `Select`
    and `DiscreteSlider` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/RadioBoxGroup.html

    :Example:

    >>> RadioBoxGroup(
    ...     name='Sponsor', options=['Anaconda', 'Blackstone'], inline=True
    ... )
    """

    inline = param.Boolean(default=False, doc="""
        Whether the items be arrange vertically (``False``) or
        horizontally in-line (``True``).""")

    _supports_embed = True

    _widget_type = _BkRadioBoxGroup



class _CheckGroupBase(SingleSelectBase):

    value = param.List(default=[])

    _rename = {'name': None, 'options': 'labels', 'value': 'active'}

    _source_transforms = {'value': "value.map((index) => source.labels[index])"}

    _target_transforms = {'value': "value.map((label) => target.labels.indexOf(label))"}

    _supports_embed = False

    __abstract = True

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        values = self.values
        if 'active' in msg:
            msg['active'] = [indexOf(v, values) for v in msg['active']
                             if isIn(v, values)]
        if 'labels' in msg:
            msg['labels'] = self.labels
            if any(not isIn(v, values) for v in self.value):
                self.value = [v for v in self.value if isIn(v, values)]
            msg["active"] = [indexOf(v, values) for v in self.value
                             if isIn(v, values)]
        msg.pop('title', None)
        return msg

    def _process_property_change(self, msg):
        msg = super(SingleSelectBase, self)._process_property_change(msg)
        if 'value' in msg:
            values = self.values
            msg['value'] = [values[a] for a in msg['value']]
        return msg



class CheckButtonGroup(_CheckGroupBase, _ButtonBase):
    """
    The `CheckButtonGroup` widget allows selecting between a list of options
    by toggling the corresponding buttons.

    It falls into the broad category of multi-option selection widgets that
    provide a compatible API and include the `MultiSelect`, `CrossSelector`
    and `CheckBoxGroup` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/CheckButtonGroup.html

    :Example:

    >>> CheckButtonGroup(
    ...     name='Regression Models', value=['Lasso', 'Ridge'],
    ...     options=['Lasso', 'Linear', 'Ridge', 'Polynomial']
    ... )
    """

    orientation = param.Selector(default='horizontal',
        objects=['horizontal', 'vertical'], doc="""
        Button group orientation, either 'horizontal' (default) or 'vertical'.""")

    _widget_type = _BkCheckboxButtonGroup


class CheckBoxGroup(_CheckGroupBase):
    """
    The `CheckBoxGroup` widget allows selecting between a list of options by
    ticking the corresponding checkboxes.

    It falls into the broad category of multi-option selection widgets that
    provide a compatible API and include the `MultiSelect`, `CrossSelector`
    and `CheckButtonGroup` widgets.

    Reference: https://panel.holoviz.org/reference/widgets/CheckBoxGroup.html

    :Example:

    >>> CheckBoxGroup(
    ...     name='Fruits', value=['Apple', 'Pear'], options=['Apple', 'Banana', 'Pear', 'Strawberry'],
    ...     inline=True
    ... )
    """

    inline = param.Boolean(default=False, doc="""
        Whether the items be arrange vertically (``False``) or
        horizontally in-line (``True``).""")

    _widget_type = _BkCheckboxGroup



class ToggleGroup(SingleSelectBase):
    """This class is a factory of ToggleGroup widgets.

    A ToggleGroup is a group of widgets which can be switched 'on' or 'off'.

    Two types of widgets are available through the widget_type argument :
        * `'button'` (default)
        * `'box'`

    Two different behaviors are available through behavior argument:
        * 'check' (default) : boolean
           Any number of widgets can be selected. In this case value
           is a 'list' of objects.
        * 'radio' : boolean
           One and only one widget is switched on. In this case value
           is an 'object'.
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

    Reference: https://panel.holoviz.org/reference/widgets/CrossSelector.html

    :Example:

    >>> CrossSelector(
    ...     name='Fruits', value=['Apple', 'Pear'],
    ...     options=['Apple', 'Banana', 'Pear', 'Strawberry']
    ... )
    """

    width = param.Integer(default=600, allow_None=True, doc="""
        The number of options shown at once (note this is the
        only way to control the height of this widget)""")

    height = param.Integer(default=200, allow_None=True, doc="""
        The number of options shown at once (note this is the
        only way to control the height of this widget)""")

    filter_fn = param.Callable(default=re.search, doc="""
        The filter function applied when querying using the text
        fields, defaults to re.search. Function is two arguments, the
        query or pattern and the item label.""")

    size = param.Integer(default=10, doc="""
        The number of options shown at once (note this is the only way
        to control the height of this widget)""")

    definition_order = param.Integer(default=True, doc="""
       Whether to preserve definition order after filtering. Disable
       to allow the order of selection to define the order of the
       selected list.""")

    def __init__(self, **params):
        super().__init__(**params)
        # Compute selected and unselected values

        labels, values = self.labels, self.values
        selected = [labels[indexOf(v, values)] for v in params.get('value', [])
                    if isIn(v, values)]
        unselected = [k for k in labels if k not in selected]
        layout = dict(sizing_mode='stretch_both', background=self.background, margin=0)
        self._lists = {
            False: MultiSelect(options=unselected, size=self.size, **layout),
            True: MultiSelect(options=selected, size=self.size, **layout)
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
            False: TextInput(placeholder='Filter available options',
                             margin=(0, 0, 10, 0), width_policy='max'),
            True: TextInput(placeholder='Filter selected options',
                            margin=(0, 0, 10, 0), width_policy='max')
        }
        self._search[False].param.watch(self._filter_options, 'value')
        self._search[True].param.watch(self._filter_options, 'value')

        self._placeholder = TextAreaInput(
            placeholder=("To select an item highlight it on the left "
                         "and use the arrow button to move it to the right."),
            disabled=True, **layout
        )
        right = self._lists[True] if self.value else self._placeholder

        # Define Layout
        self._unselected = Column(self._search[False], self._lists[False], **layout)
        self._selected = Column(self._search[True], right, **layout)
        buttons = Column(self._buttons[True], self._buttons[False], margin=(0, 5))

        self._composite[:] = [
            self._unselected, Column(VSpacer(), buttons, VSpacer()), self._selected
        ]

        self._selections = {False: [], True: []}
        self._query = {False: '', True: ''}

        self._update_disabled()

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
        if len(self._lists[True].options) and self._selected[-1] is not self._lists[True]:
            self._selected[-1] = self._lists[True]
        elif not len(self._lists[True].options) and self._selected[-1] is not self._placeholder:
            self._selected[-1] = self._placeholder

    @param.depends('options', watch=True)
    def _update_options(self):
        """
        Updates the options of each of the sublists after the options
        for the whole widget are updated.
        """
        self._selections[False] = []
        self._selections[True] = []
        self._update_value()

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
        if self.definition_order:
            options = [k for k in labels if k not in other]
        else:
            options = self._lists[selected].values
        if not query:
            self._lists[selected].options = options
            self._lists[selected].value = []
        else:
            try:
                matches = [o for o in options if self.filter_fn(query, o)]
            except Exception:
                matches = []
            self._lists[selected].options = options if options else []
            self._lists[selected].value = [m for m in matches]

    def _update_selection(self, event):
        """
        Updates the current selection in each list.
        """
        selected = event.obj is self._lists[True]
        self._selections[selected] = [v for v in event.new if v != '']

    def _apply_selection(self, event):
        """
        Applies the current selection depending on which button was
        pressed.
        """
        selected = event.obj is self._buttons[True]

        new = OrderedDict([(k, self._items[k]) for k in self._selections[not selected]])
        old = self._lists[selected].options
        other = self._lists[not selected].options

        merged = OrderedDict([(k, k) for k in list(old)+list(new)])
        leftovers = OrderedDict([(k, k) for k in other if k not in new])
        self._lists[selected].options = merged if merged else {}
        self._lists[not selected].options = leftovers if leftovers else {}
        if len(self._lists[True].options):
            self._selected[-1] = self._lists[True]
        else:
            self._selected[-1] = self._placeholder
        self.value = [self._items[o] for o in self._lists[True].options if o != '']
        self._apply_filters()

    def _get_model(self, doc, root=None, parent=None, comm=None):
        return self._composite._get_model(doc, root, parent, comm)
