"""
Panel widgets makes your data exploration and apps interactive
==============================================================

Panel provides a long range of basic and specialized widgets.

Check out the widget gallery
https://panel.holoviz.org/reference/index.html#widgets for inspiration.

How to use Panel widgets in 4 simple steps
------------------------------------------

1. Define your function

>>> def my_func(value1, value2):
...    ...
...    return some_python_object

2. Define your widgets

>>> widget1 = pn.widgets.SomeWidget(value=..., ...).servable(area='sidebar')
>>> widget2 = pn.widgets.AnotherWidget(value=..., ...).servable(area='sidebar')

3. Bind the function to your widgets

>>> interactive_func = pn.bind(my_func, value1=widget1, value2=widget2)

4. Layout your interactive function in a panel, Column, Row or similar

>>> pn.panel(interactive_func).servable()

For more detail see the Getting Started Guide
https://panel.holoviz.org/getting_started/index.html
"""
from .base import CompositeWidget, Widget  # noqa
from .button import Button, MenuButton, Toggle  # noqa
from .chatbox import ChatBox  # noqa
from .codeeditor import Ace, CodeEditor  # noqa
from .debugger import Debugger  # noqa
from .file_selector import FileSelector  # noqa
from .indicators import (  # noqa
    BooleanStatus, Dial, Gauge, LinearGauge, LoadingSpinner, Number, Progress,
    TooltipIcon, Tqdm, Trend,
)
from .input import (  # noqa
    ArrayInput, Checkbox, ColorPicker, DatePicker, DatetimeInput,
    DatetimePicker, DatetimeRangeInput, DatetimeRangePicker, FileInput,
    FloatInput, IntInput, LiteralInput, NumberInput, PasswordInput, Spinner,
    StaticText, Switch, TextAreaInput, TextInput,
)
from .misc import FileDownload, JSONEditor, VideoStream  # noqa
from .player import DiscretePlayer, Player  # noqa
from .select import (  # noqa
    AutocompleteInput, CheckBoxGroup, CheckButtonGroup, CrossSelector,
    MultiChoice, MultiSelect, RadioBoxGroup, RadioButtonGroup, Select,
    ToggleGroup,
)
from .slider import (  # noqa
    DateRangeSlider, DateSlider, DatetimeRangeSlider, DiscreteSlider,
    EditableFloatSlider, EditableIntSlider, EditableRangeSlider, FloatSlider,
    IntRangeSlider, IntSlider, RangeSlider,
)
from .speech_to_text import Grammar, GrammarList, SpeechToText  # noqa
from .tables import DataFrame, Tabulator  # noqa
from .terminal import Terminal  # noqa
from .text_to_speech import TextToSpeech, Utterance, Voice  # noqa
from .texteditor import TextEditor  # noqa
from .widget import widget  # noqa

__all__ = (
    "Ace",
    "ArrayInput",
    "AutocompleteInput",
    "BooleanStatus",
    "Button",
    "ChatBox",
    "Checkbox",
    "CheckBoxGroup",
    "CheckButtonGroup",
    "CodeEditor",
    "ColorPicker",
    "CompositeWidget",
    "CrossSelector",
    "DataFrame",
    "DatePicker",
    "DateRangeSlider",
    "DatetimeRangeSlider",
    "DateSlider",
    "DatetimeInput",
    "DatetimePicker",
    "DatetimeRangeInput",
    "DatetimeRangePicker",
    "Debugger",
    "Dial",
    "DiscretePlayer",
    "DiscreteSlider",
    "EditableFloatSlider",
    "EditableIntSlider",
    "EditableRangeSlider",
    "FileDownload",
    "FileInput",
    "FileSelector",
    "FloatInput",
    "FloatSlider",
    "Gauge",
    "Grammar",
    "GrammarList",
    "IntInput",
    "IntRangeSlider",
    "IntSlider",
    "JSONEditor",
    "LinearGauge",
    "LiteralInput",
    "LoadingSpinner",
    "MenuButton",
    "MultiChoice",
    "MultiSelect",
    "Number",
    "NumberInput",
    "PasswordInput",
    "Player",
    "Progress",
    "RadioBoxGroup",
    "RadioButtonGroup",
    "RangeSlider",
    "Select",
    "SpeechToText",
    "Spinner",
    "StaticText",
    "Switch",
    "Tabulator",
    "Terminal",
    "TextAreaInput",
    "TextEditor",
    "TextInput",
    "TextToSpeech",
    "Toggle",
    "ToggleGroup",
    "TooltipIcon",
    "Tqdm",
    "Trend",
    "Utterance",
    "VideoStream",
    "Voice",
    "Widget",
)
