"""
Miscellaneous widgets which do not fit into the other main categories.
"""
from __future__ import absolute_import, division, unicode_literals

import os

from base64 import b64encode

import param

from ..models import Audio as _BkAudio
from .base import Widget



class Audio(Widget):

    loop = param.Boolean(default=False, doc="""
        Whether the audio should loop""")

    time = param.Number(default=0, doc="""
        The current timestamp""")

    throttle = param.Integer(default=250, doc="""
        How frequently to sample the current playback time in milliseconds""")

    paused = param.Boolean(default=True, doc="""
        Whether the audio is currently paused""")

    value = param.String(default='', doc="""
        The audio file either local or remote.""")

    volume = param.Number(default=None, bounds=(0, 100), doc="""
        The volume of the audio player.""")

    _widget_type = _BkAudio

    _rename = {'name': None}

    def _process_param_change(self, msg):
        msg = super(Audio, self)._process_param_change(msg)
        if 'value' in msg and os.path.isfile(msg['value']):
            fmt = msg['value'].split('.')[-1]
            with open(msg['value'], 'rb') as f:
                data = f.read()
            template = 'data:audio/{mime};base64,{data}'
            data = b64encode(data)
            msg['value'] = template.format(data=data.decode('utf-8'),
                                           mime=fmt)
        return msg

