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
from typing import TYPE_CHECKING as _TC

from .widget import widget

if _TC:
    from .base import CompositeWidget, Widget, WidgetBase
    from .button import Button, MenuButton, Toggle
    from .codeeditor import CodeEditor
    from .debugger import Debugger
    from .file_selector import FileSelector
    from .icon import ButtonIcon, ToggleIcon
    from .indicators import (
        BooleanStatus, Dial, Gauge, LinearGauge, LoadingSpinner, Number,
        Progress, TooltipIcon, Tqdm, Trend,
    )
    from .input import (
        ArrayInput, Checkbox, ColorPicker, DatePicker, DateRangePicker,
        DatetimeInput, DatetimePicker, DatetimeRangeInput, DatetimeRangePicker,
        FileDropper, FileInput, FloatInput, IntInput, LiteralInput,
        NumberInput, PasswordInput, Spinner, StaticText, Switch, TextAreaInput,
        TextInput, TimePicker,
    )
    from .misc import FileDownload, JSONEditor, VideoStream
    from .player import DiscretePlayer, Player
    from .select import (
        AutocompleteInput, CheckBoxGroup, CheckButtonGroup, ColorMap,
        CrossSelector, MultiChoice, MultiSelect, NestedSelect, RadioBoxGroup,
        RadioButtonGroup, Select, ToggleGroup,
    )
    from .slider import (
        DateRangeSlider, DateSlider, DatetimeRangeSlider, DiscreteSlider,
        EditableFloatSlider, EditableIntSlider, EditableRangeSlider,
        FloatSlider, IntRangeSlider, IntSlider, RangeSlider,
    )
    from .speech_to_text import Grammar, GrammarList, SpeechToText
    from .tables import DataFrame, Tabulator
    from .terminal import Terminal
    from .text_to_speech import TextToSpeech, Utterance, Voice
    from .texteditor import TextEditor

_attrs = {
    "ArrayInput": "panel.widgets.input:ArrayInput",
    "AutocompleteInput": "panel.widgets.select:AutocompleteInput",
    "BooleanStatus": "panel.widgets.indicators:BooleanStatus",
    "Button": "panel.widgets.button:Button",
    "ButtonIcon": "panel.widgets.icon:ButtonIcon",
    "Checkbox": "panel.widgets.input:Checkbox",
    "CheckBoxGroup": "panel.widgets.select:CheckBoxGroup",
    "CheckButtonGroup": "panel.widgets.select:CheckButtonGroup",
    "CodeEditor": "panel.widgets.codeeditor:CodeEditor",
    "ColorMap": "panel.widgets.select:ColorMap",
    "ColorPicker": "panel.widgets.input:ColorPicker",
    "CompositeWidget": "panel.widgets.base:CompositeWidget",
    "CrossSelector": "panel.widgets.select:CrossSelector",
    "DataFrame": "panel.widgets.tables:DataFrame",
    "DatePicker": "panel.widgets.input:DatePicker",
    "DateRangePicker": "panel.widgets.input:DateRangePicker",
    "DateRangeSlider": "panel.widgets.slider:DateRangeSlider",
    "DatetimeRangeSlider": "panel.widgets.slider:DatetimeRangeSlider",
    "DateSlider": "panel.widgets.slider:DateSlider",
    "DatetimeInput": "panel.widgets.input:DatetimeInput",
    "DatetimePicker": "panel.widgets.input:DatetimePicker",
    "DatetimeRangeInput": "panel.widgets.input:DatetimeRangeInput",
    "DatetimeRangePicker": "panel.widgets.input:DatetimeRangePicker",
    "Debugger": "panel.widgets.debugger:Debugger",
    "Dial": "panel.widgets.indicators:Dial",
    "DiscretePlayer": "panel.widgets.player:DiscretePlayer",
    "DiscreteSlider": "panel.widgets.slider:DiscreteSlider",
    "EditableFloatSlider": "panel.widgets.slider:EditableFloatSlider",
    "EditableIntSlider": "panel.widgets.slider:EditableIntSlider",
    "EditableRangeSlider": "panel.widgets.slider:EditableRangeSlider",
    "FileDownload": "panel.widgets.misc:FileDownload",
    "FileDropper": "panel.widgets.input:FileDropper",
    "FileInput": "panel.widgets.input:FileInput",
    "FileSelector": "panel.widgets.file_selector:FileSelector",
    "FloatInput": "panel.widgets.input:FloatInput",
    "FloatSlider": "panel.widgets.slider:FloatSlider",
    "Gauge": "panel.widgets.indicators:Gauge",
    "Grammar": "panel.widgets.speech_to_text:Grammar",
    "GrammarList": "panel.widgets.speech_to_text:GrammarList",
    "IntInput": "panel.widgets.input:IntInput",
    "IntRangeSlider": "panel.widgets.slider:IntRangeSlider",
    "IntSlider": "panel.widgets.slider:IntSlider",
    "JSONEditor": "panel.widgets.misc:JSONEditor",
    "LinearGauge": "panel.widgets.indicators:LinearGauge",
    "LiteralInput": "panel.widgets.input:LiteralInput",
    "LoadingSpinner": "panel.widgets.indicators:LoadingSpinner",
    "MenuButton": "panel.widgets.button:MenuButton",
    "MultiChoice": "panel.widgets.select:MultiChoice",
    "MultiSelect": "panel.widgets.select:MultiSelect",
    "NestedSelect": "panel.widgets.select:NestedSelect",
    "Number": "panel.widgets.indicators:Number",
    "NumberInput": "panel.widgets.input:NumberInput",
    "PasswordInput": "panel.widgets.input:PasswordInput",
    "Player": "panel.widgets.player:Player",
    "Progress": "panel.widgets.indicators:Progress",
    "RadioBoxGroup": "panel.widgets.select:RadioBoxGroup",
    "RadioButtonGroup": "panel.widgets.select:RadioButtonGroup",
    "RangeSlider": "panel.widgets.slider:RangeSlider",
    "Select": "panel.widgets.select:Select",
    "SpeechToText": "panel.widgets.speech_to_text:SpeechToText",
    "Spinner": "panel.widgets.input:Spinner",
    "StaticText": "panel.widgets.input:StaticText",
    "Switch": "panel.widgets.input:Switch",
    "Tabulator": "panel.widgets.tables:Tabulator",
    "Terminal": "panel.widgets.terminal:Terminal",
    "TextAreaInput": "panel.widgets.input:TextAreaInput",
    "TextEditor": "panel.widgets.texteditor:TextEditor",
    "TextInput": "panel.widgets.input:TextInput",
    "TextToSpeech": "panel.widgets.text_to_speech:TextToSpeech",
    "TimePicker": "panel.widgets.input:TimePicker",
    "Toggle": "panel.widgets.button:Toggle",
    "ToggleGroup": "panel.widgets.select:ToggleGroup",
    "ToggleIcon": "panel.widgets.icon:ToggleIcon",
    "TooltipIcon": "panel.widgets.indicators:TooltipIcon",
    "Tqdm": "panel.widgets.indicators:Tqdm",
    "Trend": "panel.widgets.indicators:Trend",
    "Utterance": "panel.widgets.text_to_speech:Utterance",
    "VideoStream": "panel.widgets.misc:VideoStream",
    "Voice": "panel.widgets.text_to_speech:Voice",
    "Widget": "panel.widgets.base:Widget",
    "WidgetBase": "panel.widgets.base:WidgetBase",
}


def __getattr__(name: str) -> object:
    if name in _attrs:
        import importlib
        mod_name, _, attr_name = _attrs[name].partition(':')
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name) if attr_name else mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = (
    "ArrayInput",
    "AutocompleteInput",
    "BooleanStatus",
    "Button",
    "ButtonIcon",
    "Checkbox",
    "CheckBoxGroup",
    "CheckButtonGroup",
    "CodeEditor",
    "ColorMap",
    "ColorPicker",
    "CompositeWidget",
    "CrossSelector",
    "DataFrame",
    "DatePicker",
    "DateRangePicker",
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
    "FileDropper",
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
    "NestedSelect",
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
    "TimePicker",
    "Toggle",
    "ToggleGroup",
    "ToggleIcon",
    "TooltipIcon",
    "Tqdm",
    "Trend",
    "Utterance",
    "VideoStream",
    "Voice",
    "Widget",
    "WidgetBase",
    "widget",
)

__dir__ = lambda: list(__all__)
