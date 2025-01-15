"""
Custom bokeh Widget models.
"""
from bokeh.core.enums import ButtonType
from bokeh.core.properties import (
    Any, Bool, Either, Enum, Float, Instance, Int, List, Nullable, Override,
    String, Tuple,
)
from bokeh.events import ModelEvent
from bokeh.models.ui import Tooltip
from bokeh.models.ui.icons import Icon
from bokeh.models.widgets import (
    Button as bkButton, CheckboxButtonGroup as bkCheckboxButtonGroup,
    InputWidget, MultiSelect, RadioButtonGroup as bkRadioButtonGroup, Select,
    TextAreaInput as bkTextAreaInput, TextInput as bkTextInput, Widget,
)

from .layout import HTMLBox


class DoubleClickEvent(ModelEvent):

    event_name = 'dblclick_event'

    def __init__(self, model, option=None):
        self.option = option
        super().__init__(model=model)


class Player(Widget):
    """
    The Player widget provides controls to play through a number of frames.
    """
    title = Nullable(String, default="", help="""
    The slider's label (supports :ref:`math text <ug_styling_mathtext>`).
    """)

    start = Int(0, help="Lower bound of the Player slider")

    end = Int(10, help="Upper bound of the Player slider")

    value = Int(0, help="Current value of the player app")

    value_throttled = Int(0, help="Current throttled value of the player app")

    value_align = String("start", help="""Location to display
        the value of the slider ("start" "center", "end")""")

    step = Int(1, help="Number of steps to advance the player by.")

    interval = Int(500, help="Interval between updates")

    direction = Int(0, help="""
        Current play direction of the Player (-1: playing in reverse,
        0: paused, 1: playing)""")

    loop_policy = Enum('once', 'reflect', 'loop', default='once')

    show_loop_controls = Bool(True, help="""Whether the loop controls
        radio buttons are shown""")

    preview_duration = Int(1500, help="""
        Duration (in milliseconds) for showing the current FPS when clicking
        the slower/faster buttons, before reverting to the icon.""")

    show_value = Bool(True, help="""
        Whether to show the widget value""")

    width = Override(default=400)  # type: ignore

    height = Override(default=250)  # type: ignore

    scale_buttons = Float(1, help="Percentage to scale the size of the buttons by")

    visible_buttons = List(String, default=[
        'slower', 'first', 'previous', 'reverse', 'pause', 'play', 'next', 'last', 'faster'
    ], help="The buttons to display on the player.")  # type: ignore

    visible_loop_options = List(String, default=[
        'once', 'loop', 'reflect'
    ], help="The loop options to display on the player.")  # type: ignore

class DiscretePlayer(Player):

    options = List(Any, help="""
        List of discrete options.""")


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

    size = Int(default=4, help="""
    The number of visible options in the dropdown list. (This uses the
    ``select`` HTML element's ``size`` attribute. Some browsers might not
    show less than 3 options.)
    """)

    value = Nullable(String, help="Initial or selected value.")


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

    volume = Nullable(Float, help="""The volume of the audio player.""")


class Video(HTMLBox):

    loop = Bool(False, help="""Whether the video should loop""")

    paused = Bool(False, help="""Whether the video is paused""")

    muted = Bool(False, help="""Whether the video is muted""")

    autoplay = Bool(False, help="""Whether the video is playing automatically""")

    time = Float(0, help="""
        The current time stamp of the video playback""")

    throttle = Int(250, help="""
        The frequency at which the time value is updated in milliseconds.""")

    value = String(help="Encoded file data")

    volume = Int(help="""The volume of the video player.""")


class VideoStream(HTMLBox):

    format = Enum('png', 'jpeg', default='png')

    paused = Bool(False, help="""Whether the video is paused""")

    snapshot = Bool(False, help="""On change generate a snapshot of the current video frame""")

    timeout = Nullable(Int, help="""
        The timeout between snapshots (if None snapshot only generated
        when snapshot property is changed""")

    value = Any(help="""Snapshot Data""")

    height = Override(default=240)  # type: ignore

    width = Override(default=320)  # type: ignore


class Progress(HTMLBox):

    active = Bool(True, help="""Whether to animate the bar""")

    bar_color = Enum('primary', 'secondary', 'success', 'info',
                     'danger', 'warning', 'light', 'dark', default='primary')

    max = Int(100, help="""Maximum value""")

    value = Nullable(Int, help="""Current value""")

    css = List(String)


class FileDownload(InputWidget):

    auto = Bool(False, help="""Whether to download on click""")

    button_type = Enum(ButtonType, help="""
    A style for the button, signifying it's role.
    """)

    clicks = Int(0, help="""
    A private property that used to trigger ``on_click`` event handler.
    """)

    data = String(help="""Encoded URI data.""")

    embed = Bool(False, help="""Whether the data is pre-embedded.""")

    icon = Nullable(Instance(Icon), help="""
    An optional image appearing to the left of button's text. An instance of
    :class:`~bokeh.models.Icon` (such as :class:`~bokeh.models.BuiltinIcon`,
    :class:`~bokeh.models.SVGIcon`, or :class:`~bokeh.models.TablerIcon`).`
    """)

    label = String("", help="""The text label for the button to display.""")

    filename = String(help="""Filename to use on download""")

    _transfers = Int(0, help="""
    A private property to create and click the link.
    """)

    title = Override(default='')  # type: ignore


class CustomSelect(Select):
    ''' Custom widget that extends the base Bokeh Select
    by adding a parameter to disable one or more options.

    '''
    disabled_options = List(Any, default=[], help="""
    List of options to disable.
    """)

    size = Int(default=1)


class CustomMultiSelect(MultiSelect):
    """
    MultiSelect widget which allows capturing double tap events.
    """

class TooltipIcon(Widget):
    description = Instance(
        Tooltip,
        default=Tooltip(content="Help text", position="right"),
        help="""The tooltip held by the icon"""
    )


class TextAreaInput(bkTextAreaInput):

    auto_grow = Bool(
        default=False,
        help="""
        Whether the text area should automatically grow vertically to
        accommodate the current text."""
    )

    max_rows = Nullable(Int(), help="""
        Maximum number of rows the input area can grow to if auto_grow
        is enabled."""
    )


class Button(bkButton):

    tooltip = Nullable(Instance(Tooltip), help="""
    A tooltip with plain text or rich HTML contents, providing general help or
    description of a widget's or component's function.
    """)

    tooltip_delay = Int(500, help="""
    Delay (in milliseconds) to display the tooltip after the cursor has
    hovered over the Button, default is 500ms.
    """)


class CheckboxButtonGroup(bkCheckboxButtonGroup):

    tooltip = Nullable(Instance(Tooltip), help="""
    A tooltip with plain text or rich HTML contents, providing general help or
    description of a widget's or component's function.
    """)

    tooltip_delay = Int(500, help="""
    Delay (in milliseconds) to display the tooltip after the cursor has
    hovered over the Button, default is 500ms.
    """)


class RadioButtonGroup(bkRadioButtonGroup):

    tooltip = Nullable(Instance(Tooltip), help="""
    A tooltip with plain text or rich HTML contents, providing general help or
    description of a widget's or component's function.
    """)

    tooltip_delay = Int(500, help="""
    Delay (in milliseconds) to display the tooltip after the cursor has
    hovered over the Button, default is 500ms.
    """)


class EnterEvent(ModelEvent):

    event_name = 'enter-pressed'

    def __init__(self, model, value_input):
        self.value_input = value_input
        super().__init__(model=model)

    def __repr__(self):
        return (
            f'{type(self).__name__}(value_input={self.value_input})'
        )

class TextInput(bkTextInput): ...
