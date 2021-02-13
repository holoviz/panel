"""
Defines Player widgets which offer media-player like controls.
"""
import param

from ..models.widgets import Player as _BkPlayer
from ..util import isIn, indexOf
from .base import Widget
from .select import SelectBase


class PlayerBase(Widget):

    interval = param.Integer(default=500, doc="Interval between updates")

    loop_policy = param.ObjectSelector(default='once',
                                       objects=['once', 'loop', 'reflect'], doc="""
        Policy used when player hits last frame""")

    step = param.Integer(default=1, doc="""
        Number of frames to step forward and back by on each event.""")

    show_loop_controls = param.Boolean(default=True, doc="""
        Whether the loop controls radio buttons are shown""")

    height = param.Integer(default=80)

    width = param.Integer(default=510)

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

    _supports_embed = True

    def __init__(self, **params):
        if 'length' in params:
            if 'start' in params or 'end' in params:
                raise ValueError('Supply either length or start and end to Player not both')
            params['start'] = 0
            params['end'] = params.pop('length')-1
        elif params.get('start', 0) > 0 and not 'value' in params:
            params['value'] = params['start']
        super().__init__(**params)

    def _get_embed_state(self, root, values=None, max_opts=3):
        if values is None:
            values = list(range(self.start, self.end, self.step))
        return (self, self._models[root.ref['id']][0], values,
                lambda x: x.value, 'value', 'cb_obj.value')



class DiscretePlayer(PlayerBase, SelectBase):
    """
    The DiscretePlayer provides controls to iterate through a list of
    discrete options.  The speed at which the widget plays is defined
    by the interval, but it is also possible to skip items using the
    step parameter.
    """

    interval = param.Integer(default=500, doc="Interval between updates")

    value = param.Parameter()

    _rename = {'name': None, 'options': None}

    _source_transforms = {'value': None}

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
        return super()._process_param_change(msg)

    def _process_property_change(self, msg):
        if 'value' in msg:
            value = msg.pop('value')
            if value < len(self.options):
                msg['value'] = self.values[value]
        return msg
