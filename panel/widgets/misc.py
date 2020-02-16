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

from ..depends import depends
from ..io.notebook import push
from ..io.state import state
from ..models import (
    Audio as _BkAudio, VideoStream as _BkVideoStream, Progress as _BkProgress
)
from .base import Widget


class _MediaBase(Widget):

    loop = param.Boolean(default=False, doc="""
        Whether the meida should loop""")

    time = param.Number(default=0, doc="""
        The current timestamp""")

    throttle = param.Integer(default=250, doc="""
        How frequently to sample the current playback time in milliseconds""")

    paused = param.Boolean(default=True, doc="""
        Whether the media is currently paused""")

    value = param.String(default='', doc="""
        The media file either local or remote.""")

    volume = param.Number(default=None, bounds=(0, 100), doc="""
        The volume of the media player.""")

    _rename = {'name': None, 'sample_rate': None}

    _default_mime = None

    _media_type = None

    def __init__(self, **params):
        self.param.warning('%s widget is deprecated, use the equivalent '
                           'Pane type instead.' % type(self).__name__)
        super(_MediaBase, self).__init__(**params)

    def _from_numpy(self, data):
        from scipy.io import wavfile
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer

    def _process_param_change(self, msg):
        msg = super(_MediaBase, self)._process_param_change(msg)

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
            elif value.lower().startswith('http'):
                return msg
            elif not value:
                data, fmt = b'', self._default_mime
            else:
                raise ValueError('Value should be either path to a sound file or numpy array')
            template = 'data:audio/{mime};base64,{data}'
            msg['value'] = template.format(data=data.decode('utf-8'),
                                           mime=fmt)
        return msg


class Audio(_MediaBase):

    sample_rate = param.Integer(default=44100, doc="""
        The sample_rate of the audio when given a NumPy array.""")

    value = param.ClassSelector(default='', class_=(string_types + (np.ndarray,)), doc="""
        The audio file either local or remote.""")

    _media_type = 'audio'

    _default_mime = 'wav'

    _widget_type = _BkAudio


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


class Progress(Widget):

    active = param.Boolean(default=True, doc="""
        If no value is set the active property toggles animation of the
        progress bar on and off.""")

    bar_color = param.ObjectSelector(default='success', objects=[
        'primary', 'secondary', 'success', 'info', 'danger', 'warning',
        'light', 'dark'])

    max = param.Integer(default=100, doc="The maximum value of the progress bar.")

    value = param.Integer(default=None, bounds=(0, 100), doc="""
        The current value of the progress bar. If set to None the progress
        bar will be indeterminate and animate depending on the active
        parameter.""")

    _rename = {'name': None}

    _widget_type = _BkProgress

    @depends('max', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (0, self.max)
