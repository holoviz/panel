"""
Defines Player widgets which offer media-player like controls.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Type,
)

import param

from ..config import config
from ..models.widgets import Player as _BkPlayer
from ..util import indexOf, isIn
from .base import Widget
from .select import SelectBase

if TYPE_CHECKING:
    from bokeh.model import Model


class PlayerBase(Widget):

    direction = param.Integer(default=0, doc="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    interval = param.Integer(default=500, doc="""
        Interval between updates, in milliseconds. Default is 500, i.e.
        two updates per second.""")

    loop_policy = param.ObjectSelector(
        default='once', objects=['once', 'loop', 'reflect'], doc="""
        Policy used when player hits last frame""")

    show_loop_controls = param.Boolean(default=True, doc="""
        Whether the loop controls radio buttons are shown""")

    step = param.Integer(default=1, doc="""
        Number of frames to step forward and back by on each event.""")

    height = param.Integer(default=80)

    width = param.Integer(default=510, allow_None=True, doc="""
      Width of this component. If sizing_mode is set to stretch
      or scale mode this will merely be used as a suggestion.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None}

    _widget_type: ClassVar[Type[Model]] = _BkPlayer

    __abstract = True

    def __init__(self, **params):
        if 'value' in params and 'value_throttled' in self.param:
            params['value_throttled'] = params['value']
        super().__init__(**params)

    def play(self):
        self.direction = 1

    def pause(self):
        self.direction = 0

    def reverse(self):
        self.direction = -1



class Player(PlayerBase):
    """
    The `Player` provides controls to play and skip through a number of
    frames defined by explicit start and end values.  The speed at
    which the widget plays is defined by the `interval` (in milliseconds), but it is also
    possible to skip frames using the `step` parameter.

    Reference: https://panel.holoviz.org/reference/widgets/Player.html

    :Example:

    >>> Player(name='Player', start=0, end=100, value=32, loop_policy='loop')
    """

    start = param.Integer(default=0, doc="Lower bound on the slider value")

    end = param.Integer(default=10, doc="Upper bound on the slider value")

    value = param.Integer(default=0, doc="Current player value")

    value_throttled = param.Integer(default=0, constant=True, doc="""
        Current throttled player value.""")

    _supports_embed: ClassVar[bool] = True

    def __init__(self, **params):
        if 'length' in params:
            if 'start' in params or 'end' in params:
                raise ValueError('Supply either length or start and end to Player not both')
            params['start'] = 0
            params['end'] = params.pop('length')-1
        elif params.get('start', 0) > 0 and 'value' not in params:
            params['value'] = params['start']
        super().__init__(**params)

    def _process_property_change(self, msg):
        if config.throttled:
            if "value" in msg:
                del msg["value"]
            if "value_throttled" in msg:
                msg["value"] = msg["value_throttled"]
        return super()._process_property_change(msg)

    def _get_embed_state(self, root, values=None, max_opts=3):
        if values is None:
            values = list(range(self.start, self.end, self.step))
        return (self, self._models[root.ref['id']][0], values,
                lambda x: x.value, 'value', 'cb_obj.value')



class DiscretePlayer(PlayerBase, SelectBase):
    """
    The `DiscretePlayer` provides controls to iterate through a list of
    discrete options.  The speed at which the widget plays is defined
    by the `interval` (in milliseconds), but it is also possible to skip items using the
    `step` parameter.

    Reference: https://panel.holoviz.org/reference/widgets/DiscretePlayer.html

    :Example:

    >>> DiscretePlayer(
    ...     name='Discrete Player',
    ...     options=[2, 4, 8, 16, 32, 64, 128], value=32,
    ...     loop_policy='loop'
    ... )
    """

    interval = param.Integer(default=500, doc="Interval between updates")

    value = param.Parameter(doc="Current player value")

    value_throttled = param.Parameter(constant=True, doc="Current player value")

    _rename: ClassVar[Mapping[str, str | None]] = {'name': None, 'options': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'value': None, 'value_throttled': None}

    def _process_param_change(self, msg):
        values = self.values
        if 'options' in msg:
            msg['start'] = 0
            msg['end'] = len(values) - 1
            if values and not isIn(self.value, values):
                self.value = values[0]
        if 'value' in msg:
            value = msg['value']
            if isIn(value, values):
                msg['value'] = indexOf(value, values)
            elif values:
                self.value = values[0]
        if 'value_throttled' in msg:
            del msg['value_throttled']
        return super()._process_param_change(msg)

    def _process_property_change(self, msg):
        for prop in ('value', 'value_throttled'):
            if prop in msg:
                value = msg.pop(prop)
                if value < len(self.options):
                    msg[prop] = self.values[value]
        return msg
