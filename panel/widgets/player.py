"""
Defines Player widgets which offer media-player like controls.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from ..models.widgets import Player as _BkPlayer
from .base import Widget


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
