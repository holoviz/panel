"""
Custom bokeh Widget models.
"""
from bokeh.core.enums import ButtonType
from bokeh.core.properties import (
    Any, Bool, Dict, Either, Enum, Float, Int, List, Nullable, Override,
    String, Tuple,
)
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets import InputWidget, Select, Widget


class Player(Widget):
    """
    The Player widget provides controls to play through a number of frames.
    """

    start = Int(0, help="Lower bound of the Player slider")

    end = Int(10, help="Upper bound of the Player slider")

    value = Int(0, help="Current value of the player app")

    value_throttled = Int(0, help="Current throttled value of the player app")

    step = Int(1, help="Number of steps to advance the player by.")

    interval = Int(500, help="Interval between updates")

    direction = Int(0, help="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    loop_policy = Enum('once', 'reflect', 'loop', default='once')

    show_loop_controls = Bool(True, help="""Whether the loop controls
        radio buttons are shown""")

    width = Override(default=400)

    height = Override(default=250)


class SingleSelect(InputWidget):
    ''' Single-select widget.

    '''

    disabled_options = List(Any, default=[], help="""
    List of options to disable.
    """)

    options = List(Either(String, Tuple(String, String)), help="""
    Available selection options. Options may be provided either as a list of
    possible string values, or as a list of tuples, each of the form
    ``(value, label)``. In the latter case, the visible widget text for each
    value will be corresponding given label.
    """)

    value = String(help="Initial or selected value.")

    size = Int(default=4, help="""
    The number of visible options in the dropdown list. (This uses the
    ``select`` HTML element's ``size`` attribute. Some browsers might not
    show less than 3 options.)
    """)


class Audio(HTMLBox):

    loop = Bool(False, help="""Whether the audio should loop""")

    paused = Bool(False, help="""Whether the audio is paused""")

    muted = Bool(False, help="""Whether the audio is muted""")

    autoplay = Bool(False, help="""Whether the audio is playing automatically""")

    time = Float(0, help="""
        The current time stamp of the audio playback""")

    throttle = Int(250, help="""
        The frequency at which the time value is updated in milliseconds.""")

    value = Any(help="Encoded file data")

    volume = Int(0, help="""The volume of the audio player.""")


class Video(HTMLBox):

    loop = Bool(False, help="""Whether the video should loop""")

    paused = Bool(False, help="""Whether the video is paused""")

    muted = Bool(False, help="""Whether the video is muted""")

    autoplay = Bool(False, help="""Whether the video is playing automatically""")

    time = Float(0, help="""
        The current time stamp of the video playback""")

    throttle = Int(250, help="""
        The frequency at which the time value is updated in milliseconds.""")

    value = Any(help="Encoded file data")

    volume = Int(help="""The volume of the video player.""")


class VideoStream(HTMLBox):

    format = Enum('png', 'jpeg', default='png')

    paused = Bool(False, help="""Whether the video is paused""")

    snapshot = Bool(False, help="""On change generate a snapshot of the current video frame""")

    timeout = Nullable(Int, help="""
        The timeout between snapshots (if None snapshot only generated
        when snapshot property is changed""")

    value = Any(help="""Snapshot Data""")

    height = Override(default=240)

    width = Override(default=320)


class Progress(HTMLBox):

    active = Bool(True, help="""Whether to animate the bar""")

    bar_color = Enum('primary', 'secondary', 'success', 'info',
                     'danger', 'warning', 'light', 'dark', default='primary')

    max = Int(100, help="""Maximum value""")

    value = Nullable(Int, help="""Current value""")

    style = Dict(String, Any, default={}, help="""
    Raw CSS style declaration. Note this may be web browser dependent.
    """)


class FileDownload(InputWidget):

    auto = Bool(False, help="""Whether to download on click""")

    button_type = Enum(ButtonType, help="""
    A style for the button, signifying it's role.
    """)

    clicks = Int(0, help="""
    A private property that used to trigger ``on_click`` event handler.
    """)

    data = String(help="""Encoded URI data.""")

    label = String("", help="""The text label for the button to display.""")

    filename = String(help="""Filename to use on download""")

    _transfers = Int(0, help="""
    A private property to create and click the link.
    """)

    title = Override(default='')


class CustomSelect(Select):
    ''' Custom widget that extends the base Bokeh Select
    by adding a parameter to disable one or more options.

    '''
    disabled_options = List(Any, default=[], help="""
    List of options to disable.
    """)
