"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import annotations

import itertools
import re
import sys

from collections.abc import Awaitable, Callable, Mapping
from functools import partial
from types import FunctionType
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
import param

from bokeh.models import PaletteSelect
from bokeh.models.widgets import (
    AutocompleteInput as _BkAutocompleteInput,
    CheckboxGroup as _BkCheckboxGroup, MultiChoice as _BkMultiChoice,
    RadioGroup as _BkRadioBoxGroup,
)

from ..io.resources import CDN_DIST
from ..io.state import state
from ..layout.base import Column, ListPanel, NamedListPanel
from ..models import (
    CheckboxButtonGroup as _BkCheckboxButtonGroup,
    CustomMultiSelect as _BkMultiSelect, CustomSelect,
    RadioButtonGroup as _BkRadioButtonGroup, SingleSelect as _BkSingleSelect,
)
from ..util import (
    PARAM_NAME_PATTERN, indexOf, isIn, unique_iterator,
)
from ._mixin import TooltipMixin
from .base import CompositeWidget, Widget
from .button import Button, _ButtonBase
from .input import TextAreaInput, TextInput

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..models.widgets import DoubleClickEvent


class SelectBase(Widget):

    options = param.ClassSelector(default=[], class_=(dict, list))

    __abstract = True

    @property
    def labels(self):
        labels = []
        for o in self.options:
            if isinstance(o, param.Parameterized) and not PARAM_NAME_PATTERN.match(o.name):
                labels.append(o.name)
            else:
                labels.append(str(o))
        return labels

    @property
    def values(self):
        if isinstance(self.options, dict):
            return list(self.options.values())
        else:
            return self.options

    @property
    def _items(self):
        return dict(zip(self.labels, self.values))


class SingleSelectBase(SelectBase):

    value = param.Parameter(default=None)

    _allows_values: ClassVar[bool] = True

    _allows_none: ClassVar[bool] = False

    _supports_embed: bool = True

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        values = self.values
        if self.value is None and None not in values and values and not self._allows_none:
            self.value = values[0]

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        labels, values = self.labels, self.values
        unique = len(set(self.unicode_values)) == len(labels) and self._allows_values
        if 'value' in msg:
            val = msg['value']
            if isIn(val, values):
                unicode_values = self.unicode_values if unique else labels
                msg['value'] = unicode_values[indexOf(val, values)]
            elif values:
                self.value = self.param['value'].default if self._allows_none else self.values[0]
                if not self._allows_none:
                    del msg['value']
            else:
                self.value = self.param['value'].default
                if self._allows_none:
                    msg['value'] = self.value

        option_prop = self._property_mapping.get('options', 'options')
        is_list = isinstance(self.param['value'], param.List)
        if option_prop in msg and not is_list:
            if isinstance(self.options, dict):
                if unique and self._allows_values:
                    options = [(v, l) for l,v in zip(labels, self.unicode_values)]
                else:
                    options = labels
                msg[option_prop] = options
            else:
                msg[option_prop] = self.unicode_values
            val = self.value
            if values:
                if not isIn(val, values):
                    self.value = self.param['value'].default if self._allows_none else values[0]
            else:
                self.value = self.param['value'].default
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
                             f"in the {type(self).__name__} widgets values list.")
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

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    disabled_options = param.List(default=[], nested_refs=True, doc="""
        Optional list of ``options`` that are disabled, i.e. unusable and
        un-clickable. If ``options`` is a dictionary the list items must be
        dictionary values.""")

    groups = param.Dict(default=None, nested_refs=True, doc="""
        Dictionary whose keys are used to visually group the options
        and whose values are either a list or a dictionary of options
        to select from. Mutually exclusive with ``options``  and valid only
        if ``size`` is 1.""")

    size = param.Integer(default=1, bounds=(1, None), doc="""
        Declares how many options are displayed at the same time.
        If set to 1 displays options as dropdown otherwise displays
        scrollable area.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'groups': None,
    }

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'size': None, 'groups': None
    }

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/select.css']

    @property
    def _widget_type(self):
        return CustomSelect if self.size == 1 else _BkSingleSelect

    def __init__(self, **params):
        super().__init__(**params)
        if self.size == 1:
            self.param.size.constant = True
        self._internal_callbacks.extend([
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

    def _process_param_change(self, msg: dict[str, Any]) -> dict[str, Any]:
        groups_provided = 'groups' in msg
        msg = super()._process_param_change(msg)
        if groups_provided or 'options' in msg and self.groups:
            groups: dict[str, list[str | tuple[str, str]]] = self.groups
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
                            group: [str(v) for v in self.groups[group]]  # type: ignore
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


class NestedSelect(CompositeWidget):
    """
    The `NestedSelect` widget is composed of multiple widgets, where subsequent select options
    depend on the parent's value.

    Reference: https://panel.holoviz.org/reference/widgets/NestedSelect.html

    :Example:

    >>> NestedSelect(
    ...     options={
    ...         "gfs": {"tmp": [1000, 500], "pcp": [1000]},
    ...         "name": {"tmp": [1000, 925, 850, 700, 500], "pcp": [1000]},
    ...     },
    ...     levels=["model", "var", "level"],
    ... )
    """

    disabled = param.Boolean(default=False, doc="""
        Whether the widget is disabled.""")

    layout = param.Parameter(default=Column, doc="""
        The layout type of the widgets. If a dictionary, a "type" key can be provided,
        to specify the layout type of the widgets, and any additional keyword arguments
        will be used to instantiate the layout.""")

    levels = param.List(doc="""
        Either a list of strings or a list of dictionaries. If a list of strings, the strings
        are used as the names of the levels. If a list of dictionaries, each dictionary may
        have a "name" key, which is used as the name of the level, a "type" key, which
        is used as the type of widget, and any corresponding widget keyword arguments.
        Must be specified if options is callable.""")

    options = param.ClassSelector(class_=(list, dict, FunctionType), doc="""
        The options to select from. The options may be nested dictionaries, lists,
        or callables that return those types. If callables are used, the callables
        must accept `level` and `value` keyword arguments, where `level` is the
        level that updated and `value` is a dictionary of the current values, containing keys
        up to the level that was updated.""")

    value = param.Dict(doc="""
        The value from all the Select widgets; the keys are the levels names.
        If no levels names are specified, the keys are the levels indices.""")

    _widgets = param.List(doc="The nested select widgets.")

    _max_depth = param.Integer(doc="The number of levels of the nested select widgets.")

    _levels = param.List(doc="""
        The internal rep of levels to prevent overwriting user provided levels.""")

    @classmethod
    def _infer_params(cls, values, **params):
        if 'pandas' in sys.modules and isinstance(values, sys.modules['pandas'].MultiIndex):
            params['options'] = options = {}
            params['levels'] = levels = list(values.names)
            depth = len(values.names)
            value = {}
            for vals in values.to_list():
                current = options
                for i, (l, v) in enumerate(zip(levels, vals)):
                    if 'value' not in params:
                        value[l] = v
                    if i == (depth-1):
                        if v not in current:
                            current.append(v)
                        continue
                    elif v not in current:
                        container = [] if i == (depth-2) else {}
                        current[v] = container
                    current = current[v]
                if 'value' not in params:
                    params['value'] = value
        else:
            params['options'] = options = list(unique_iterator(values))
            if hasattr(values, 'name'):
                params['levels'] = [values.name]
                params['value'] = {values.name: options[0]}
            else:
                params['levels'] = []
                params['value'] = {0: options[0]}
        return super()._infer_params(values, **params)

    def __init__(self, **params):
        super().__init__(**params)
        self._update_widgets()

    def _gather_values_from_widgets(self, up_to_i=None):
        """
        Gather values from all the select widgets to update the class' value.
        """
        values = {}
        for i, select in enumerate(self._widgets):
            if up_to_i is not None and i >= up_to_i:
                break
            level = self._levels[i]
            if isinstance(level, dict):
                name = level.get("name", i)
            else:
                name = level
            values[name] = select.value if select.options else None

        return values

    def _uses_callable(self, d):
        """
        Check if the nested options has a callable.
        """
        if callable(d):
            return True

        if isinstance(d, dict):
            for value in d.values():
                if callable(value):
                    return True
                elif isinstance(value, dict):
                    return self._uses_callable(value)
        return False

    def _find_max_depth(self, d, depth=1):
        if isinstance(d, list) or d is None:
            return depth-1
        max_depth = depth
        for value in d.values():
            max_depth = max(max_depth, self._find_max_depth(value, depth + 1))
        return max_depth

    def _resolve_callable_options(self, i, options) -> dict | list:
        level = self.levels[i]
        value = self._gather_values_from_widgets(up_to_i=i)
        options = options(level=level, value=value)
        return options

    @param.depends("options", "layout", "levels", watch=True)
    def _update_widgets(self):
        """
        When options is changed, reflect changes on the select widgets.
        """
        if self._uses_callable(self.options):
            if not self.levels:
                raise ValueError("levels must be specified if options is callable")
            self._max_depth = len(self.levels)
        elif isinstance(self.options, list):
            self._max_depth = 1
        else:
            self._max_depth = self._find_max_depth(self.options) + 1

        if not self.levels:
            self._levels = [i for i in range(self._max_depth)]
        elif len(self.levels) != self._max_depth:
            raise ValueError(f"levels must be of length {self._max_depth}")
        else:
            self._levels = self.levels

        self._widgets = []

        # use [] as default because it's the last level if options is None
        options = (self.options or [])
        if isinstance(self.options, dict):
            options = self.options.copy()

        for i in range(self._max_depth):
            if callable(options):
                options = self._resolve_callable_options(i, options)

            value = self._init_widget(i, options)
            if isinstance(options, dict) and len(options) > 0 and value is not None:
                options = options[value]
            elif i < self._max_depth - 1 and not isinstance(options, dict):
                raise ValueError(
                    f"The level, {self.levels[i]!r} is not the last nested level, "
                    f"so it must be a dict, but got {options!r}, which is a "
                    f"{type(options).__name__}"
                )

        if isinstance(self.layout, dict):
            layout_type = self.layout.pop("type", Column)
            layout_kwargs = self.layout.copy()
        elif issubclass(self.layout, (ListPanel, NamedListPanel)):
            layout_type = self.layout
            layout_kwargs = {}
        else:
            raise ValueError(
                f"The layout must be a subclass of ListLike or dict, got {self.layout!r}."
            )

        self._composite[:] = [layout_type(*self._widgets, **layout_kwargs)]
        if self.options is not None:
            self.value = self._gather_values_from_widgets()

    def _extract_level_metadata(self, i):
        """
        Extract the widget type and keyword arguments from the level metadata.
        """
        level = self._levels[i]
        if isinstance(level, int):
            return Select, {}
        elif isinstance(level, str):
            return Select, {"name": level}
        widget_type = level.get("type", Select)
        widget_kwargs = {k: v for k, v in level.items() if k != "type"}
        return widget_type, widget_kwargs

    def _lookup_value(self, i, options, values, name=None, error=False):
        """
        Look up the value of the select widget at index i or by name.
        """
        options_iterable = isinstance(options, (list, dict))
        if values is None or (options_iterable and len(options) == 0):
            value = None
        elif name is None:
            # get by index
            value = list(values.values())[i] if i < len(values) else None
        elif isinstance(self._levels[0], int):
            # get by levels keys, which are enumerations
            value = values.get(i)
        else:
            # get by levels keys, which are strings
            value = values.get(name)

        if options_iterable and options and value not in options:
            if value is not None and error:
                raise ValueError(
                    f"Failed to set value {value!r} for level {name!r}, "
                    f"must be one of {options!r}."
                )
            else:
                value = options[0]
        return value

    def _init_widget(self, i, options):
        """
        Helper method to initialize a select widget.
        """
        if isinstance(options, dict):
            options = list(options.keys())
        elif not isinstance(options, (list, dict)) and not callable(options):
            raise ValueError(
                f"options must be a dict, list, or callable that returns those types, "
                f"got {options!r}, which is a {type(options).__name__}"
            )

        widget_type, widget_kwargs = self._extract_level_metadata(i)
        value = self._lookup_value(i, options, self.value, error=False)
        widget_kwargs["options"] = options
        widget_kwargs["value"] = value
        widget_kwargs["disabled"] = self.param.disabled
        if "visible" not in widget_kwargs:
            # first select widget always visible
            widget_kwargs["visible"] = i == 0 or callable(options) or len(options) > 0
        widget = widget_type(**widget_kwargs)
        self.link(widget, disabled="disabled")
        widget.param.watch(self._update_widget_options_interactively, "value")
        self._widgets.append(widget)
        return value

    def _update_widget_options_interactively(self, event):
        """
        When a select widget's value is changed, update to the latest options.
        """
        if self.options is None:
            return

        # little optimization to avoid looping through all the
        # widgets and updating their value
        for start_i, select in enumerate(self._widgets):  # noqa: B007
            if select is event.obj:
                break

        options = self.options if callable(self.options) else self.options.copy()

        # batch watch to prevent continuously triggering
        # this function when updating the select widgets
        with param.parameterized.batch_call_watchers(self):
            for i, select in enumerate(self._widgets[:-1]):
                if select.value is None:
                    options = {}
                    visible = False
                elif options:
                    if isinstance(options, dict):
                        if select.value in options:
                            options = options[select.value]
                        else:
                            options = options[list(options.keys())[0]]
                    visible = bool(options)

                if i < start_i:
                    # If the select widget is before the one
                    # that triggered the event,
                    # then we don't need to update it;
                    # we just need to subset options.
                    continue

                next_select = self._widgets[i + 1]
                if callable(options):
                    options = self._resolve_callable_options(i + 1, options)
                    next_options = list(options)
                elif isinstance(options, dict):
                    next_options = list(options.keys())
                elif isinstance(options, list):
                    next_options = options
                else:
                    raise NotImplementedError(
                        "options must be a dict, list, or callable that returns those types."
                    )

                next_select.param.update(
                    options=next_options,
                    visible=visible
                )
            self.value = self._gather_values_from_widgets()

    @param.depends("value", watch=True)
    def _update_options_programmatically(self):
        """
        When value is passed, update to the latest options.
        """
        if self.options is None:
            return

        # must define these or else it gets mutated in the loop
        options = self.options if callable(self.options) else self.options.copy()
        set_values = self.value.copy()
        original_values = self._gather_values_from_widgets()

        if set_values == original_values:
            return

        with param.parameterized.batch_call_watchers(self):
            try:
                for i in range(self._max_depth):
                    curr_select = self._widgets[i]
                    if callable(options):
                        options = self._resolve_callable_options(i, options)
                        curr_options = list(options)
                    elif isinstance(options, dict):
                        curr_options = list(options.keys())
                    else:
                        curr_options = options
                    curr_value = self._lookup_value(
                        i, curr_options, set_values,
                        name=curr_select.name, error=True
                    )

                    with param.discard_events(self):
                        curr_select.param.update(
                            options=curr_options,
                            value=curr_value,
                            visible=callable(curr_options) or len(curr_options) > 0
                        )
                    if curr_value is None:
                        break
                    if i < self._max_depth - 1:
                        options = options[curr_value]
            except Exception:
                # revert to original values if there is an error
                # so it's not in a limbo state
                self.value = original_values
                raise


class ColorMap(SingleSelectBase):
    """
    The `ColorMap` widget allows selecting a value from a dictionary of
    `options` each containing a colormap specified as a list of colors
    or a matplotlib colormap.

    Reference: https://panel.holoviz.org/reference/widgets/ColorMap.html

    :Example:

    >>> ColorMap(name='Reds', options={'Reds': ['white', 'red'], 'Blues': ['#ffffff', '#0000ff']})
    """

    options = param.Dict(default={}, doc="""
        Dictionary of colormaps""")

    ncols = param.Integer(default=1, doc="""
        Number of columns of swatches to display.""")

    swatch_height = param.Integer(default=20, doc="""
        Height of the color swatches.""")

    swatch_width = param.Integer(default=100, doc="""
        Width of the color swatches.""")

    value = param.Parameter(default=None, doc="The selected colormap.")

    value_name = param.String(default=None, doc="Name of the selected colormap.")

    _rename = {'options': 'items', 'value_name': None}

    _widget_type: ClassVar[type[Model]] = PaletteSelect

    @param.depends('value_name', watch=True, on_init=True)
    def _sync_value_name(self):
        if self.value_name and self.value_name in self.options:
            self.value = self.options[self.value_name]

    @param.depends('value', watch=True, on_init=True)
    def _sync_value(self):
        if self.value:
            idx = indexOf(self.value, self.values)
            self.value_name = self.labels[idx]

    def _process_param_change(self, params):
        if 'options' in params:
            options = []
            for name, cmap in params.pop('options').items():
                if 'matplotlib' in getattr(cmap, '__module__', ''):
                    N = getattr(cmap, 'N', 10)
                    samples = np.linspace(0, 1, N)
                    rgba_tmpl = 'rgba({0}, {1}, {2}, {3:.3g})'
                    cmap = [
                        rgba_tmpl.format(*(rgba[:3]*255).astype(int), rgba[-1])
                        for rgba in cmap(samples)
                    ]
                options.append((name, cmap))
            params['options'] = options
        if 'value' in params and not isinstance(params['value'], (str, type(None))):
            idx = indexOf(params['value'], self.values)
            params['value'] = self.labels[idx]
        return {
            self._property_mapping.get(p, p): v for p, v in params.items()
            if self._property_mapping.get(p, False) is not None
        }


class _MultiSelectBase(SingleSelectBase):

    value = param.List(default=[])

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _supports_embed: bool = False

    __abstract = True

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

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/select.css']

    _widget_type: ClassVar[type[Model]] = _BkMultiSelect

    def __init__(self, **params):
        click_handler = params.pop('on_double_click', None)
        super().__init__(**params)
        self._dbl__click_handlers = [click_handler] if click_handler else []

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('dblclick_event', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event: DoubleClickEvent) -> None:
        if event.option in self.labels:
            event.option = self._items[event.option]
            for handler in self._dbl__click_handlers:
                state.execute(partial(handler, event))

    def on_double_click(
        self, callback: Callable[[param.parameterized.Event], None | Awaitable[None]]
    ) -> param.parameterized.Watcher:
        """
        Register a callback to be executed when a `MultiSelect` option is double-clicked.

        The callback is given an `DoubleClickEvent` argument

        Example
        -------

        >>> select = pn.widgets.MultiSelect(options=["A", "B", "C"])
        >>> def handle_click(event):
        ...    print(f"Option {event.option} was double clicked.")
        >>> select.on_double_click(handle_click)

        Parameters
        ----------
        callback:
            The function to run on click events. Must accept a positional `Event` argument. Can
            be a sync or async function
        """
        self._dbl__click_handlers.append(callback)



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

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _widget_type: ClassVar[type[Model]] = _BkMultiChoice


class AutocompleteInput(SingleSelectBase):
    """
    The `AutocompleteInput` widget allows selecting multiple values from a list of
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

    placeholder = param.String(default='', doc="""
        Placeholder for empty input field.""")

    restrict = param.Boolean(default=True, doc="""
        Set to False in order to allow users to enter text that is not
        present in the list of completion strings.""")

    search_strategy = param.Selector(default='starts_with',
        objects=['starts_with', 'includes'], doc="""
        Define how to search the list of completion strings. The default option
        `"starts_with"` means that the user's text must match the start of a
        completion string. Using `"includes"` means that the user's text can
        match any substring of a completion string.""")

    value = param.Parameter(default='', allow_None=True, doc="""
      Initial or entered text value updated when <enter> key is pressed.""")

    value_input = param.String(default='', allow_None=True, doc="""
      Initial or entered text value updated on every key press.""")

    width = param.Integer(default=300, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    description = param.String(default=None, doc="""
        An HTML string describing the function of this component.""")

    _allows_values: ClassVar[bool] = False

    _allows_none: ClassVar[bool] = True

    _rename: ClassVar[Mapping[str, str | None]] = {'name': 'title', 'options': 'completions'}

    _widget_type: ClassVar[type[Model]] = _BkAutocompleteInput

    def _process_property_change(self, msg):
        if not self.restrict and 'value' in msg:
            try:
                return super()._process_property_change(msg)
            except Exception:
                return Widget._process_property_change(self, msg)
        return super()._process_property_change(msg)

    def _process_param_change(self, msg):
        if 'value' in msg and not self.restrict and not isIn(msg['value'], self.values):
            with param.parameterized.discard_events(self):
                props = super()._process_param_change(msg)
                self.value = props['value'] = msg['value']
        else:
            props = super()._process_param_change(msg)
        return props


class _RadioGroupBase(SingleSelectBase):

    _supports_embed = False

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': None, 'options': 'labels', 'value': 'active'
    }

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
                             f"the {type(self).__name__} widgets values list.")
        return (self, self._models[root.ref['id']][0], values,
                lambda x: x.active, 'active', 'cb_obj.active')



class RadioButtonGroup(_RadioGroupBase, _ButtonBase, TooltipMixin):
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

    _rename: ClassVar[Mapping[str, str | None]] = {**_RadioGroupBase._rename, **TooltipMixin._rename}

    _source_transforms = {
        'value': "source.labels[value]", 'button_style': None, 'description': None
    }

    _supports_embed: bool = True

    _widget_type: ClassVar[type[Model]] = _BkRadioButtonGroup



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

    _supports_embed: bool = True

    _widget_type: ClassVar[type[Model]] = _BkRadioBoxGroup



class _CheckGroupBase(SingleSelectBase):

    value = param.List(default=[])

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None, 'options': 'labels', 'value': 'active'}

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



class CheckButtonGroup(_CheckGroupBase, _ButtonBase, TooltipMixin):
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

    _rename: ClassVar[Mapping[str, str | None]] = {**_CheckGroupBase._rename, **TooltipMixin._rename}

    _source_transforms = {
        'value': "value.map((index) => source.labels[index])", 'button_style': None,
        'description': None
    }

    _widget_type: ClassVar[type[Model]] = _BkCheckboxButtonGroup


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

    _widget_type: ClassVar[type[Model]] = _BkCheckboxGroup



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
            raise ValueError(f'widget_type {widget_type} is not valid. Valid options are {ToggleGroup._widgets_type}')
        if behavior not in ToggleGroup._behaviors:
            raise ValueError(f'behavior {widget_type} is not valid. Valid options are {ToggleGroup._behaviors}')

        if behavior == 'check':
            if widget_type == 'button':
                return CheckButtonGroup(**params)
            else:
                return CheckBoxGroup(**params)
        else:
            if isinstance(params.get('value'), list):
                raise ValueError('Radio buttons require a single value, '
                                 'found: {}'.format(params['value']))
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
        selected = [
            labels[indexOf(v, values)] for v in params.get('value', [])
            if isIn(v, values)
        ]
        unselected = [k for k in labels if k not in selected]
        layout = dict(
            sizing_mode='stretch_both', margin=0
        )
        self._lists = {
            False: MultiSelect(options=unselected, size=self.size, **layout),
            True: MultiSelect(options=selected, size=self.size, **layout)
        }
        self._lists[False].param.watch(self._update_selection, 'value')
        self._lists[True].param.watch(self._update_selection, 'value')

        # Define buttons
        self._buttons = {
            False: Button(name='\u276e\u276e', width=50, sizing_mode=None),
            True: Button(name='\u276f\u276f', width=50, sizing_mode=None)
        }

        self._buttons[False].param.watch(self._apply_selection, 'clicks')
        self._buttons[True].param.watch(self._apply_selection, 'clicks')

        # Define search
        self._search = {
            False: TextInput(
                placeholder='Filter available options',
                margin=(0, 0, 10, 0), sizing_mode='stretch_width'
            ),
            True: TextInput(
                placeholder='Filter selected options',
                margin=(0, 0, 10, 0), sizing_mode='stretch_width'
            )
        }
        self._search[False].param.watch(self._filter_options, 'value_input')
        self._search[True].param.watch(self._filter_options, 'value_input')

        self._placeholder = TextAreaInput(
            placeholder=("To select an item highlight it on the left "
                         "and use the arrow button to move it to the right."),
            disabled=True, **layout
        )
        right = self._lists[True] if self.value else self._placeholder

        # Define Layout
        self._unselected = Column(self._search[False], self._lists[False], **layout)
        self._selected = Column(self._search[True], right, **layout)
        buttons = Column(
            self._buttons[True], self._buttons[False],
            margin=(0, 5), align='center', sizing_mode=None
        )

        self._composite[:] = [
            self._unselected, buttons, self._selected
        ]

        self._selections = {False: [], True: []}
        self._query = {False: '', True: ''}

        self._update_disabled()
        self._update_width()

    @param.depends('width', watch=True)
    def _update_width(self):
        width = int(self.width // 2. - 50)
        self._search[False].width = width
        self._search[True].width = width
        self._lists[False].width = width
        self._lists[True].width = width

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

        new = {k: self._items[k] for k in self._selections[not selected]}
        old = self._lists[selected].options
        other = self._lists[not selected].options

        merged = {k: k for k in list(old)+list(new)}
        leftovers = {k: k for k in other if k not in new}
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
