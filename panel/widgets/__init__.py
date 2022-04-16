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
from .ace import Ace as Ace  # noqa
from .base import Widget as Widget, CompositeWidget as CompositeWidget  # noqa
from .button import ( # noqa
    Button as Button,
    MenuButton as MenuButton,
    Toggle as Toggle,
)  
from .file_selector import FileSelector as FileSelector  # noqa
from .indicators import (  # noqa
    BooleanStatus as BooleanStatus,
    Dial as Dial,
    Gauge as Gauge,
    LinearGauge as LinearGauge,
    LoadingSpinner as LoadingSpinner,
    Number as Number,
    Progress as Progress,
    Trend as Trend,
    Tqdm as Tqdm,
)
from .input import (  # noqa
    ArrayInput as ArrayInput,
    ColorPicker as ColorPicker,
    Checkbox as Checkbox,
    DatetimeInput as DatetimeInput,
    DatePicker as DatePicker,
    DatetimePicker as DatetimePicker,
    DatetimeRangeInput as DatetimeRangeInput,
    DatetimeRangePicker as DatetimeRangePicker,
    FileInput as FileInput,
    LiteralInput as LiteralInput,
    StaticText as StaticText,
    TextInput as TextInput,
    IntInput as IntInput,
    FloatInput as FloatInput,
    NumberInput as NumberInput,
    Spinner as Spinner,
    PasswordInput as PasswordInput,
    TextAreaInput as TextAreaInput,
)
from .misc import ( # noqa
    FileDownload as FileDownload,
    JSONEditor as JSONEditor,
    VideoStream as VideoStream,
)  
from .player import DiscretePlayer as DiscretePlayer, Player as Player  # noqa
from .slider import (  # noqa
    DateSlider as DateSlider,
    DateRangeSlider as DateRangeSlider,
    DiscreteSlider as DiscreteSlider,
    EditableRangeSlider as EditableRangeSlider,
    EditableFloatSlider as EditableFloatSlider,
    EditableIntSlider as EditableIntSlider,
    FloatSlider as FloatSlider,
    IntSlider as IntSlider,
    IntRangeSlider as IntRangeSlider,
    RangeSlider as RangeSlider,
)
from .select import (  # noqa
    AutocompleteInput as AutocompleteInput,
    CheckBoxGroup as CheckBoxGroup,
    CheckButtonGroup as CheckButtonGroup,
    CrossSelector as CrossSelector,
    MultiChoice as MultiChoice,
    MultiSelect as MultiSelect,
    RadioButtonGroup as RadioButtonGroup,
    RadioBoxGroup as RadioBoxGroup,
    Select as Select,
    ToggleGroup as ToggleGroup,
)
from .speech_to_text import ( # noqa
    SpeechToText as SpeechToText,
    Grammar as Grammar,
    GrammarList as GrammarList,
)  
from .tables import DataFrame as DataFrame, Tabulator as Tabulator  # noqa
from .terminal import Terminal as Terminal  # noqa
from .debugger import Debugger as Debugger  # noqa
from .text_to_speech import ( # noqa
    TextToSpeech as TextToSpeech,
    Utterance as Utterance,
    Voice as Voice,
)  
from .texteditor import TextEditor as TextEditor  # noqa
