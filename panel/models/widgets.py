import os

from bokeh.core.properties import Int, Override, Enum, String
from bokeh.models import Widget

from ..util import CUSTOM_MODELS


class Player(Widget):
    """
    The Player widget provides controls to play through a number of frames.
    """

    __implementation__ = os.path.join(os.path.dirname(__file__), 'player.ts')

    start = Int(help="Lower bound of the Player slider")

    end = Int(help="Upper bound of the Player slider")

    value = Int(0, help="Current value of the player app")

    step = Int(1, help="Number of steps to advance the player by.")

    interval = Int(500, help="Interval between updates")

    direction = Int(0, help="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    loop_policy = Enum('once', 'reflect', 'loop', default='once')

    height = Override(default=250)


class FileInput(Widget):

    __implementation__ = os.path.join(os.path.dirname(__file__), 'fileinput.ts')

    value = String(help="Selected file")


CUSTOM_MODELS['panel.models.widgets.Player'] = Player
CUSTOM_MODELS['panel.models.widgets.FileInput'] = FileInput

