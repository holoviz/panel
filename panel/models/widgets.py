import os

from bokeh.core.properties import Int, Override, Enum
from bokeh.models import Widget, WidgetBox

class Player(Widget):
    """
    The Player widget provides controls to play through a number of frames.
    """

    __implementation__ = os.path.join(os.path.dirname(__file__), 'player.ts')

    length = Int(help="The number of frames to play through")

    value = Int(0, help="Current value of the player app")

    interval = Int(500, help="Interval between updates")

    direction = Int(0, help="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    loop_policy = Enum('once', 'reflect', 'loop', default='once')

    height = Override(default=250)
