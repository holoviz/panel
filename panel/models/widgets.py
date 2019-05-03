"""
Custom bokeh Widget models.
"""
from __future__ import absolute_import, division, unicode_literals

import os

from bokeh.core.properties import Int, Float, Override, Enum, Any, Bool
from bokeh.models import Widget

from ..compiler import CUSTOM_MODELS


class Player(Widget):
    """
    The Player widget provides controls to play through a number of frames.
    """

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'player.ts')

    start = Int(help="Lower bound of the Player slider")

    end = Int(help="Upper bound of the Player slider")

    value = Int(0, help="Current value of the player app")

    step = Int(1, help="Number of steps to advance the player by.")

    interval = Int(500, help="Interval between updates")

    direction = Int(0, help="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    loop_policy = Enum('once', 'reflect', 'loop', default='once')

    width = Override(default=400)

    height = Override(default=250)


class FileInput(Widget):

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fileinput.ts')

    value = Any(help="Encoded file data")


class Audio(Widget):

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'audio.ts')

    loop = Bool(False, help="""Whether the audio should loop""")

    paused = Bool(False, help="""Whether the audio is paused""")

    time = Float(0, help="""
        The current time stamp of the audio playback""")

    throttle = Int(250, help="""
        The frequency at which the time value is updated in milliseconds.""")

    value = Any(help="Encoded file data")

    volume = Int(0, help="""The volume of the audio player.""")


class VideoStream(Widget):

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'videostream.ts')

    format = Enum('png', 'jpeg', default='png')

    paused = Bool(False, help="""Whether the video is paused""")

    snapshot = Bool(False, help="""On change generate a snapshot of the current video frame""")

    timeout = Float(None, help="""
        The timeout between snapshots (if None snapshot only generated
        when snapshot property is changed""")

    value = Any(help="""Snapshot Data""")

    height = Override(default=240)

    width = Override(default=320)



CUSTOM_MODELS['panel.models.widgets.Player'] = Player
CUSTOM_MODELS['panel.models.widgets.FileInput'] = FileInput
CUSTOM_MODELS['panel.models.widgets.Audio'] = Audio
CUSTOM_MODELS['panel.models.widgets.VideoStream'] = VideoStream
