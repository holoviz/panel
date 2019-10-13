"""
Miscellaneous widgets which do not fit into the other main categories.
"""
from __future__ import absolute_import, division, unicode_literals

import os

from io import BytesIO
from base64 import b64encode
from six import string_types

import param
import numpy as np
from scipy.io import wavfile

from ..io.notebook import push
from ..io.state import state
from ..models import (Audio as _BkAudio,
                      VideoStream as _BkVideoStream)
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

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array.""")

    value = param.ClassSelector(default='', class_=(string_types + (np.ndarray,)), doc="""
        The audio file either local or remote.""")

    volume = param.Number(default=None, bounds=(0, 100), doc="""
        The volume of the audio player.""")

    _widget_type = _BkAudio

    _rename = {'name': None, 'sample_rate': None}

    def _from_numpy(self, data):
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_param_change(self, msg):
        msg = super(Audio, self)._process_param_change(msg)

        if 'value' in msg:
            value =  msg['value']
            if isinstance(value, np.ndarray):
                fmt = 'wav'
                buffer = self._from_numpy(value)
                data = b64encode(buffer.getvalue())
            elif os.path.isfile(value):
                fmt = value.split('.')[-1]
                with open(value, 'rb') as f:
                    data = f.read()
                data = b64encode(data)
            elif not value:
                data, fmt = b'', 'wav'
            else:
                raise ValueError('Value should be either path to a sound file or numpy array')
            template = 'data:audio/{mime};base64,{data}'
            msg['value'] = template.format(data=data.decode('utf-8'),
                                           mime=fmt)
        return msg

class VideoStream(Widget):

    format = param.ObjectSelector(default='png', objects=['png', 'jpeg'],
                                  doc="""
        The file format as which the video is returned.""")

    paused = param.Boolean(default=False, doc="""
        Whether the video is currently paused""")

    timeout = param.Number(default=None, doc="""
        Interval between snapshots in millisecons""")

    value = param.String(default='', doc="""
        A base64 representation of the video stream snapshot.""")

    _widget_type = _BkVideoStream

    _rename = {'name': None}

    def snapshot(self):
        """
        Triggers a snapshot of the current VideoStream state to sync
        the widget value.
        """
        for ref, (m, _) in self._models.items():
            m.snapshot = not m.snapshot
            (self, root, doc, comm) = state._views[ref]
            if comm and 'embedded' not in root.tags:
                push(doc, comm)
