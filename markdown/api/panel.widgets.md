# panel.widgets package

## Submodules

- [panel.widgets.base module](panel.widgets.base.md)
  - [CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)
    - [CompositeWidget.select()](panel.widgets.base.md#panel.widgets.base.CompositeWidget.select)
  - [Widget](panel.widgets.base.md#panel.widgets.base.Widget)
  - [WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase)
    - [WidgetBase.from_param()](panel.widgets.base.md#panel.widgets.base.WidgetBase.from_param)
    - [WidgetBase.from_values()](panel.widgets.base.md#panel.widgets.base.WidgetBase.from_values)
- [panel.widgets.button module](panel.widgets.button.md)
  - [Button](panel.widgets.button.md#panel.widgets.button.Button)
    - [Button.jslink()](panel.widgets.button.md#panel.widgets.button.Button.jslink)
    - [Button.on_click()](panel.widgets.button.md#panel.widgets.button.Button.on_click)
  - [IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)
  - [MenuButton](panel.widgets.button.md#panel.widgets.button.MenuButton)
    - [MenuButton.on_click()](panel.widgets.button.md#panel.widgets.button.MenuButton.on_click)
  - [Toggle](panel.widgets.button.md#panel.widgets.button.Toggle)
- [panel.widgets.codeeditor module](panel.widgets.codeeditor.md)
  - [CodeEditor](panel.widgets.codeeditor.md#panel.widgets.codeeditor.CodeEditor)
- [panel.widgets.debugger module](panel.widgets.debugger.md)
  - [CheckFilter](panel.widgets.debugger.md#panel.widgets.debugger.CheckFilter)
    - [CheckFilter.add_debugger()](panel.widgets.debugger.md#panel.widgets.debugger.CheckFilter.add_debugger)
    - [CheckFilter.filter()](panel.widgets.debugger.md#panel.widgets.debugger.CheckFilter.filter)
  - [Debugger](panel.widgets.debugger.md#panel.widgets.debugger.Debugger)
  - [DebuggerButtons](panel.widgets.debugger.md#panel.widgets.debugger.DebuggerButtons)
  - [TermFormatter](panel.widgets.debugger.md#panel.widgets.debugger.TermFormatter)
    - [TermFormatter.format()](panel.widgets.debugger.md#panel.widgets.debugger.TermFormatter.format)
- [panel.widgets.file_selector module](panel.widgets.file_selector.md)
  - [BaseFileNavigator](panel.widgets.file_selector.md#panel.widgets.file_selector.BaseFileNavigator)
  - [BaseFileSelector](panel.widgets.file_selector.md#panel.widgets.file_selector.BaseFileSelector)
  - [FileSelector](panel.widgets.file_selector.md#panel.widgets.file_selector.FileSelector)
- [panel.widgets.icon module](panel.widgets.icon.md)
  - [ButtonIcon](panel.widgets.icon.md#panel.widgets.icon.ButtonIcon)
    - [ButtonIcon.on_click()](panel.widgets.icon.md#panel.widgets.icon.ButtonIcon.on_click)
  - [ToggleIcon](panel.widgets.icon.md#panel.widgets.icon.ToggleIcon)
- [panel.widgets.indicators module](panel.widgets.indicators.md)
  - [Indicators](panel.widgets.indicators.md#indicators)
    - [How to use indicators](panel.widgets.indicators.md#how-to-use-indicators)
  - [BooleanIndicator](panel.widgets.indicators.md#panel.widgets.indicators.BooleanIndicator)
  - [BooleanStatus](panel.widgets.indicators.md#panel.widgets.indicators.BooleanStatus)
  - [Dial](panel.widgets.indicators.md#panel.widgets.indicators.Dial)
  - [Gauge](panel.widgets.indicators.md#panel.widgets.indicators.Gauge)
  - [LinearGauge](panel.widgets.indicators.md#panel.widgets.indicators.LinearGauge)
  - [LoadingSpinner](panel.widgets.indicators.md#panel.widgets.indicators.LoadingSpinner)
  - [Number](panel.widgets.indicators.md#panel.widgets.indicators.Number)
  - [Progress](panel.widgets.indicators.md#panel.widgets.indicators.Progress)
    - [Progress.sizing_mode](panel.widgets.indicators.md#panel.widgets.indicators.Progress.sizing_mode)
  - [String](panel.widgets.indicators.md#panel.widgets.indicators.String)
  - [TooltipIcon](panel.widgets.indicators.md#panel.widgets.indicators.TooltipIcon)
  - [Tqdm](panel.widgets.indicators.md#panel.widgets.indicators.Tqdm)
    - [Tqdm.reset()](panel.widgets.indicators.md#panel.widgets.indicators.Tqdm.reset)
  - [Trend](panel.widgets.indicators.md#panel.widgets.indicators.Trend)
    - [Trend.sizing_mode](panel.widgets.indicators.md#panel.widgets.indicators.Trend.sizing_mode)
  - [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)
- [panel.widgets.input module](panel.widgets.input.md)
  - [ArrayInput](panel.widgets.input.md#panel.widgets.input.ArrayInput)
  - [Checkbox](panel.widgets.input.md#panel.widgets.input.Checkbox)
  - [ColorPicker](panel.widgets.input.md#panel.widgets.input.ColorPicker)
  - [DatePicker](panel.widgets.input.md#panel.widgets.input.DatePicker)
  - [DateRangePicker](panel.widgets.input.md#panel.widgets.input.DateRangePicker)
  - [DatetimeInput](panel.widgets.input.md#panel.widgets.input.DatetimeInput)
    - [DatetimeInput.type](panel.widgets.input.md#panel.widgets.input.DatetimeInput.type)
  - [DatetimePicker](panel.widgets.input.md#panel.widgets.input.DatetimePicker)
  - [DatetimeRangeInput](panel.widgets.input.md#panel.widgets.input.DatetimeRangeInput)
  - [DatetimeRangePicker](panel.widgets.input.md#panel.widgets.input.DatetimeRangePicker)
  - [FileDropper](panel.widgets.input.md#panel.widgets.input.FileDropper)
  - [FileInput](panel.widgets.input.md#panel.widgets.input.FileInput)
    - [FileInput.clear()](panel.widgets.input.md#panel.widgets.input.FileInput.clear)
    - [FileInput.save()](panel.widgets.input.md#panel.widgets.input.FileInput.save)
  - [FloatInput](panel.widgets.input.md#panel.widgets.input.FloatInput)
  - [IntInput](panel.widgets.input.md#panel.widgets.input.IntInput)
  - [LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput)
  - [NumberInput](panel.widgets.input.md#panel.widgets.input.NumberInput)
  - [PasswordInput](panel.widgets.input.md#panel.widgets.input.PasswordInput)
  - [Spinner](panel.widgets.input.md#panel.widgets.input.Spinner)
  - [StaticText](panel.widgets.input.md#panel.widgets.input.StaticText)
  - [Switch](panel.widgets.input.md#panel.widgets.input.Switch)
  - [TextAreaInput](panel.widgets.input.md#panel.widgets.input.TextAreaInput)
  - [TextInput](panel.widgets.input.md#panel.widgets.input.TextInput)
  - [TimePicker](panel.widgets.input.md#panel.widgets.input.TimePicker)
- [panel.widgets.misc module](panel.widgets.misc.md)
  - [FileDownload](panel.widgets.misc.md#panel.widgets.misc.FileDownload)
  - [JSONEditor](panel.widgets.misc.md#panel.widgets.misc.JSONEditor)
  - [VideoStream](panel.widgets.misc.md#panel.widgets.misc.VideoStream)
    - [VideoStream.snapshot()](panel.widgets.misc.md#panel.widgets.misc.VideoStream.snapshot)
- [panel.widgets.player module](panel.widgets.player.md)
  - [DiscretePlayer](panel.widgets.player.md#panel.widgets.player.DiscretePlayer)
  - [Player](panel.widgets.player.md#panel.widgets.player.Player)
  - [PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase)
- [panel.widgets.select module](panel.widgets.select.md)
  - [AutocompleteInput](panel.widgets.select.md#panel.widgets.select.AutocompleteInput)
  - [CheckBoxGroup](panel.widgets.select.md#panel.widgets.select.CheckBoxGroup)
  - [CheckButtonGroup](panel.widgets.select.md#panel.widgets.select.CheckButtonGroup)
  - [ColorMap](panel.widgets.select.md#panel.widgets.select.ColorMap)
  - [CrossSelector](panel.widgets.select.md#panel.widgets.select.CrossSelector)
    - [CrossSelector.filter_fn()](panel.widgets.select.md#panel.widgets.select.CrossSelector.filter_fn)
  - [MultiChoice](panel.widgets.select.md#panel.widgets.select.MultiChoice)
  - [MultiSelect](panel.widgets.select.md#panel.widgets.select.MultiSelect)
    - [MultiSelect.on_double_click()](panel.widgets.select.md#panel.widgets.select.MultiSelect.on_double_click)
  - [NestedSelect](panel.widgets.select.md#panel.widgets.select.NestedSelect)
    - [NestedSelect.layout](panel.widgets.select.md#panel.widgets.select.NestedSelect.layout)
  - [RadioBoxGroup](panel.widgets.select.md#panel.widgets.select.RadioBoxGroup)
  - [RadioButtonGroup](panel.widgets.select.md#panel.widgets.select.RadioButtonGroup)
  - [Select](panel.widgets.select.md#panel.widgets.select.Select)
  - [SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase)
  - [SingleSelectBase](panel.widgets.select.md#panel.widgets.select.SingleSelectBase)
  - [ToggleGroup](panel.widgets.select.md#panel.widgets.select.ToggleGroup)
- [panel.widgets.slider module](panel.widgets.slider.md)
  - [ContinuousSlider](panel.widgets.slider.md#panel.widgets.slider.ContinuousSlider)
  - [DateRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DateRangeSlider)
  - [DateSlider](panel.widgets.slider.md#panel.widgets.slider.DateSlider)
  - [DatetimeRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DatetimeRangeSlider)
  - [DatetimeSlider](panel.widgets.slider.md#panel.widgets.slider.DatetimeSlider)
  - [DiscreteSlider](panel.widgets.slider.md#panel.widgets.slider.DiscreteSlider)
    - [DiscreteSlider.labels](panel.widgets.slider.md#panel.widgets.slider.DiscreteSlider.labels)
    - [DiscreteSlider.values](panel.widgets.slider.md#panel.widgets.slider.DiscreteSlider.values)
  - [EditableFloatSlider](panel.widgets.slider.md#panel.widgets.slider.EditableFloatSlider)
  - [EditableIntSlider](panel.widgets.slider.md#panel.widgets.slider.EditableIntSlider)
  - [EditableRangeSlider](panel.widgets.slider.md#panel.widgets.slider.EditableRangeSlider)
  - [FloatSlider](panel.widgets.slider.md#panel.widgets.slider.FloatSlider)
  - [IntRangeSlider](panel.widgets.slider.md#panel.widgets.slider.IntRangeSlider)
  - [IntSlider](panel.widgets.slider.md#panel.widgets.slider.IntSlider)
  - [RangeSlider](panel.widgets.slider.md#panel.widgets.slider.RangeSlider)
- [panel.widgets.speech_to_text module](panel.widgets.speech_to_text.md)
  - [Grammar](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.Grammar)
    - [Grammar.serialize()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.Grammar.serialize)
  - [GrammarList](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.GrammarList)
    - [GrammarList.add_from_string()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.GrammarList.add_from_string)
    - [GrammarList.add_from_uri()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.GrammarList.add_from_uri)
    - [GrammarList.serialize()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.GrammarList.serialize)
  - [Language](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.Language)
  - [RecognitionAlternative](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionAlternative)
  - [RecognitionResult](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionResult)
    - [RecognitionResult.create_from_dict()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionResult.create_from_dict)
    - [RecognitionResult.create_from_list()](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.RecognitionResult.create_from_list)
  - [SpeechToText](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.SpeechToText)
    - [SpeechToText.results_as_html](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.SpeechToText.results_as_html)
    - [SpeechToText.results_deserialized](panel.widgets.speech_to_text.md#panel.widgets.speech_to_text.SpeechToText.results_deserialized)
- [panel.widgets.tables module](panel.widgets.tables.md)
  - [BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable)
    - [BaseTable.add_filter()](panel.widgets.tables.md#panel.widgets.tables.BaseTable.add_filter)
    - [BaseTable.current_view](panel.widgets.tables.md#panel.widgets.tables.BaseTable.current_view)
    - [BaseTable.patch()](panel.widgets.tables.md#panel.widgets.tables.BaseTable.patch)
    - [BaseTable.remove_filter()](panel.widgets.tables.md#panel.widgets.tables.BaseTable.remove_filter)
    - [BaseTable.selected_dataframe](panel.widgets.tables.md#panel.widgets.tables.BaseTable.selected_dataframe)
    - [BaseTable.stream()](panel.widgets.tables.md#panel.widgets.tables.BaseTable.stream)
  - [ColumnSpec](panel.widgets.tables.md#panel.widgets.tables.ColumnSpec)
  - [DataFrame](panel.widgets.tables.md#panel.widgets.tables.DataFrame)
  - [GroupSpec](panel.widgets.tables.md#panel.widgets.tables.GroupSpec)
  - [Tabulator](panel.widgets.tables.md#panel.widgets.tables.Tabulator)
    - [Tabulator.current_view](panel.widgets.tables.md#panel.widgets.tables.Tabulator.current_view)
    - [Tabulator.download()](panel.widgets.tables.md#panel.widgets.tables.Tabulator.download)
    - [Tabulator.download_menu()](panel.widgets.tables.md#panel.widgets.tables.Tabulator.download_menu)
    - [Tabulator.on_click()](panel.widgets.tables.md#panel.widgets.tables.Tabulator.on_click)
    - [Tabulator.on_edit()](panel.widgets.tables.md#panel.widgets.tables.Tabulator.on_edit)
    - [Tabulator.stream()](panel.widgets.tables.md#panel.widgets.tables.Tabulator.stream)
- [panel.widgets.terminal module](panel.widgets.terminal.md)
  - [Terminal](panel.widgets.terminal.md#panel.widgets.terminal.Terminal)
    - [Terminal.subprocess](panel.widgets.terminal.md#panel.widgets.terminal.Terminal.subprocess)
  - [TerminalSubprocess](panel.widgets.terminal.md#panel.widgets.terminal.TerminalSubprocess)
    - [TerminalSubprocess.run()](panel.widgets.terminal.md#panel.widgets.terminal.TerminalSubprocess.run)
- [panel.widgets.text_to_speech module](panel.widgets.text_to_speech.md)
  - [TextToSpeech](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.TextToSpeech)
  - [Utterance](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Utterance)
    - [Utterance.set_voices()](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Utterance.set_voices)
    - [Utterance.to_dict()](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Utterance.to_dict)
  - [Voice](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Voice)
    - [Voice.group_by_lang()](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Voice.group_by_lang)
    - [Voice.to_voices_list()](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Voice.to_voices_list)
- [panel.widgets.texteditor module](panel.widgets.texteditor.md)
  - [TextEditor](panel.widgets.texteditor.md#panel.widgets.texteditor.TextEditor)
- [panel.widgets.widget module](panel.widgets.widget.md)
  - [fixed](panel.widgets.widget.md#panel.widgets.widget.fixed)
    - [fixed.get_interact_value()](panel.widgets.widget.md#panel.widgets.widget.fixed.get_interact_value)
  - [widget](panel.widgets.widget.md#panel.widgets.widget.widget)
    - [widget.widget_from_iterable()](panel.widgets.widget.md#panel.widgets.widget.widget.widget_from_iterable)
    - [widget.widget_from_single_value()](panel.widgets.widget.md#panel.widgets.widget.widget.widget_from_single_value)
    - [widget.widget_from_tuple()](panel.widgets.widget.md#panel.widgets.widget.widget.widget_from_tuple)

## Module contents

### Panel widgets makes your data exploration and apps interactive

Panel provides a long range of basic and specialized widgets.

Check out the widget gallery
[https://panel.holoviz.org/reference/index.html#widgets](https://panel.holoviz.org/reference/index.html#widgets)
for inspiration.

#### How to use Panel widgets in 4 simple steps

1.  Define your function

\>\>\>
def
my_func(value1,
value2):
...  ...
...  return
some_python_object

2.  Define your widgets

\>\>\> widget1
=
pn.widgets.SomeWidget(value=...,
...).servable(area='sidebar')
\>\>\> widget2
=
pn.widgets.AnotherWidget(value=...,
...).servable(area='sidebar')

3.  Bind the function to your widgets

\>\>\> interactive_func
=
pn.bind(my_func,
value1=widget1,
value2=widget2)

4.  Layout your interactive function in a panel, Column, Row or similar

\>\>\>
pn.panel(interactive_func).servable()

For more detail see the Getting Started Guide
[https://panel.holoviz.org/getting_started/index.html](https://panel.holoviz.org/getting_started/index.html)

class panel.widgets.ArrayInput(\*, max_array_size, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput)

The ArrayInput allows rendering and editing NumPy arrays in a text input
widget.

Arrays larger than the max_array_size will be summarized and editing
will be disabled.

Reference:
[https://panel.holoviz.org/reference/widgets/ArrayInput.html](https://panel.holoviz.org/reference/widgets/ArrayInput.html)

Example:

\>\>\> To
be determined
...

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal"
> title="panel.widgets.input.LiteralInput"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets. input .LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput):
> value, width, description, placeholder, serializer, type
>
>

`max_array_size`` ``=`` ``Integer(default=1000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``array`` ``size')`
Arrays larger than this limit will be allowed in Python but will not be
serialized into JavaScript. Although such large arrays will thus not be
editable in the widget, such a restriction helps avoid overwhelming the
browser and lets other widgets remain usable.

class panel.widgets.AutocompleteInput(\*, case_sensitive, description, min_characters, placeholder, restrict, search_strategy, value_input, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](panel.widgets.select.md#panel.widgets.select.SingleSelectBase)

The AutocompleteInput widget allows selecting multiple values from a
list of options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the MultiSelect,
CrossSelector, CheckBoxGroup and CheckButtonGroup widgets.

The MultiChoice widget provides a much more compact UI than MultiSelect.

Reference: [https://panel.holoviz.org/reference/widgets/AutocompleteInput.html](https://panel.holoviz.org/reference/widgets/AutocompleteInput.html)

Example:

\>\>\>
AutocompleteInput(
...
name='Study',
options=\['Biology',
'Chemistry',
'Physics'\],
...
placeholder='Write
your study here ...' ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``default='',`` ``label='Value')`
Initial or entered text value updated when \<enter\> key is pressed.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`case_sensitive`` ``=`` ``Boolean(default=True,`` ``label='Case`` ``sensitive')`
Enable or disable case sensitivity.

`min_characters`` ``=`` ``Integer(default=2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Min`` ``characters')`
The number of characters a user must type before completions are
presented.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder for empty input field.

`restrict`` ``=`` ``Boolean(default=True,`` ``label='Restrict')`
Set to False in order to allow users to enter text that is not present
in the list of completion strings.

`search_strategy`` ``=`` ``Selector(default='starts_with',`` ``label='Search`` ``strategy',`` ``names={},`` ``objects=['starts_with',`` ``'includes'])`
Define how to search the list of completion strings. The default option
“starts_with” means that the user’s text must match the start of a
completion string. Using “includes” means that the user’s text can match
any substring of a completion string.

`value_input`` ``=`` ``String(allow_None=True,`` ``default='',`` ``label='Value`` ``input')`
Initial or entered text value updated on every key press.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.BooleanStatus(\*, color, throttle, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [BooleanIndicator](panel.widgets.indicators.md#panel.widgets.indicators.BooleanIndicator)

The BooleanStatus is a boolean indicator providing a visual
representation of a boolean status as filled or non-filled circle.

If the value is set to True the indicator will be filled while setting
it to False will cause it to be non-filled.

Reference: [https://panel.holoviz.org/reference/indicators/BooleanStatus.html](https://panel.holoviz.org/reference/indicators/BooleanStatus.html)

Example:

\>\>\>
BooleanStatus(value=True,
color='primary',
width=100,
height=100)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> href="panel.widgets.indicators.html#panel.widgets.indicators.BooleanIndicator"
> class="reference internal"
> title="panel.widgets.indicators.BooleanIndicator"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.BooleanIndicator:
> throttle
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Whether the indicator is active or not.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
height of the circle.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of the circle.

`color`` ``=`` ``Selector(default='dark',`` ``label='Color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the circle, one of ‘primary’, ‘secondary’, ‘success’,
‘info’, ‘danger’, ‘warning’, ‘light’, ‘dark’

class panel.widgets.Button(\*, clicks, button_style, button_type, color, variant, icon, icon_size, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ButtonBase`,
`_ClickButton`,
[IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin),
`TooltipMixin`

The Button widget allows triggering events when the button is clicked.

The Button provides a value parameter, which will toggle from False to
True while the click event is being processed

It also provides an additional clicks parameter, that can be watched to
subscribe to click events.

Reference: [https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button](https://panel.holoviz.org/reference/widgets/Button.html#widgets-gallery-button)

Example:

\>\>\>
pn.widgets.Button(name='Click
me',
icon='caret-right',
color='primary')

Methods

|  |  |
|----|----|
| [jslink](#panel.widgets.Button.jslink)(target\[, code, args, bidirectional\]) | Links properties on the this Button to those on the target object in Javascript (JS) code. |
| [on_click](#panel.widgets.Button.on_click)(callback) | Register a callback to be executed when the Button is clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> [class="reference internal" title="panel.widgets.button.IconMixin"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`value`` ``=`` ``Event(allow_refs=True,`` ``default=False,`` ``label='Value')`
Toggles from False to True while the event is being processed.

`clicks`` ``=`` ``Integer(allow_refs=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Clicks')`
Number of clicks (can be listened to)

jslink(target: JSLinkTarget, code: dict\[str, str\] \| None = None, args: dict\[str, t.Any\] \| None = None, bidirectional: bool = False, **links: str) → Link
Links properties on the this Button to those on the target object in
Javascript (JS) code.

Supports two modes, either specify a mapping between the source and
target model properties as keywords or provide a dictionary of JS code
snippets which maps from the source parameter to a JS code snippet which
is executed when the property changes.

Parameters:
**target: panel.viewable.Viewable \| bokeh.model.Model \| holoviews.core.dimension.Dimensioned**
The target to link the value(s) to.

**code: dict**
Custom code which will be executed when the widget value changes.

**args: dict**
A mapping of objects to make available to the JS callback

**bidirectional: boolean**
Whether to link source and target bi-directionally. Default is False.

****links: dict\[str,str\]**
A mapping between properties on the source model and the target model
property to link it to.

Returns:
Link
The Link can be used unlink the widget and the target model.

on_click(callback: Callable\[\[param.parameterized.Event\], None \| Awaitable\[None\]\]) → param.parameterized.Watcher
Register a callback to be executed when the Button is clicked.

The callback is given an Event argument declaring the number of clicks

Parameters:
**callback:**
The function to run on click events. Must accept a positional Event
argument. Can be a sync or async function

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the button is clicked.

class panel.widgets.ButtonIcon(\*, clicks, toggle_duration, active_icon, icon, size, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ClickableIcon`,
`_ClickButton`,
`TooltipMixin`

The ButtonIcon widget facilitates event triggering upon button clicks.

This widget displays a default icon initially. Upon being clicked, an
active_icon appears for a specified toggle_duration.

For instance, the ButtonIcon can be effectively utilized to implement a
feature akin to ChatGPT’s copy-to-clipboard button.

The button incorporates a value attribute, which alternates between
False and True as the click event is processed.

Furthermore, it includes an clicks attribute, enabling subscription to
click events for further actions or monitoring.

Reference:
[https://panel.holoviz.org/reference/widgets/ButtonIcon.html](https://panel.holoviz.org/reference/widgets/ButtonIcon.html)

Example:

\>\>\> button_icon
=
pn.widgets.ButtonIcon(
...
icon='clipboard',
...
active_icon='check',
...
description='Copy',
...
toggle_duration=2000
... )

Methods

|  |  |
|----|----|
| [on_click](#panel.widgets.ButtonIcon.on_click)(callback) | Register a callback to be executed when the button is clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.icon._ClickableIcon`:
> active_icon, icon, size
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Toggles from False to True while the event is being processed.

`clicks`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Clicks')`
The number of times the button has been clicked.

`toggle_duration`` ``=`` ``Integer(default=75,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Toggle`` ``duration')`
The number of milliseconds the active_icon should be shown for and how
long the button should be disabled for.

on_click(callback: Callable\[\[param.parameterized.Event\], None\]) → param.parameterized.Watcher
Register a callback to be executed when the button is clicked.

The callback is given an Event argument declaring the number of clicks.

Parameters:
**callback: (Callable\[\[param.parameterized.Event\], None\])**
The function to run on click events. Must accept a positional Event
argument

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the MenuButton is clicked.

class panel.widgets.CheckBoxGroup(\*, inline, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_CheckGroupBase`

The CheckBoxGroup widget allows selecting between a list of options by
ticking the corresponding checkboxes.

It falls into the broad category of multi-option selection widgets that
provide a compatible API and include the MultiSelect, CrossSelector and
CheckButtonGroup widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/CheckBoxGroup.html](https://panel.holoviz.org/reference/widgets/CheckBoxGroup.html)

Example:

\>\>\>
CheckBoxGroup(
...
name='Fruits',
value=\['Apple',
'Pear'\],
options=\['Apple',
'Banana',
'Pear',
'Strawberry'\],
...
inline=True
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._CheckGroupBase`: value
>
>

`inline`` ``=`` ``Boolean(default=False,`` ``label='Inline')`
Whether the items be arrange vertically
(`False`) or horizontally in-line
(`True`).

class panel.widgets.CheckButtonGroup(\*, orientation, options, button_style, button_type, color, variant, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_CheckGroupBase`,
`_ButtonBase`,
`TooltipMixin`

The CheckButtonGroup widget allows selecting between a list of options
by toggling the corresponding buttons.

It falls into the broad category of multi-option selection widgets that
provide a compatible API and include the MultiSelect, CrossSelector and
CheckBoxGroup widgets.

Reference: [https://panel.holoviz.org/reference/widgets/CheckButtonGroup.html](https://panel.holoviz.org/reference/widgets/CheckButtonGroup.html)

Example:

\>\>\>
CheckButtonGroup(
...
name='Regression
Models',
value=\['Lasso',
'Ridge'\],
...
options=\['Lasso',
'Linear',
'Ridge',
'Polynomial'\]
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._CheckGroupBase`: value
>
>

`orientation`` ``=`` ``Selector(default='horizontal',`` ``label='Orientation',`` ``names={},`` ``objects=['horizontal',`` ``'vertical'])`
Button group orientation, either ‘horizontal’ (default) or ‘vertical’.

class panel.widgets.Checkbox(**params: Any)
Bases: `_BooleanWidget`

The Checkbox allows toggling a single condition between True/False
states by ticking a checkbox.

This widget is interchangeable with the Toggle widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Checkbox.html](https://panel.holoviz.org/reference/widgets/Checkbox.html)

Example:

\>\>\>
Checkbox(name='Works
with the tools you know and love',
value=True)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.input._BooleanWidget`: value
>
>

class panel.widgets.CodeEditor(\*, annotations, filename, indent, language, on_keyup, print_margin, readonly, soft_tabs, theme, value_input, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The CodeEditor widget allows displaying and editing code in the powerful
Ace editor.

Reference:
[https://panel.holoviz.org/reference/widgets/CodeEditor.html](https://panel.holoviz.org/reference/widgets/CodeEditor.html)

Example:

\>\>\>
CodeEditor(value=py_code,
language='python',
theme='monokai')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``String(default='',`` ``label='Value')`
State of the current code in the editor if on_keyup. Otherwise, only
upon loss of focus, i.e. clicking outside the editor, or pressing
\<Ctrl+Enter\> or \<Cmd+Enter\>.

`annotations`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Annotations')`
List of annotations to add to the editor.

`filename`` ``=`` ``String(default='',`` ``label='Filename')`
Filename from which to deduce language

`language`` ``=`` ``String(default='text',`` ``label='Language')`
Language of the editor

`indent`` ``=`` ``Integer(default=4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Indent')`
The default indent size.

`on_keyup`` ``=`` ``Boolean(default=True,`` ``label='On`` ``keyup')`
Whether to update the value on every key press or only upon loss of
focus / hotkeys.

`print_margin`` ``=`` ``Boolean(default=False,`` ``label='Print`` ``margin')`
Whether to show the a print margin.

`readonly`` ``=`` ``Boolean(default=False,`` ``label='Readonly')`
Define if editor content can be modified. Alias for disabled.

`soft_tabs`` ``=`` ``Boolean(default=False,`` ``label='Soft`` ``tabs')`
Whether to use spaces instead of tabs.

`theme`` ``=`` ``Selector(default='github_light_default',`` ``label='Theme',`` ``names={},`` ``objects=['ambiance',`` ``'chaos',`` ``'chrome',`` ``'cloud9_day',`` ``'cloud9_night',`` ``'clouds',`` ``'clouds_midnight',`` ``'cobalt',`` ``'crimson_editor',`` ``'dawn',`` ``'dracula',`` ``'dreamweaver',`` ``'eclipse',`` ``'github',`` ``'github_dark',`` ``'github_light_default',`` ``'gob',`` ``'gruvbox',`` ``'idle_fingers',`` ``'iplastic',`` ``'katzenmilch',`` ``'kr_theme',`` ``'kuroir',`` ``'merbivore',`` ``'merbivore_soft',`` ``'mono_industrial',`` ``'monokai',`` ``'nord_dark',`` ``'one_dark',`` ``'pastel_on_dark',`` ``'solarized_dark',`` ``'solarized_light',`` ``'sqlserver',`` ``'terminal',`` ``'textmate',`` ``'tomorrow',`` ``'tomorrow_night',`` ``'tomorrow_night_blue',`` ``'tomorrow_night_bright',`` ``'tomorrow_night_eighties',`` ``'twilight',`` ``'vibrant_ink',`` ``'xcode'])`
If no value is provided, it defaults to the current theme set by
pn.config.theme, as specified in the CodeEditor.THEME_CONFIGURATION
dictionary. If not defined there, it falls back to the default parameter
value.

`value_input`` ``=`` ``String(default='',`` ``label='Value`` ``input')`
State of the current code updated on every key press. Identical to value
if on_keyup.

class panel.widgets.ColorPicker(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The ColorPicker widget allows selecting a hexadecimal RGB color value
using the browser’s color-picking widget.

Reference:
[https://panel.holoviz.org/reference/widgets/ColorPicker.html](https://panel.holoviz.org/reference/widgets/ColorPicker.html)

Example:

\>\>\>
ColorPicker(name='Color',
value='#99ef78')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Value')`
The selected color

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=52,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.CompositeWidget(\*, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

A baseclass for widgets which are made up of two or more other widgets

Methods

|  |  |
|----|----|
| [select](#panel.widgets.CompositeWidget.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

class panel.widgets.CrossSelector(\*, definition_order, filter_fn, size, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
[MultiSelect](panel.widgets.select.md#panel.widgets.select.MultiSelect)

A composite widget which allows selecting from a list of items by moving
them between two lists. Supports filtering values by name to select them
in bulk.

Reference:
[https://panel.holoviz.org/reference/widgets/CrossSelector.html](https://panel.holoviz.org/reference/widgets/CrossSelector.html)

Example:

\>\>\>
CrossSelector(
...
name='Fruits',
value=\['Apple',
'Pear'\],
...
options=\['Apple',
'Banana',
'Pear',
'Strawberry'\]
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, description
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=200,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=600,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`size`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`filter_fn`` ``=`` ``Callable(label='Filter`` ``fn')`
The filter function applied when querying using the text fields,
defaults to re.search. Function is two arguments, the query or pattern
and the item label.

`definition_order`` ``=`` ``Integer(default=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Definition`` ``order')`
Whether to preserve definition order after filtering. Disable to allow
the order of selection to define the order of the selected list.

filter_fn(string, flags=0)
Scan through string looking for a match to the pattern, returning a
Match object, or None if no match was found.

class panel.widgets.DataFrame(value=None, **params)
Bases:
[BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable)

The DataFrame widget allows displaying and editing a pandas DataFrame.

Note that editing is not possible for multi-indexed DataFrames, in which
case you will need to reduce the DataFrame to a single index.

Also note that the DataFrame widget will eventually be replaced with the
Tabulator widget, and so new code should be written to use Tabulator
instead.

Reference:
[https://panel.holoviz.org/reference/widgets/DataFrame.html](https://panel.holoviz.org/reference/widgets/DataFrame.html)

Example:

\>\>\>
DataFrame(df,
name='DataFrame')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.tables.BaseTable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.tables.BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable):
> value, selection, aggregators, editables, editors, formatters,
> hierarchical, row_height, show_index, sorters, text_align, titles,
> widths
>
>

`auto_edit`` ``=`` ``Boolean(default=False,`` ``label='Auto`` ``edit')`
Whether clicking on a table cell automatically starts edit mode.

`autosize_mode`` ``=`` ``Selector(default='force_fit',`` ``label='Autosize`` ``mode',`` ``names={},`` ``objects=['none',`` ``'fit_columns',`` ``'fit_viewport',`` ``'force_fit'])`
Determines the column autosizing mode, as one of the following options:
`"fit_columns"` Compute column widths based on
cell contents while ensuring the table fits into the available viewport.
This results in no horizontal scrollbar showing up, but data can get
unreadable if there is not enough space available.
`"fit_viewport"` Adjust the viewport size after
computing column widths based on cell contents.
`"force_fit"` Fit columns into available space
dividing the table width across the columns equally (equivalent to
fit_columns=True). This results in no horizontal scrollbar showing up,
but data can get unreadable if there is not enough space available.
`"none"` Do not automatically compute column
widths.

`fit_columns`` ``=`` ``Boolean(allow_None=True,`` ``label='Fit`` ``columns')`
Whether columns should expand to the available width. This results in no
horizontal scrollbar showing up, but data can get unreadable if there is
no enough space available.

`frozen_columns`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Frozen`` ``columns')`
Integer indicating the number of columns to freeze. If set, the first N
columns will be frozen, which prevents them from scrolling out of frame.

`frozen_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Frozen`` ``rows')`
Integer indicating the number of rows to freeze. If set, the first N
rows will be frozen, which prevents them from scrolling out of frame; if
set to a negative value the last N rows will be frozen.

`reorderable`` ``=`` ``Boolean(default=True,`` ``label='Reorderable')`
Allows the reordering of a table’s columns. To reorder a column, click
and drag a table’s header to the desired location in the table. The
columns on either side will remain in their previous order.

`sortable`` ``=`` ``Boolean(default=True,`` ``label='Sortable')`
Allows to sort table’s contents. By default natural order is preserved.
To sort a column, click on its header. Clicking one more time changes
sort direction. Use Ctrl + click to return to natural order. Use Shift +
click to sort multiple columns simultaneously.

class panel.widgets.DatePicker(\*, description, disabled_dates, enabled_dates, end, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The DatePicker allows selecting a date value using a text box and a
date-picking utility.

Reference:
[https://panel.holoviz.org/reference/widgets/DatePicker.html](https://panel.holoviz.org/reference/widgets/DatePicker.html)

Example:

\>\>\>
DatePicker(
...
value=date(2025,1,1),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
name='Date'
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`start`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`disabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Disabled`` ``dates')`
Dates to make unavailable for selection; others will be available.

`enabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Enabled`` ``dates')`
Dates to make available for selection; others will be unavailable.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.DateRangePicker(\*, description, disabled_dates, enabled_dates, end, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The DateRangePicker allows selecting a date range using a text box and a
date-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DateRangePicker.html](https://panel.holoviz.org/reference/widgets/DateRangePicker.html)

Example:

\>\>\>
DateRangePicker(
...
value=(date(2025,1,1),
date(2025,1,5)),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
name='Date
range' ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The current value

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`start`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`disabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Disabled`` ``dates')`
Dates to make unavailable for selection; others will be available.

`enabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Enabled`` ``dates')`
Dates to make available for selection; others will be unavailable.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.DateRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SliderBase`

The DateRangeSlider widget allows selecting a date range using a slider
with two handles. Supports datetime.datetime, datetime.date and
np.datetime64 ranges.

Reference: [https://panel.holoviz.org/reference/widgets/DateRangeSlider.html](https://panel.holoviz.org/reference/widgets/DateRangeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DateRangeSlider(
...
value=(dt.datetime(2025,
1,
9),
dt.datetime(2025,
1,
16)),
...
start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
31), ...

step=2,
...
name="A
tuple of datetimes" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The selected range as a tuple of values. Updated when one of the handles
is dragged. Supports datetime.datetime, datetime.date, and np.datetime64
ranges.

`value_start`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``start',`` ``readonly=True)`
The lower value of the selected range.

`value_end`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``end',`` ``readonly=True)`
The upper value of the selected range.

`value_throttled`` ``=`` ``DateRange(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of values. Updated one of the handles is
released. Supports datetime.datetime, datetime.date and np.datetime64
ranges

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in days. Default is 1 day.

`format`` ``=`` ``String(allow_None=True,`` ``label='Format')`
Datetime format used for parsing and formatting the date.

class panel.widgets.DateSlider(\*, as_datetime, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SliderBase`

The DateSlider widget allows selecting a value within a set of bounds
using a slider. Supports datetime.datetime, datetime.date and
np.datetime64 values. The step size is fixed at 1 day.

Reference:
[https://panel.holoviz.org/reference/widgets/DateSlider.html](https://panel.holoviz.org/reference/widgets/DateSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DateSlider(
...
value=dt.datetime(2025,
1,
1), ...

start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
7), ...

name="A
datetime value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected date value of the slider. Updated when the slider handle is
dragged. Supports datetime.datetime, datetime.date or np.datetime64
types.

`value_throttled`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the slider handle is released.

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`as_datetime`` ``=`` ``Boolean(default=False,`` ``label='As`` ``datetime')`
Whether to store the date as a datetime.

`step`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step parameter in days.

`format`` ``=`` ``String(allow_None=True,`` ``label='Format')`
Datetime format used for parsing and formatting the date.

class panel.widgets.DatetimeInput(\*, end, format, start, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput)

The DatetimeInput allows specifying Python datetime like values using a
text input widget.

An optional type may be declared.

Reference:
[https://panel.holoviz.org/reference/widgets/DatetimeInput.html](https://panel.holoviz.org/reference/widgets/DatetimeInput.html)

Example:

\>\>\>
DatetimeInput(name='Datetime',
value=datetime(2019,
2,
8))

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal"
> title="panel.widgets.input.LiteralInput"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets. input .LiteralInput](panel.widgets.input.md#panel.widgets.input.LiteralInput):
> width, description, placeholder, serializer, type
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`format`` ``=`` ``String(default='%Y-%m-%d`` ``%H:%M:%S',`` ``label='Format')`
Datetime format used for parsing and formatting the datetime.

type
alias of `datetime`

class panel.widgets.DatetimePicker(\*, mode, allow_input, as_numpy_datetime64, description, disabled_dates, enable_seconds, enable_time, enabled_dates, end, military_time, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_DatetimePickerBase`

The DatetimePicker allows selecting selecting a datetime value using a
textbox and a datetime-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimePicker.html](https://panel.holoviz.org/reference/widgets/DatetimePicker.html)

Example:

\>\>\>
DatetimePicker(
...
value=datetime(2025,1,1,22,0),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
military_time=True,
name='Date
and time' ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._DatetimePickerBase`:
> width, allow_input, disabled_dates, enabled_dates, enable_time,
> enable_seconds, end, military_time, start, description,
> as_numpy_datetime64
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

`mode`` ``=`` ``String(constant=True,`` ``default='single',`` ``label='Mode')`
The mode of the datetime picker, which is always ‘single’ for this
widget.

class panel.widgets.DatetimeRangeInput(\*, end, format, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

The DatetimeRangeInput widget allows selecting a datetime range using
two DatetimeInput widgets, which return a tuple range.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangeInput.html](https://panel.holoviz.org/reference/widgets/DatetimeRangeInput.html)

Example:

\>\>\>
DatetimeRangeInput(
...
name='Datetime
Range', ...
value=(datetime(2017,
1,
1),
datetime(2018,
1,
10)),
...
start=datetime(2017,
1,
1),
end=datetime(2019,
1,
1), ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``Tuple(default=(None,`` ``None),`` ``label='Value',`` ``length=2)`
The current value

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`format`` ``=`` ``String(default='%Y-%m-%d`` ``%H:%M:%S',`` ``label='Format')`
Datetime format used for parsing and formatting the datetime.

class panel.widgets.DatetimeRangePicker(\*, mode, allow_input, as_numpy_datetime64, description, disabled_dates, enable_seconds, enable_time, enabled_dates, end, military_time, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_DatetimePickerBase`

The DatetimeRangePicker allows selecting selecting a datetime range
using a text box and a datetime-range-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangePicker.html](https://panel.holoviz.org/reference/widgets/DatetimeRangePicker.html)

Example:

\>\>\>
DatetimeRangePicker(
...
value=(datetime(2025,1,1,22,0),
datetime(2025,1,2,22,0)),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
military_time=True,
name='Datetime
Range' ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._DatetimePickerBase`:
> width, allow_input, disabled_dates, enabled_dates, enable_time,
> enable_seconds, end, military_time, start, description,
> as_numpy_datetime64
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The current value

`mode`` ``=`` ``String(constant=True,`` ``default='range',`` ``label='Mode')`
The mode of the datetime picker, which is always ‘range’ for this
widget.

class panel.widgets.DatetimeRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[DateRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DateRangeSlider)

The DatetimeRangeSlider widget allows selecting a datetime range using a
slider with two handles. Supports datetime.datetime and np.datetime64
ranges.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangeSlider.html](https://panel.holoviz.org/reference/widgets/DatetimeRangeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DatetimeRangeSlider(
...
value=(dt.datetime(2025,
1,
9),
dt.datetime(2025,
1,
16)),
...
start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
31), ...

step=10000,
...
name="A
tuple of datetimes" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.DateRangeSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.DateRangeSlider](panel.widgets.slider.md#panel.widgets.slider.DateRangeSlider):
> value, value_start, value_end, value_throttled, start, end, format
>
>

`step`` ``=`` ``Number(default=60000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in ms. Default is 1 min.

class panel.widgets.DatetimeSlider(\*, as_datetime, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[DateSlider](panel.widgets.slider.md#panel.widgets.slider.DateSlider)

The DatetimeSlider widget allows selecting a value within a set of
bounds using a slider. Supports datetime.date, datetime.datetime and
np.datetime64 values. The step size is fixed at 1 minute.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeSlider.html](https://panel.holoviz.org/reference/widgets/DatetimeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DatetimeSlider(
...
value=dt.datetime(2025,
1,
1), ...

start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
7), ...

name="A
datetime value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal" title="panel.widgets.slider.DateSlider"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.DateSlider](panel.widgets.slider.md#panel.widgets.slider.DateSlider):
> value, value_throttled, start, end, format
>
>

`as_datetime`` ``=`` ``Boolean(constant=True,`` ``default=True,`` ``label='As`` ``datetime',`` ``readonly=True)`
Whether to store the date as a datetime.

`step`` ``=`` ``Number(bounds=(1,`` ``None),`` ``default=60,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in seconds. Default is 1 minute, i.e 60 seconds.

class panel.widgets.Debugger(\*, \_number_of_errors, \_number_of_infos, \_number_of_warnings, formatter_args, level, logger_names, only_last, active_header_background, button_css_classes, collapsed, collapsible, header, header_background, header_color, header_css_classes, hide_header, title, title_css_classes, auto_scroll_limit, scroll_button_threshold, scroll_position, view_latest, scroll, objects, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [Card](panel.layout.card.md#panel.layout.card.Card)

A uneditable Card layout holding a terminal printing out logs from your
callbacks. By default, it will only print exceptions. If you want to add
your own log, use the panel.callbacks logger within your callbacks:
logger = logging.getLogger(‘panel.callbacks’)

Methods

|                        |     |
|------------------------|-----|
| **acknowledge_errors** |     |
| **update_log_counts**  |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, design, height, min_width, min_height, max_width,
> max_height, margin, styles, stylesheets, tags, width, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.layout.base.ListLike"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListLike](panel.layout.base.md#panel.layout.base.ListLike):
> objects
>
> [class="reference internal" title="panel.layout.base.ListPanel"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.ListPanel](panel.layout.base.md#panel.layout.base.ListPanel):
> scroll
>
> [class="reference internal" title="panel.layout.base.Column"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.base.Column](panel.layout.base.md#panel.layout.base.Column):
> auto_scroll_limit, scroll_button_threshold, scroll_position,
> view_latest
>
> [class="reference internal" title="panel.layout.card.Card"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.layout.card.Card](panel.layout.card.md#panel.layout.card.Card):
> css_classes, active_header_background, button_css_classes,
> collapsible, collapsed, header, header_background, header_color,
> header_css_classes, hide_header, title_css_classes, title
>
>

`_number_of_errors`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``errors')`
Number of logged errors since last acknowledged.

`_number_of_warnings`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``warnings')`
Number of logged warnings since last acknowledged.

`_number_of_infos`` ``=`` ``Integer(bounds=(0,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``number`` ``of`` ``infos')`
Number of logged information since last acknowledged.

`only_last`` ``=`` ``Boolean(default=True,`` ``label='Only`` ``last')`
Whether only the last stack is printed or the full.

`level`` ``=`` ``Integer(default=40,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Level')`
Logging level to print in the debugger terminal.

`formatter_args`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={'fmt':`` ``'%(asctime)s`` ``[%(name)s`` ``-`` ``%(levelname)s]:`` ``%(message)s'},`` ``label='Formatter`` ``args')`
Arguments to pass to the logging formatter. See the standard python
logging libraries.

`logger_names`` ``=`` ``List(bounds=(1,`` ``None),`` ``default=['panel'],`` ``item_type=<class`` ``'str'>,`` ``label='Logger`` ``names')`
Loggers which will be prompted in the debugger terminal.

class panel.widgets.Dial(\*, annulus_width, background, bounds, colors, default_color, end_angle, format, label_color, nan_format, needle_color, needle_width, start_angle, tick_size, title_size, unfilled_color, value_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)

A Dial represents a value in some range as a position on an annular
dial. It is similar to a Gauge but more minimal visually.

Reference:
[https://panel.holoviz.org/reference/indicators/Dial.html](https://panel.holoviz.org/reference/indicators/Dial.html)

Example:

\>\>\>
Dial(label='Speed',
value=79,
format="{value}
km/h",
bounds=(0,
200),
colors=\[(0.4,
'green'),
(1,
'red')\])

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the dial a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=250,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=250,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`annulus_width`` ``=`` ``Number(default=0.2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Annulus`` ``width')`
Width of the radial annulus as a fraction of the total.

`background`` ``=`` ``Parameter(allow_None=True,`` ``label='Background')`
Background color of the component.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the dial.

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Dial, specified as a list of tuples of the
fractional threshold and the color to switch to.

`default_color`` ``=`` ``String(default='lightblue',`` ``label='Default`` ``color')`
Color of the radial annulus if not color thresholds are supplied.

`end_angle`` ``=`` ``Number(default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End`` ``angle')`
Angle at which the dial ends.

`format`` ``=`` ``String(default='{value}%',`` ``label='Format')`
Formatting string for the value indicator and lower/upper bounds.

`label_color`` ``=`` ``String(default='black',`` ``label='Label`` ``color')`
Color for all extraneous labels.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`needle_color`` ``=`` ``String(default='black',`` ``label='Needle`` ``color')`
Color of the Dial needle.

`needle_width`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Needle`` ``width')`
Radial width of the needle.

`start_angle`` ``=`` ``Number(default=-205,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``angle')`
Angle at which the dial starts.

`tick_size`` ``=`` ``String(allow_None=True,`` ``label='Tick`` ``size')`
Font size of the Dial min/max labels.

`title_size`` ``=`` ``String(allow_None=True,`` ``label='Title`` ``size')`
Font size of the Dial title.

`unfilled_color`` ``=`` ``String(default='whitesmoke',`` ``label='Unfilled`` ``color')`
Color of the unfilled region of the Dial.

`value_size`` ``=`` ``String(allow_None=True,`` ``label='Value`` ``size')`
Font size of the Dial value label.

class panel.widgets.DiscretePlayer(\*, value_throttled, direction, interval, loop_policy, preview_duration, scale_buttons, show_loop_controls, show_value, step, value_align, visible_buttons, visible_loop_options, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase),
[SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase)

The DiscretePlayer provides controls to iterate through a list of
discrete options. The speed at which the widget plays is defined by the
interval (in milliseconds), but it is also possible to skip items using
the step parameter.

Reference: [https://panel.holoviz.org/reference/widgets/DiscretePlayer.html](https://panel.holoviz.org/reference/widgets/DiscretePlayer.html)

Example:

\>\>\>
DiscretePlayer(
...
name='Discrete
Player', ...
options=\[2,
4,
8,
16,
32,
64,
128\],
value=32,
...
loop_policy='loop',
...
value_align='start'
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> [class="reference internal" title="panel.widgets.player.PlayerBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.player.PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase):
> height, width, direction, loop_policy, preview_duration,
> show_loop_controls, step, value_align, scale_buttons, visible_buttons,
> visible_loop_options
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
Current player value

`interval`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Interval')`
Interval between updates

`show_value`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``value')`
Whether to show the widget value

`value_throttled`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='Value`` ``throttled')`
Current player value

class panel.widgets.DiscreteSlider(\*, formatter, options, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
`_SliderBase`

The DiscreteSlider widget allows selecting a value from a discrete list
or dictionary of values using a slider.

Reference: [https://panel.holoviz.org/reference/widgets/DiscreteSlider.html](https://panel.holoviz.org/reference/widgets/DiscreteSlider.html)

Example:

\>\>\>
DiscreteSlider(
...
value=0,
...
options=list(\[0,
1,
2,
4,
8,
16,
32,
64\]),
...
name="A
discrete value", ...
)

Attributes:
[labels](#panel.widgets.DiscreteSlider.labels)
The list of labels to display

[values](#panel.widgets.DiscreteSlider.values)
The list of option values

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The selected value of the slider. Updated when the handle is dragged.
Must be one of the options.

`value_throttled`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released.

`options`` ``=`` ``ClassSelector(class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``default=[],`` ``label='Options')`
A list or dictionary of valid options.

`formatter`` ``=`` ``String(default='%.3g',`` ``label='Formatter')`
A custom format string. Separate from format parameter since formatting
is applied in Python, not via the bokeh TickFormatter.

property labels
The list of labels to display

property values
The list of option values

class panel.widgets.EditableFloatSlider(\*, fixed_end, fixed_start, editable, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_EditableContinuousSlider`,
[FloatSlider](panel.widgets.slider.md#panel.widgets.slider.FloatSlider)

The EditableFloatSlider widget allows selecting selecting a numeric
floating-point value within a set of bounds using a slider and for more
precise control offers an editable number input box.

Reference: [https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html](https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html)

Example:

\>\>\>
EditableFloatSlider(
...
value=1.0,
start=0.0,
end=2.0,
step=0.25,
name="A
float value" ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
> href="panel.widgets.slider.html#panel.widgets.slider.ContinuousSlider"
> class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider:
> format
>
> [class="reference internal"
> title="panel.widgets.slider.FloatSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.FloatSlider](panel.widgets.slider.md#panel.widgets.slider.FloatSlider):
> value, start, end, step, value_throttled
>
> `panel.widgets.slider._EditableContinuousSlider`:
> editable, show_value
>
>

`fixed_start`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

class panel.widgets.EditableIntSlider(\*, fixed_end, fixed_start, editable, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_EditableContinuousSlider`,
[IntSlider](panel.widgets.slider.md#panel.widgets.slider.IntSlider)

The EditableIntSlider widget allows selecting selecting an integer value
within a set of bounds using a slider and for more precise control
offers an editable integer input box.

Reference: [https://panel.holoviz.org/reference/widgets/EditableIntSlider.html](https://panel.holoviz.org/reference/widgets/EditableIntSlider.html)

Example:

\>\>\>
EditableIntSlider(
...
value=2,
start=0,
end=5,
step=1,
name="An
integer value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
> href="panel.widgets.slider.html#panel.widgets.slider.ContinuousSlider"
> class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider:
> format
>
> [class="reference internal" title="panel.widgets.slider.IntSlider"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.IntSlider](panel.widgets.slider.md#panel.widgets.slider.IntSlider):
> value, start, end, step, value_throttled
>
> `panel.widgets.slider._EditableContinuousSlider`:
> editable, show_value
>
>

`fixed_start`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

class panel.widgets.EditableRangeSlider(\*, editable, end, fixed_end, fixed_start, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
`_SliderBase`

The EditableRangeSlider widget allows selecting a floating-point range
using a slider with two handles and for more precise control also offers
a set of number input boxes.

Reference: [https://panel.holoviz.org/reference/widgets/EditableRangeSlider.html](https://panel.holoviz.org/reference/widgets/EditableRangeSlider.html)

Example:

\>\>\>
EditableRangeSlider(
...
value=(1.0,
1.5),
start=0.0,
end=2.0,
step=0.25,
name="A
tuple of floats" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
>

`value`` ``=`` ``Range(default=(0,`` ``1),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
Current range value. Updated when a handle is dragged.

`show_value`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Show`` ``value',`` ``readonly=True)`
Whether to show the widget value.

`value_throttled`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2)`
The value of the slider. Updated when the handle is released.

`start`` ``=`` ``Number(default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Lower bound of the range.

`end`` ``=`` ``Number(default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Upper bound of the range.

`fixed_start`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
Slider and number input step.

`editable`` ``=`` ``Tuple(default=(True,`` ``True),`` ``label='Editable',`` ``length=2)`
Whether the lower and upper values are editable.

`format`` ``=`` ``ClassSelector(class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.formatters.TickFormatter'>),`` ``default='0.0[0000]',`` ``label='Format')`
Allows defining a custom format string or bokeh TickFormatter.

class panel.widgets.FileDownload(file=None, **params)
Bases:
[IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)

The FileDownload widget allows a user to download a file.

It works either by sending the file data to the browser on
initialization ([\`](#id1)embed\`=True), or when the button is
clicked.

Reference:
[https://panel.holoviz.org/reference/widgets/FileDownload.html](https://panel.holoviz.org/reference/widgets/FileDownload.html)

Example:

\>\>\>
FileDownload(file='IntroductionToPanel.ipynb',
filename='intro.ipynb')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.button.IconMixin"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin):
> icon, icon_size
>
>

`label`` ``=`` ``String(default='Download`` ``file',`` ``label='Label')`
The label of the download button

`auto`` ``=`` ``Boolean(default=True,`` ``label='Auto')`
Whether to download on the initial click or allow for right-click save
as.

`button_type`` ``=`` ``Selector(default='default',`` ``label='Button`` ``type',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light'])`
A button theme; should be one of ‘default’ (white), ‘primary’ (blue),
‘success’ (green), ‘info’ (yellow), ‘light’ (light), or ‘danger’ (red).
The same value is exposed as `color`.

`button_style`` ``=`` ``Selector(default='solid',`` ``label='Button`` ``style',`` ``names={},`` ``objects=['solid',`` ``'outline'])`
A button style to switch between ‘solid’, ‘outline’. The same value is
exposed as `variant`.

`color`` ``=`` ``Selector(default='default',`` ``label='Color',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light'])`
Semantic color of the button; alias for
`button_type`.

`variant`` ``=`` ``Selector(default='solid',`` ``label='Variant',`` ``names={},`` ``objects=['solid',`` ``'outline'])`
Visual variant of the button; alias for
`button_style` (‘solid’ or ‘outline’).

`callback`` ``=`` ``Callable(allow_None=True,`` ``label='Callback')`
A callable that returns the file path or file-like object.

`data`` ``=`` ``String(allow_None=True,`` ``label='Data')`
The data being transferred.

`embed`` ``=`` ``Boolean(default=False,`` ``label='Embed')`
Whether to embed the file on initialization.

`file`` ``=`` ``Parameter(allow_None=True,`` ``label='File')`
The file, Path, file-like object or file contents to transfer. If the
file is not pointing to a file on disk a filename must also be provided.

`filename`` ``=`` ``String(allow_None=True,`` ``label='Filename')`
A filename which will also be the default name when downloading the
file.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

`_clicks`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``clicks')`
Internal counter for button clicks.

`_transfers`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``transfers')`

class panel.widgets.FileDropper(\*, accepted_filetypes, chunk_size, layout, max_file_size, max_files, max_total_file_size, mime_type, multiple, previews, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The FileDropper allows the user to upload one or more files to the
server.

It is similar to the FileInput widget but additionally adds support for
chunked uploads, making it possible to upload large files. The UI also
supports previews for image files. Unlike FileInput the uploaded files
are stored as dictionary of bytes object indexed by the filename.

Reference:
[https://panel.holoviz.org/reference/widgets/FileDropper.html](https://panel.holoviz.org/reference/widgets/FileDropper.html)

Example:

\>\>\>
FileDropper(accepted_filetypes=\['image/\*'\],
multiple=True)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Value')`
A dictionary containing the uploaded file(s) as bytes or string objects
indexed by the filename. Files that have a text/\* mimetype will
automatically be decoded as utf-8.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`accepted_filetypes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Accepted`` ``filetypes')`
List of accepted file types. Can be mime types, file extensions or wild
cards.For instance \[‘image/[\*](#id3)’\] will accept all images.
\[‘.png’, ‘image/jpeg’\] will only accepts PNGs and JPEGs.

`chunk_size`` ``=`` ``Integer(default=10000000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Chunk`` ``size')`
Size in bytes per chunk transferred across the WebSocket.

`layout`` ``=`` ``Selector(label='Layout',`` ``names={},`` ``objects=['circle',`` ``'compact',`` ``'integrated'])`
Compact mode removes padding. Integrated mode renders FilePond as part
of a bigger element. Circle mode keeps FilePond’s per-file action
buttons and upload progress indicator inside the circular drop area.

`max_file_size`` ``=`` ``String(allow_None=True,`` ``label='Max`` ``file`` ``size')`
Maximum size of a file as a string with units given in KB or MB, e.g.
5MB or 750KB.

`max_files`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``files')`
Maximum number of files that can be uploaded if multiple=True.

`max_total_file_size`` ``=`` ``String(allow_None=True,`` ``label='Max`` ``total`` ``file`` ``size')`
Maximum size of all uploaded files, as a string with units given in KB
or MB, e.g. 5MB or 750KB.

`mime_type`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Mime`` ``type')`
A dictionary containing the mimetypes for each of the uploaded files
indexed by their filename.

`multiple`` ``=`` ``Boolean(default=False,`` ``label='Multiple')`
Whether to allow uploading multiple files.

`previews`` ``=`` ``ListSelector(default=['image',`` ``'pdf'],`` ``label='Previews',`` ``names={},`` ``objects=['image',`` ``'pdf'])`
List of previews to enable in the FileDropper. The following previews
are available: - image: Adds support for image previews. - pdf: Adds
support for PDF previews.

class panel.widgets.FileInput(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The FileInput allows the user to upload one or more files to the server.

It makes the filename, MIME type and (bytes) content available in
Python.

Please note

- you can in fact *drag and drop* files onto the FileInput.

- you easily save the files using the save method.

Reference:
[https://panel.holoviz.org/reference/widgets/FileInput.html](https://panel.holoviz.org/reference/widgets/FileInput.html)

Example:

\>\>\>
FileInput(accept='.png,.jpeg',
multiple=True)

Methods

|  |  |
|----|----|
| [clear](#panel.widgets.FileInput.clear)() | Clear the file(s) in the FileInput widget |
| [save](#panel.widgets.FileInput.save)(filename) | Saves the uploaded FileInput data object(s) to file(s) or BytesIO object(s). |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The uploaded file(s) stored as a single bytes object if multiple is
False or a list of bytes otherwise.

`accept`` ``=`` ``String(allow_None=True,`` ``label='Accept')`
A comma separated string of all extension types that should be
supported.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component rendered as a
tooltip icon.

`directory`` ``=`` ``Boolean(default=False,`` ``label='Directory')`
Whether to allow selection of directories instead of files. The filename
will be relative paths to the uploaded directory. .. note:: When a
directory is uploaded it will give add a confirmation pop up. The
confirmation pop up cannot be disabled, as this is a security feature in
the browser. .. note:: The accept parameter only works with file
extension. When using accept with directory, the number of files
reported will be the total amount of files, not the filtered.

`filename`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'list'>),`` ``label='Filename')`
Name of the uploaded file(s).

`mime_type`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'list'>),`` ``label='Mime`` ``type')`
Mimetype of the uploaded file(s).

`multiple`` ``=`` ``Boolean(default=False,`` ``label='Multiple')`
Whether to allow uploading multiple files. If enabled value parameter
will return a list.

clear()
Clear the file(s) in the FileInput widget

save(filename)
Saves the uploaded FileInput data object(s) to file(s) or BytesIO
object(s).

Parameters:
**filename (str or list\[str\]): File path or file-like object**

class panel.widgets.FileSelector(directory: t.AnyStr \| os.PathLike \| None = None, fs: AbstractFileSystem \| None = None, **params)
Bases: [BaseFileNavigator](panel.widgets.file_selector.md#panel.widgets.file_selector.BaseFileNavigator)

The FileSelector widget allows browsing the filesystem on the server and
selecting one or more files in a directory.

Reference:
[https://panel.holoviz.org/reference/widgets/FileSelector.html](https://panel.holoviz.org/reference/widgets/FileSelector.html)

Example:

\>\>\>
FileSelector(directory='~',
file_pattern='\*.png')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> href="panel.widgets.file_selector.html#panel.widgets.file_selector.BaseFileSelector"
> class="reference internal"
> title="panel.widgets.file_selector.BaseFileSelector"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.file_selector.BaseFileSelector:
> directory, file_pattern, only_files, refresh_period, root_directory,
> value
>
>

`show_hidden`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``hidden')`
Whether to show hidden files and directories (starting with a period).

`size`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of options shown at once (note this is the only way to
control the height of this widget)

class panel.widgets.FloatInput(\*, step, value_throttled, page_step_multiplier, wheel_wait, mode, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`,
`_FloatInputBase`

The FloatInput allows selecting a floating point value using a spinbox.

It behaves like a slider except that the lower and upper bounds are
optional and a specific value can be entered. The value can be changed
using the keyboard (up, down, page up, page down), mouse wheel and arrow
buttons.

Reference:
[https://panel.holoviz.org/reference/widgets/FloatInput.html](https://panel.holoviz.org/reference/widgets/FloatInput.html)

Example:

\>\>\>
FloatInput(name='Value',
value=5.,
step=1e-1,
start=0,
end=10)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> description, format
>
> `panel.widgets.input._FloatInputBase`: value,
> start, end, mode
>
> `panel.widgets.input._SpinnerBase`: width,
> page_step_multiplier, wheel_wait
>
>

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder when the value is empty.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Number(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The current value. Updates only on \<enter\> or when the widget looses
focus.

class panel.widgets.FloatSlider(\*, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ContinuousSlider](panel.widgets.slider.md#panel.widgets.slider.ContinuousSlider)

The FloatSlider widget allows selecting a floating-point value within a
set of bounds using a slider.

Reference:
[https://panel.holoviz.org/reference/widgets/FloatSlider.html](https://panel.holoviz.org/reference/widgets/FloatSlider.html)

Example:

\>\>\>
FloatSlider(value=0.5,
start=0.0,
end=1.0,
step=0.1,
name="Float
value")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> href="panel.widgets.slider.html#panel.widgets.slider.ContinuousSlider"
> class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider:
> format
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected floating-point value of the slider. Updated when the handle
is dragged.

`start`` ``=`` ``Number(default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Number(default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Number(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released.

class panel.widgets.Gauge(\*, annulus_width, bounds, colors, custom_opts, end_angle, format, num_splits, show_labels, show_ticks, start_angle, title_size, tooltip_format, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)

A Gauge represents a value in some range as a position on speedometer or
gauge. It is similar to a Dial but visually a lot busier. Requires the
ECharts extension to be loaded.

Reference:
[https://panel.holoviz.org/reference/indicators/Gauge.html](https://panel.holoviz.org/reference/indicators/Gauge.html)

Example:

\>\>\>
pn.extension('echarts')
\>\>\>
Gauge(label='Speed',
value=79,
bounds=(0,
200),
colors=\[(0.4,
'green'),
(1,
'red')\])

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the gauge a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`annulus_width`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Annulus`` ``width')`
Width of the gauge annulus.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the dial.

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Gauge, specified as a list of tuples of the
fractional threshold and the color to switch to.

`custom_opts`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Custom`` ``opts')`
Additional options to pass to the ECharts Gauge definition.

`end_angle`` ``=`` ``Number(default=-45,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End`` ``angle')`
Angle at which the gauge ends.

`format`` ``=`` ``String(default='{value}%',`` ``label='Format')`
Formatting string for the value indicator.

`num_splits`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Num`` ``splits')`
Number of splits along the gauge.

`show_ticks`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``ticks')`
Whether to show ticks along the dials.

`show_labels`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``labels')`
Whether to show tick labels along the dials.

`start_angle`` ``=`` ``Number(default=225,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``angle')`
Angle at which the gauge starts.

`tooltip_format`` ``=`` ``String(default='{b}`` ``:`` ``{c}%',`` ``label='Tooltip`` ``format')`
Formatting string for the hover tooltip.

`title_size`` ``=`` ``Integer(allow_None=True,`` ``default=18,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Title`` ``size')`
Size of title font.

class panel.widgets.Grammar(\*, src, uri, weight, name)
Bases: `Parameterized`

A set of words or patterns of words that we want the speech recognition
service to recognize

For example

grammar = Grammar(
src=’#JSGF V1.0; grammar colors; public \<color\> = aqua \| azure \|
beige;’, weight=0.7

)

Wraps the HTML SpeechGrammar API. See
[https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammar](https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammar)

Methods

|  |  |
|----|----|
| [serialize](#panel.widgets.Grammar.serialize)() | Returns the grammar as dict |

**Parameter Definitions**

------------------------------------------------------------------------

`src`` ``=`` ``String(default='',`` ``label='Src')`
A set of words or patterns of words that we want the recognition service
to recognize. Defined using JSpeech Grammar Format. See
[https://www.w3.org/TR/jsgf/](https://www.w3.org/TR/jsgf/).

`uri`` ``=`` ``String(default='',`` ``label='Uri')`
An uri pointing to the definition. If src is available it will be used.
Otherwise uri. The uri will be loaded on the client side only.

`weight`` ``=`` ``Number(bounds=(0.0,`` ``1.0),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Weight',`` ``step=0.01)`
The weight of the grammar. A number in the range 0–1. Default is 1.

serialize()
Returns the grammar as dict

class panel.widgets.GrammarList(iterable=(), /)
Bases: `list`

A list of Grammar objects containing words or patterns of words that we
want the recognition service to recognize.

Example:

grammar = ‘#JSGF V1.0; grammar colors; public \<color\> = aqua \| azure
\| beige \| bisque ;’ grammar_list = GrammarList()
grammar_list.add_from_string(grammar, 1)

Wraps the HTML 5 SpeechGrammarList API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammarList](https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammarList)

Methods

|  |  |
|----|----|
| [serialize](#panel.widgets.GrammarList.serialize)() | Returns a list of serialized grammars |

add_from_string(src, weight=1.0)
Takes a src and weight and adds it to the GrammarList as a new Grammar
object. The new Grammar object is returned.

add_from_uri(uri, weight=1.0)
Takes a grammar present at a specific uri, and adds it to the
GrammarList as a new Grammar object. The new Grammar object is returned.

serialize()
Returns a list of serialized grammars

class panel.widgets.IntInput(\*, step, value_throttled, page_step_multiplier, wheel_wait, mode, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`,
`_IntInputBase`

The IntInput allows selecting an integer value using a spinbox.

It behaves like a slider except that lower and upper bounds are optional
and a specific value can be entered. The value can be changed using the
keyboard (up, down, page up, page down), mouse wheel and arrow buttons.

Reference:
[https://panel.holoviz.org/reference/widgets/IntInput.html](https://panel.holoviz.org/reference/widgets/IntInput.html)

Example:

\>\>\>
IntInput(name='Value',
value=100,
start=0,
end=1000,
step=10)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> description, format
>
> `panel.widgets.input._IntInputBase`: value,
> start, end, mode
>
> `panel.widgets.input._SpinnerBase`: width,
> placeholder, page_step_multiplier, wheel_wait
>
>

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Integer(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The current value. Updates only on \<enter\> or when the widget looses
focus.

class panel.widgets.IntRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[RangeSlider](panel.widgets.slider.md#panel.widgets.slider.RangeSlider)

The IntRangeSlider widget allows selecting an integer range using a
slider with two handles.

Reference: [https://panel.holoviz.org/reference/widgets/IntRangeSlider.html](https://panel.holoviz.org/reference/widgets/IntRangeSlider.html)

Example:

\>\>\>
IntRangeSlider(
...
value=(2,
4),
start=0,
end=10,
step=2,
name="A
tuple of integers" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.RangeSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.RangeSlider](panel.widgets.slider.md#panel.widgets.slider.RangeSlider):
> value, value_start, value_end, value_throttled, format
>
>

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

class panel.widgets.IntSlider(\*, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ContinuousSlider](panel.widgets.slider.md#panel.widgets.slider.ContinuousSlider)

The IntSlider widget allows selecting an integer value within a set of
bounds using a slider.

Reference:
[https://panel.holoviz.org/reference/widgets/IntSlider.html](https://panel.holoviz.org/reference/widgets/IntSlider.html)

Example:

\>\>\>
IntSlider(value=5,
start=0,
end=10,
step=1,
name="Integer
Value")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> href="panel.widgets.slider.html#panel.widgets.slider.ContinuousSlider"
> class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider:
> format
>
>

`value`` ``=`` ``Integer(allow_None=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected integer value of the slider. Updated when the handle is
dragged.

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Integer(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released

class panel.widgets.JSONEditor(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The JSONEditor provides a visual editor for JSON-serializable
datastructures, e.g. Python dictionaries and lists, with functionality
for different editing modes, inserting objects and validation using JSON
Schema.

Reference:
[https://panel.holoviz.org/reference/widgets/JSONEditor.html](https://panel.holoviz.org/reference/widgets/JSONEditor.html)

Example:

\>\>\>
JSONEditor(value={
...  'dict'
:
{'key':
'value'},
...  'float'
:
3.14,
...  'int'
:
1, ...
 'list' :
\[1,
2,
3\], ...
 'string':
'A string',
... },
mode='code')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``Parameter(default={},`` ``label='Value')`
JSON data to be edited.

`menu`` ``=`` ``Boolean(default=True,`` ``label='Menu')`
Adds main menu bar - Contains format, sort, transform, search etc.
functionality. true by default. Applicable in all types of mode.

`mode`` ``=`` ``Selector(default='tree',`` ``label='Mode',`` ``names={},`` ``objects=['tree',`` ``'view',`` ``'form',`` ``'text',`` ``'preview'])`
Sets the editor mode. In ‘view’ mode, the data and datastructure is
read-only. In ‘form’ mode, only the value can be changed, the data
structure is read-only. Mode ‘code’ requires the Ace editor to be loaded
on the page. Mode ‘text’ shows the data as plain text. The ‘preview’
mode can handle large JSON documents up to 500 MiB. It shows a preview
of the data, and allows to transform, sort, filter, format, or compact
the data.

`search`` ``=`` ``Boolean(default=True,`` ``label='Search')`
Enables a search box in the upper right corner of the JSONEditor. true
by default. Only applicable when mode is ‘tree’, ‘view’, or ‘form’.

`selection`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Selection')`
Current selection.

`schema`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Schema')`
Validate the JSON object against a JSON schema. A JSON schema describes
the structure that a JSON object must have, like required properties or
the type that a value must have. See [http://json-schema.org/](http://json-schema.org/) for more
information.

`templates`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Templates')`
Array of templates that will appear in the context menu, Each template
is a json object precreated that can be added as a object value to any
node in your document.

class panel.widgets.LinearGauge(\*, bounds, colors, default_color, format, horizontal, nan_format, needle_color, show_boundaries, tick_size, title_size, unfilled_color, value_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)

A LinearGauge represents a value in some range as a position on an
linear scale. It is similar to a Dial/Gauge but visually more compact.

Reference: [https://panel.holoviz.org/reference/indicators/LinearGauge.html](https://panel.holoviz.org/reference/indicators/LinearGauge.html)

Example:

\>\>\>
LinearGauge(value=30,
default_color='red',
bounds=(0,
100))

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the dial a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=125,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the gauge.

`default_color`` ``=`` ``String(default='lightblue',`` ``label='Default`` ``color')`
Color of the radial annulus if not color thresholds are supplied.

`colors`` ``=`` ``Parameter(allow_None=True,`` ``label='Colors')`
Color thresholds for the gauge, specified as a list of tuples of the
fractional threshold and the color to switch to.

`format`` ``=`` ``String(default='{value:.2f}%',`` ``label='Format')`
Formatting string for the value indicator and lower/upper bounds.

`horizontal`` ``=`` ``Boolean(default=False,`` ``label='Horizontal')`
Whether to display the linear gauge horizontally.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`needle_color`` ``=`` ``String(default='black',`` ``label='Needle`` ``color')`
Color of the gauge needle.

`show_boundaries`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``boundaries')`
Whether to show the boundaries between colored regions.

`unfilled_color`` ``=`` ``String(default='whitesmoke',`` ``label='Unfilled`` ``color')`
Color of the unfilled region of the LinearGauge.

`title_size`` ``=`` ``String(allow_None=True,`` ``label='Title`` ``size')`
Font size of the gauge title.

`tick_size`` ``=`` ``String(allow_None=True,`` ``label='Tick`` ``size')`
Font size of the gauge tick labels.

`value_size`` ``=`` ``String(allow_None=True,`` ``label='Value`` ``size')`
Font size of the gauge value label.

class panel.widgets.LiteralInput(\*, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The LiteralInput allows declaring Python literals using a text input
widget.

A *literal* is some specific primitive value of type str , int, float,
bool etc or a dict, list, tuple, set etc of primitive values.

Optionally the literal type may be declared.

Reference:
[https://panel.holoviz.org/reference/widgets/LiteralInput.html](https://panel.holoviz.org/reference/widgets/LiteralInput.html)

Example:

\>\>\>
LiteralInput(name='Dictionary',
value={'key':
\[1,
2,
3\]},
type=dict)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder for empty input field.

`serializer`` ``=`` ``Selector(default='ast',`` ``label='Serializer',`` ``names={},`` ``objects=['ast',`` ``'json'])`
The serialization (and deserialization) method to use. ‘ast’ uses
ast.literal_eval and ‘json’ uses json.loads and json.dumps.

`type`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'type'>,`` ``<class`` ``'tuple'>),`` ``label='Type')`
A Python literal type (e.g. list, dict, set, int, float, bool, str).

class panel.widgets.LoadingSpinner(\*, bgcolor, color, size, throttle, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [BooleanIndicator](panel.widgets.indicators.md#panel.widgets.indicators.BooleanIndicator)

The LoadingSpinner is a boolean indicator providing a visual
representation of the loading status.

If the value is set to True the spinner will rotate while setting it to
False will disable the rotating segment.

Reference: [https://panel.holoviz.org/reference/indicators/LoadingSpinner.html](https://panel.holoviz.org/reference/indicators/LoadingSpinner.html)

Example:

\>\>\>
LoadingSpinner(value=True,
color='primary',
bgcolor='light',
width=100,
height=100)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> href="panel.widgets.indicators.html#panel.widgets.indicators.BooleanIndicator"
> class="reference internal"
> title="panel.widgets.indicators.BooleanIndicator"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.BooleanIndicator:
> throttle
>
>

`value`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Value')`
Whether the indicator is active or not.

`bgcolor`` ``=`` ``Selector(allow_refs=True,`` ``default='light',`` ``label='Bgcolor',`` ``names={},`` ``objects=['dark',`` ``'light'])`
The color of spinner background segment, either ‘light’ or ‘dark’.

`color`` ``=`` ``Selector(allow_refs=True,`` ``default='dark',`` ``label='Color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the spinning segment, one of ‘primary’, ‘secondary’,
‘success’, ‘info’, ‘warn’, ‘danger’, ‘light’, ‘dark’.

`size`` ``=`` ``Integer(allow_refs=True,`` ``default=125,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
Size of the spinner in pixels.

class panel.widgets.MenuButton(\*, clicked, items, split, button_style, button_type, color, variant, icon, icon_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_ButtonBase`,
`_ClickButton`,
[IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)

The MenuButton widget allows specifying a list of menu items to select
from triggering events when the button is clicked.

Unlike other widgets, it does not have a value parameter. Instead it has
a clicked parameter that can be watched to trigger events and which
reports the last clicked menu item.

Reference:
[https://panel.holoviz.org/reference/widgets/MenuButton.html](https://panel.holoviz.org/reference/widgets/MenuButton.html)

Example:

\>\>\> menu_items
=
\[('Option
A',
'a'),
('Option
B',
'b'),
None,
('Option
C',
'c')\]
\>\>\>
MenuButton(name='Dropdown',
items=menu_items,
color='primary')

Methods

|  |  |
|----|----|
| [on_click](#panel.widgets.MenuButton.on_click)(callback) | Register a callback to be executed when the button is clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.button.IconMixin"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`clicked`` ``=`` ``String(allow_None=True,`` ``label='Clicked')`
Last menu item that was clicked.

`items`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=(<class`` ``'str'>,`` ``<class`` ``'tuple'>,`` ``<class`` ``'NoneType'>),`` ``label='Items')`
Menu items in the dropdown. Allows strings, tuples of the form (title,
value) or Nones to separate groups of items.

`split`` ``=`` ``Boolean(default=False,`` ``label='Split')`
Whether to add separate dropdown area to button.

on_click(callback: Callable\[\[param.parameterized.Event\], None\]) → param.parameterized.Watcher
Register a callback to be executed when the button is clicked.

The callback is given an Event argument declaring the number of clicks

Parameters:
**callback: (Callable\[\[param.parameterized.Event\], None\])**
The function to run on click events. Must accept a positional Event
argument

Returns:
watcher: param.Parameterized.Watcher
A Watcher that executes the callback when the MenuButton is clicked.

class panel.widgets.MultiChoice(\*, delete_button, max_items, option_limit, placeholder, search_option_limit, solid, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_MultiSelectBase`

The MultiChoice widget allows selecting multiple values from a list of
options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the MultiSelect,
CrossSelector, CheckBoxGroup and CheckButtonGroup widgets.

The MultiChoice widget provides a much more compact UI than MultiSelect.

Reference:
[https://panel.holoviz.org/reference/widgets/MultiChoice.html](https://panel.holoviz.org/reference/widgets/MultiChoice.html)

Example:

\>\>\>
MultiChoice(
...
name='Favourites',
value=\['Panel',
'hvPlot'\],
...
options=\['Panel',
'hvPlot',
'HoloViews',
'GeoViews',
'Datashader',
'Param',
'Colorcet'\],
...
max_items=2
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, description
>
>

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`delete_button`` ``=`` ``Boolean(default=True,`` ``label='Delete`` ``button')`
Whether to display a button to delete a selected option.

`max_items`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``items')`
Maximum number of options that can be selected.

`option_limit`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Option`` ``limit')`
Maximum number of options to display at once.

`search_option_limit`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Search`` ``option`` ``limit')`
Maximum number of options to display at once if search string is
entered.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
String displayed when no selection has been made.

`solid`` ``=`` ``Boolean(default=True,`` ``label='Solid')`
Whether to display widget with solid or light style.

class panel.widgets.MultiSelect(\*, size, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_MultiSelectBase`

The MultiSelect widget allows selecting multiple values from a list of
options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the\`CrossSelector\`,
CheckBoxGroup and CheckButtonGroup widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/MultiSelect.html](https://panel.holoviz.org/reference/widgets/MultiSelect.html)

Example:

\>\>\>
MultiSelect(
...
name='Frameworks',
value=\['Bokeh',
'Panel'\],
...
options=\['Bokeh',
'Dash',
'Panel',
'Streamlit',
'Voila'\],
size=8
... )

Methods

|  |  |
|----|----|
| [on_double_click](#panel.widgets.MultiSelect.on_double_click)(callback) | Register a callback to be executed when a MultiSelect option is double-clicked. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, width, description
>
>

`size`` ``=`` ``Integer(allow_refs=True,`` ``default=4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of items displayed at once (i.e. determines the widget
height).

on_double_click(callback: Callable\[\[param.parameterized.Event\], None \| Awaitable\[None\]\]) → None
Register a callback to be executed when a MultiSelect option is
double-clicked.

The callback is given an DoubleClickEvent argument

Parameters:
**callback:**
The function to run on click events. Must accept a positional Event
argument. Can be a sync or async function

class panel.widgets.NestedSelect(\*, \_levels, \_max_depth, \_widgets, layout, levels, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

The NestedSelect widget is composed of multiple widgets, where
subsequent select options depend on the parent’s value.

Reference:
[https://panel.holoviz.org/reference/widgets/NestedSelect.html](https://panel.holoviz.org/reference/widgets/NestedSelect.html)

Example:

\>\>\>
NestedSelect(
...
options={
...
"gfs":
{"tmp":
\[1000,
500\],
"pcp":
\[1000\]},
...
"name":
{"tmp":
\[1000,
925,
850,
700,
500\],
"pcp":
\[1000\]},
...  },
...
levels=\["model",
"var",
"level"\],
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width
>
>

`value`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Value')`
The value from all the Select widgets; the keys are the levels names. If
no levels names are specified, the keys are the levels indices.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the widget is disabled.

`layout`` ``=`` ``Parameter(default=<class`` ``'panel.layout.base.Column'>,`` ``label='Layout')`
The layout type of the widgets. If a dictionary, a “type” key can be
provided, to specify the layout type of the widgets, and any additional
keyword arguments will be used to instantiate the layout.

`levels`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Levels')`
Either a list of strings or a list of dictionaries. If a list of
strings, the strings are used as the names of the levels. If a list of
dictionaries, each dictionary may have a “name” key, which is used as
the name of the level, a “type” key, which is used as the type of
widget, and any corresponding widget keyword arguments; otherwise, will
inherit layoutable keyword arguments from the NestedSelect itself, e.g.
width, height, and sizing_mode. Must be specified if options is
callable.

`options`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'list'>,`` ``<class`` ``'dict'>,`` ``<class`` ``'function'>),`` ``label='Options')`
The options to select from. The options may be nested dictionaries,
lists, or callables that return those types. If callables are used, the
callables must accept level and value keyword arguments, where level is
the level that updated and value is a dictionary of the current values,
containing keys up to the level that was updated.

`_widgets`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.widgets.base.WidgetBase'>,`` ``label='`` ``widgets')`
The nested select widgets.

`_max_depth`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``max`` ``depth')`
The number of levels of the nested select widgets.

`_levels`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='`` ``levels')`
The internal rep of levels to prevent overwriting user provided levels.

layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

class panel.widgets.Number(\*, colors, default_color, font_size, format, nan_format, title_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)

The Number indicator renders the value as text optionally colored
according to the colors thresholds.

Reference:
[https://panel.holoviz.org/reference/indicators/Number.html](https://panel.holoviz.org/reference/indicators/Number.html)

Example:

\>\>\>
Number(label='Rate',
value=72,
format='{value}%',
colors=\[(80,
'green'),
(100,
'red')\]

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> href="panel.widgets.indicators.html#panel.widgets.indicators.ValueIndicator"
> class="reference internal"
> title="panel.widgets.indicators.ValueIndicator"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.ValueIndicator:
> value
>
>

`default_color`` ``=`` ``String(default='currentcolor',`` ``label='Default`` ``color')`
The color of the Number indicator if no colors are provided

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Number indicator, specified as a tuple of the
absolute thresholds and the color to switch to.

`format`` ``=`` ``String(default='{value}',`` ``label='Format')`
A formatter string which accepts a {value}.

`font_size`` ``=`` ``String(default='54pt',`` ``label='Font`` ``size')`
The size of number itself.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`title_size`` ``=`` ``String(default='18pt',`` ``label='Title`` ``size')`
The size of the title given by the label.

class panel.widgets.NumberInput(\*, page_step_multiplier, wheel_wait, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> value, description, format, start, end
>
> `panel.widgets.input._SpinnerBase`: width,
> placeholder, page_step_multiplier, wheel_wait
>
>

class panel.widgets.PasswordInput(**params: Any)
Bases: `_TextInputBase`

The PasswordInput allows entering any string using an obfuscated text
input box.

Reference:
[https://panel.holoviz.org/reference/widgets/PasswordInput.html](https://panel.holoviz.org/reference/widgets/PasswordInput.html)

Example:

\>\>\>
PasswordInput(
...
name='Password',
placeholder='Enter
your password here...' ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

class panel.widgets.Player(\*, end, start, value_throttled, direction, interval, loop_policy, preview_duration, scale_buttons, show_loop_controls, show_value, step, value_align, visible_buttons, visible_loop_options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase)

The Player provides controls to play and skip through a number of frames
defined by explicit start and end values. The speed at which the widget
plays is defined by the interval (in milliseconds), but it is also
possible to skip frames using the step parameter.

Reference:
[https://panel.holoviz.org/reference/widgets/Player.html](https://panel.holoviz.org/reference/widgets/Player.html)

Example:

\>\>\>
Player(name='Player',
start=0,
end=100,
value=32,
loop_policy='loop',
value_align='top_center')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> [class="reference internal" title="panel.widgets.player.PlayerBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.player.PlayerBase](panel.widgets.player.md#panel.widgets.player.PlayerBase):
> height, width, direction, interval, loop_policy, preview_duration,
> show_loop_controls, show_value, step, value_align, scale_buttons,
> visible_buttons, visible_loop_options
>
>

`value`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Current player value

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Lower bound on the slider value

`end`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Upper bound on the slider value

`value_throttled`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
Current throttled player value.

class panel.widgets.Progress(\*, active, bar_color, max, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](panel.widgets.indicators.md#panel.widgets.indicators.ValueIndicator)

The Progress widget displays the progress towards some target based on
the current value and the max value.

If no value is set, the Progress widget is in indeterminate mode and
will animate depending on whether it is active or not. A more beautiful
indicator for this use case is the LoadingSpinner.

Reference:
[https://panel.holoviz.org/reference/indicators/Progress.html](https://panel.holoviz.org/reference/indicators/Progress.html)

Example:

\>\>\>
Progress(value=20,
max=100,
bar_color="primary")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``Integer(allow_None=True,`` ``bounds=(-1,`` ``None),`` ``default=-1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value of the progress bar. If set to -1 the progress bar
will be indeterminate and animate depending on the active parameter.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`sizing_mode`` ``=`` ``Selector(label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

`active`` ``=`` ``Boolean(default=True,`` ``label='Active')`
If no value is set the active property toggles animation of the progress
bar on and off.

`bar_color`` ``=`` ``Selector(default='success',`` ``label='Bar`` ``color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the bar, one of ‘primary’, ‘secondary’, ‘success’, ‘info’,
‘warning’, ‘danger’, ‘light’, ‘dark’.

`max`` ``=`` ``Integer(default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max')`
The maximum value of the progress bar.

sizing_mode: t.Literal\['fixed', 'stretch_width', 'stretch_height', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'\] \| None = None

class panel.widgets.RadioBoxGroup(\*, inline, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RadioGroupBase`

The RadioBoxGroup widget allows selecting from a list or dictionary of
values using a set of checkboxes.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioButtonGroup,
Select and DiscreteSlider widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/RadioBoxGroup.html](https://panel.holoviz.org/reference/widgets/RadioBoxGroup.html)

Example:

\>\>\>
RadioBoxGroup(
...
name='Sponsor',
options=\['Anaconda',
'Blackstone'\],
inline=True
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> href="panel.widgets.select.html#panel.widgets.select.SingleSelectBase"
> class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase:
> value
>
>

`inline`` ``=`` ``Boolean(default=False,`` ``label='Inline')`
Whether the items be arrange vertically
(`False`) or horizontally in-line
(`True`).

class panel.widgets.RadioButtonGroup(\*, orientation, options, button_style, button_type, color, variant, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RadioGroupBase`,
`_ButtonBase`,
`TooltipMixin`

The RadioButtonGroup widget allows selecting from a list or dictionary
of values using a set of toggle buttons.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioBoxGroup,
Select, and DiscreteSlider widgets.

Reference: [https://panel.holoviz.org/reference/widgets/RadioButtonGroup.html](https://panel.holoviz.org/reference/widgets/RadioButtonGroup.html)

Example:

\>\>\>
RadioButtonGroup(
...
name='Plotting
library',
options=\['Matplotlib',
'Bokeh',
'Plotly'\],
...
color='success'
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> href="panel.widgets.select.html#panel.widgets.select.SingleSelectBase"
> class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase:
> value
>
>

`orientation`` ``=`` ``Selector(default='horizontal',`` ``label='Orientation',`` ``names={},`` ``objects=['horizontal',`` ``'vertical'])`
Button group orientation, either ‘horizontal’ (default) or ‘vertical’.

class panel.widgets.RangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RangeSliderBase`

The RangeSlider widget allows selecting a floating-point range using a
slider with two handles.

Reference:
[https://panel.holoviz.org/reference/widgets/RangeSlider.html](https://panel.holoviz.org/reference/widgets/RangeSlider.html)

Example:

\>\>\>
RangeSlider(
...
value=(1.0,
1.5),
start=0.0,
end=2.0,
step=0.25,
name="A
tuple of floats" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Range(default=(0,`` ``1),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of values. Updated when a handle is
dragged.

`value_start`` ``=`` ``Number(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``start',`` ``readonly=True)`
The lower value of the selected range.

`value_end`` ``=`` ``Number(constant=True,`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``end',`` ``readonly=True)`
The upper value of the selected range.

`value_throttled`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of floating point values. Updated when a
handle is released

`start`` ``=`` ``Number(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Number(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`format`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.formatters.TickFormatter'>),`` ``label='Format')`
A format string or bokeh TickFormatter.

class panel.widgets.Select(\*, description, disabled_options, groups, size, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](panel.widgets.select.md#panel.widgets.select.SingleSelectBase)

The Select widget allows selecting a value from a list or dictionary of
options by selecting it from a dropdown menu or selection area.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioBoxGroup,
AutocompleteInput and DiscreteSlider widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/Select.html](https://panel.holoviz.org/reference/widgets/Select.html)

Example:

\>\>\>
Select(name='Study',
options=\['Biology',
'Chemistry',
'Physics'\])

Attributes:
**labels**

**values**

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> href="panel.widgets.select.html#panel.widgets.select.SingleSelectBase"
> class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase:
> value
>
>

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
A description of the widget, which will be displayed as a tooltip.

`disabled_options`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Disabled`` ``options',`` ``nested_refs=True)`
Optional list of `options` that are disabled,
i.e. unusable and un-clickable. If `options` is
a dictionary the list items must be dictionary values.

`groups`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Groups',`` ``nested_refs=True)`
Dictionary whose keys are used to visually group the options and whose
values are either a list or a dictionary of options to select from.
Mutually exclusive with `options` and valid
only if `size` is 1.

`size`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
Declares how many options are displayed at the same time. If set to 1
displays options as dropdown otherwise displays scrollable area.

class panel.widgets.SpeechToText(\*, \_grammars, abort, audio_started, button_hide, button_not_started, button_started, button_type, color, continuous, grammars, interim_results, lang, max_alternatives, results, service_uri, sound_started, speech_started, start, started, stop, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The SpeechToText widget controls the speech recognition service of the
browser.

It wraps the HTML5 SpeechRecognition API. See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)

Reference:
[https://panel.holoviz.org/reference/widgets/SpeechToText.html](https://panel.holoviz.org/reference/widgets/SpeechToText.html)

Example:

\>\>\>
SpeechToText(color="light")

This functionality is **experimental** and only supported by Chrome and
a few other browsers. Checkout
[https://caniuse.com/speech-recognition](https://caniuse.com/speech-recognition)
for a up to date list of browsers supporting the SpeechRecognition Api.
Or alternatively [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility)

On some browsers, like Chrome, using Speech Recognition on a web page
involves a server-based recognition engine. Your audio is sent to a web
service for recognition processing, so it won’t work offline. Whether
this is secure and confidential enough for your use case is up to you to
evaluate.

Attributes:
[results_as_html](#panel.widgets.SpeechToText.results_as_html)
Returns the results formatted as html

[results_deserialized](#panel.widgets.SpeechToText.results_deserialized)
Returns the results as a List of RecognitionResults

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``String(constant=True,`` ``default='')`
The transcipt of the highest confidence RecognitionAlternative of the
last RecognitionResult. Please note we strip the transcript for leading
spaces.

`abort`` ``=`` ``Event(default=False,`` ``label='Abort')`
Stops the speech recognition service from listening to incoming audio,
and doesn’t attempt to return a RecognitionResult.

`start`` ``=`` ``Event(default=False,`` ``label='Start')`
Starts the speech recognition service listening to incoming audio with
intent to recognize grammars associated with the current
SpeechRecognition.

`stop`` ``=`` ``Event(default=False,`` ``label='Stop')`
Stops the speech recognition service from listening to incoming audio,
and attempts to return a RecognitionResult using the audio captured so
far.

`lang`` ``=`` ``Selector(allow_None=True,`` ``default='',`` ``names={},`` ``objects=['',`` ``'af-ZA',`` ``'ar-AE',`` ``'ar-BH',`` ``'ar-DZ',`` ``'ar-EG',`` ``'ar-IL',`` ``'ar-IQ',`` ``'ar-JO',`` ``'ar-KW',`` ``'ar-LB',`` ``'ar-MA',`` ``'ar-OM',`` ``'ar-PS',`` ``'ar-QA',`` ``'ar-SA',`` ``'ar-TN',`` ``'bg-BG',`` ``'ca-ES',`` ``'cmn-Hans-CN',`` ``'cmn-Hans-HK',`` ``'cmn-Hant-TW',`` ``'cs-CZ',`` ``'da-DK',`` ``'de-DE',`` ``'el-GR',`` ``'en-AU',`` ``'en-CA',`` ``'en-GB',`` ``'en-IE',`` ``'en-IN',`` ``'en-NZ',`` ``'en-PH',`` ``'en-US',`` ``'en-ZA',`` ``'es-AR',`` ``'es-BO',`` ``'es-CL',`` ``'es-CO',`` ``'es-CR',`` ``'es-DO',`` ``'es-EC',`` ``'es-ES',`` ``'es-GT',`` ``'es-HN',`` ``'es-MX',`` ``'es-NI',`` ``'es-PA',`` ``'es-PE',`` ``'es-PR',`` ``'es-PY',`` ``'es-SV',`` ``'es-US',`` ``'es-UY',`` ``'es-VE',`` ``'eu-ES',`` ``'fa-IR',`` ``'fi-FI',`` ``'fil-PH',`` ``'fr-FR',`` ``'gl-ES',`` ``'he-IL',`` ``'hi-IN',`` ``'hr_HR',`` ``'hu-HU',`` ``'id-ID',`` ``'is-IS',`` ``'it-CH',`` ``'it-IT',`` ``'ja-JP',`` ``'ko-KR',`` ``'lt-LT',`` ``'ms-MY',`` ``'nb-NO',`` ``'nl-NL',`` ``'pl-PL',`` ``'pt-BR',`` ``'pt-PT',`` ``'ro-RO',`` ``'ru-RU',`` ``'sk-SK',`` ``'sl-SI',`` ``'sr-RS',`` ``'sv-SE',`` ``'th-TH',`` ``'tr-TR',`` ``'uk-UA',`` ``'vi-VN',`` ``'yue-Hant-HK',`` ``'zu-ZA'])`
The language of the current SpeechRecognition in BCP 47 format. For
example ‘en-US’. If not specified, this defaults to the HTML lang
attribute value, or the user agent’s language setting if that isn’t set
either.

`continuous`` ``=`` ``Boolean(default=False,`` ``label='Continuous')`
Controls whether continuous results are returned for each recognition,
or only a single result. Defaults to False

`interim_results`` ``=`` ``Boolean(default=False,`` ``label='Interim`` ``results')`
Controls whether interim results should be returned (True) or not
(False.) Interim results are results that are not yet final (e.g. the
RecognitionResult.is_final property is False).

`max_alternatives`` ``=`` ``Integer(bounds=(1,`` ``5),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``alternatives')`
Sets the maximum number of RecognitionAlternatives provided per result.
A number between 1 and 5. The default value is 1.

`service_uri`` ``=`` ``String(default='',`` ``label='Service`` ``uri')`
Specifies the location of the speech recognition service used by the
current SpeechRecognition to handle the actual recognition. The default
is the user agent’s default speech service.

`grammars`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.widgets.speech_to_text.GrammarList'>,`` ``label='Grammars')`
A GrammarList object that represents the grammars that will be
understood by the current SpeechRecognition service

`button_hide`` ``=`` ``Boolean(default=False)`
If True no button is shown. If False a toggle Start/ Stop button is
shown.

`button_type`` ``=`` ``Selector(default='light',`` ``label='Button`` ``type',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light',`` ``'light',`` ``'dark'])`
The button styling. The same value is exposed as
`color`.

`color`` ``=`` ``Selector(default='light',`` ``label='Color',`` ``names={},`` ``objects=['default',`` ``'primary',`` ``'success',`` ``'warning',`` ``'danger',`` ``'light',`` ``'light',`` ``'dark'])`
Semantic color of the button; alias for
`button_type`.

`button_not_started`` ``=`` ``String(default='')`
The text to show on the button when the SpeechRecognition service is NOT
started. If ‘’ a *muted microphone* icon is shown.

`button_started`` ``=`` ``String(default='')`
The text to show on the button when the SpeechRecognition service is
started. If ‘’ a *muted microphone* icon is shown.

`started`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Started')`
Returns True if the Speech Recognition Service is started and False
otherwise.

`audio_started`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Audio`` ``started')`
Returns True if the Audio is started and False otherwise.

`sound_started`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Sound`` ``started')`
Returns True if the Sound is started and False otherwise.

`speech_started`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Speech`` ``started')`
Returns True if the the User has started speaking and False otherwise.

`results`` ``=`` ``List(bounds=(0,`` ``None),`` ``constant=True,`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Results')`
The results as a list of Dictionaries.

`_grammars`` ``=`` ``List(bounds=(0,`` ``None),`` ``constant=True,`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='`` ``grammars')`
List used to transfer the serialized grammars from server to browser.

property results_as_html: str
Returns the results formatted as html

Convenience method for ease of use

property results_deserialized
Returns the results as a List of RecognitionResults

panel.widgets.Spinner
alias of
[NumberInput](panel.widgets.input.md#panel.widgets.input.NumberInput)

class panel.widgets.StaticText(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The StaticText widget displays a text value, but does not allow editing
it.

Reference:
[https://panel.holoviz.org/reference/widgets/StaticText.html](https://panel.holoviz.org/reference/widgets/StaticText.html)

Example:

\>\>\>
StaticText(name='Model',
value='animagen2')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The current value to be displayed.

class panel.widgets.Switch(**params: Any)
Bases: `_BooleanWidget`

The Switch allows toggling a single condition between True/False states
by ticking a checkbox.

This widget is interchangeable with the Toggle widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Switch.html](https://panel.holoviz.org/reference/widgets/Switch.html)

Example:

\>\>\>
Switch(name='Works
with the tools you know and love',
value=True)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.input._BooleanWidget`: value
>
>

class panel.widgets.Tabulator(value=None, **params)
Bases:
[BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable)

The Tabulator widget wraps the \[Tabulator
js\]([http://tabulator.info/](http://tabulator.info/)) table to provide
a full-featured, very powerful interactive table.

Reference:
[https://panel.holoviz.org/reference/widgets/Tabulator.html](https://panel.holoviz.org/reference/widgets/Tabulator.html)

Example:

\>\>\>
Tabulator(df,
theme='site',
pagination='remote',
page_size=25)

Attributes:
[current_view](#panel.widgets.Tabulator.current_view)
Returns the current view of the table after filtering and sorting are
applied.

Methods

|  |  |
|----|----|
| [download](#panel.widgets.Tabulator.download)(\[filename\]) | Triggers downloading of the table as a CSV or JSON. |
| [download_menu](#panel.widgets.Tabulator.download_menu)(\[text_kwargs, button_kwargs\]) | Returns a menu containing a TextInput and Button widget to set the filename and trigger a client-side download of the data. |
| [on_click](#panel.widgets.Tabulator.on_click)(callback\[, column\]) | Register a callback to be executed when any cell is clicked. |
| [on_edit](#panel.widgets.Tabulator.on_edit)(callback) | Register a callback to be executed when a cell is edited. |
| [stream](#panel.widgets.Tabulator.stream)(stream_value\[, rollover, ...\]) | Streams (appends) the stream_value provided to the existing value in an efficient manner. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.tables.BaseTable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.tables.BaseTable](panel.widgets.tables.md#panel.widgets.tables.BaseTable):
> value, aggregators, editables, editors, formatters, hierarchical,
> show_index, sorters, text_align, titles, widths
>
>

`selection`` ``=`` ``_ListValidateWithCallable(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Selection')`
The currently selected rows of the table. It validates its values
against ‘selectable_rows’ if used.

`row_height`` ``=`` ``Integer(allow_refs=True,`` ``default=30,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Row`` ``height')`
The height of each table row.

`buttons`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Buttons',`` ``nested_refs=True)`
Dictionary mapping from column name to a HTML element to use as the
button icon.

`container_popup`` ``=`` ``Boolean(allow_refs=True,`` ``default=True,`` ``label='Container`` ``popup')`
If True, popups will appear within the table container, otherwise popups
will be appended to the body element of the DOM.

`expanded`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Expanded',`` ``nested_refs=True)`
List of expanded rows, only applicable if a row_content function has
been defined.

`embed_content`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Embed`` ``content')`
Whether to embed the row_content or render it dynamically when a row is
expanded.

`filters`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'dict'>,`` ``label='Filters')`
List of client-side filters declared as dictionaries containing ‘field’,
‘type’ and ‘value’ keys.

`frozen_columns`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'list'>,`` ``<class`` ``'dict'>),`` ``default=[],`` ``label='Frozen`` ``columns',`` ``nested_refs=True)`
One of: - List indicating the columns to freeze. The column(s) may be
selected by name or index. - Dict indicating columns to freeze as keys
and their freeze location as values, freeze location is either ‘right’
or ‘left’.

`frozen_rows`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'int'>,`` ``label='Frozen`` ``rows',`` ``nested_refs=True)`
List indicating the rows to freeze. If set, the first N rows will be
frozen, which prevents them from scrolling out of frame; if set to a
negative value the last N rows will be frozen.

`groups`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Groups',`` ``nested_refs=True)`
Dictionary mapping defining the groups.

`groupby`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Groupby',`` ``nested_refs=True)`
Groups rows in the table by one or more columns.

`header_align`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'str'>),`` ``default={},`` ``label='Header`` ``align',`` ``nested_refs=True)`
A mapping from column name to alignment or a fixed column alignment,
which should be one of ‘left’, ‘center’, ‘right’.

`header_filters`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'dict'>),`` ``label='Header`` ``filters',`` ``nested_refs=True)`
Whether to enable filters in the header or dictionary configuring
filters for each column.

`header_tooltips`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Header`` ``tooltips')`
Dictionary mapping from column name to a tooltip to show when hovering
over the column header.

`hidden_columns`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Hidden`` ``columns',`` ``nested_refs=True)`
List of columns to hide.

`movable_columns`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Movable`` ``columns')`
Whether columns can be reordered by dragging their headers.

`layout`` ``=`` ``Selector(allow_refs=True,`` ``default='fit_data_table',`` ``label='Layout',`` ``names={},`` ``objects=['fit_data',`` ``'fit_data_fill',`` ``'fit_data_stretch',`` ``'fit_data_table',`` ``'fit_columns'])`
Describes the column layout mode with one of the following options
‘fit_columns’, ‘fit_data’, ‘fit_data_stretch’, ‘fit_data_fill’,
‘fit_data_table’.

`initial_page_size`` ``=`` ``Integer(allow_refs=True,`` ``bounds=(1,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Initial`` ``page`` ``size')`
Initial page size if page_size is None and therefore automatically set.

`pagination`` ``=`` ``Selector(allow_None=True,`` ``allow_refs=True,`` ``label='Pagination',`` ``names={},`` ``objects=['local',`` ``'remote'])`
Defines the pagination mode of the Tabulator. - None No pagination is
applied, all rows are rendered. - ‘local’ (client-side) Pagination is
applied locally, i.e. the entire DataFrame is loaded and then
paginated. - ‘remote’ (server-side) Pagination is applied remotely, i.e.
only the current page is loaded from the server.

`page`` ``=`` ``Integer(allow_refs=True,`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Page')`
Currently selected page (indexed starting at 1), if pagination is
enabled.

`page_size`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Page`` ``size')`
Number of rows to render per page, if pagination is enabled.

`row_content`` ``=`` ``Callable(allow_None=True,`` ``label='Row`` ``content')`
A function which is given the DataFrame row and should return a Panel
object to render as additional detail below the row. The function may
also be asynchronous.

`selectable`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'str'>,`` ``<class`` ``'int'>),`` ``default=True,`` ``label='Selectable')`
Defines the selection mode of the Tabulator. - True Selects rows on
click. To select multiple use Ctrl-select, to select a range use
Shift-select - False Disables selection - ‘checkbox’ Adds a column of
checkboxes to toggle selections - ‘checkbox-single’ Same as ‘checkbox’
but header does not allow select/deselect all - ‘toggle’ Selection
toggles when clicked - int The maximum number of selectable rows.

`selectable_rows`` ``=`` ``Callable(allow_None=True,`` ``allow_refs=True,`` ``label='Selectable`` ``rows')`
A function which given a DataFrame should return a list of rows by
integer index, which are selectable.

`sortable`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'bool'>,`` ``<class`` ``'dict'>),`` ``default=True,`` ``label='Sortable')`
Whether the columns in the table should be sortable. Can either be
specified as a simple boolean toggling the behavior on and off or as a
dictionary specifying the option per column.

`theme`` ``=`` ``Selector(allow_refs=True,`` ``default='simple',`` ``label='Theme',`` ``names={},`` ``objects=['default',`` ``'site',`` ``'simple',`` ``'midnight',`` ``'modern',`` ``'bootstrap',`` ``'bootstrap4',`` ``'materialize',`` ``'bulma',`` ``'semantic-ui',`` ``'fast',`` ``'bootstrap5'])`
Tabulator CSS theme to apply to table.

`theme_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Theme`` ``classes',`` ``nested_refs=True)`
List of extra CSS classes to apply to the Tabulator element to customize
the theme.

`title_formatters`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Title`` ``formatters',`` ``nested_refs=True)`
Tabulator formatter specification to use for a particular column header
title.

property current_view: pd.DataFrame
Returns the current view of the table after filtering and sorting are
applied.

download(filename: str = 'table.csv')
Triggers downloading of the table as a CSV or JSON.

Parameters:
**filename: str**
The filename to save the table as.

download_menu(text_kwargs={}, button_kwargs={})
Returns a menu containing a TextInput and Button widget to set the
filename and trigger a client-side download of the data.

Parameters:
**text_kwargs: dict**
Keyword arguments passed to the TextInput constructor

**button_kwargs: dict**
Keyword arguments passed to the Button constructor

Returns:
filename: TextInput
The TextInput widget setting a filename.

button: Button
The Button that triggers a download.

on_click(callback: Callable\[\[CellClickEvent\], None\], column: str \| None = None)
Register a callback to be executed when any cell is clicked. The
callback is given a CellClickEvent declaring the column and row of the
cell that was clicked.

Parameters:
**callback: (callable)**
The callback to run on edit events.

**column: (str)**
Optional argument restricting the callback to a specific column.

on_edit(callback: Callable\[\[TableEditEvent\], None\])
Register a callback to be executed when a cell is edited. Whenever a
cell is edited on_edit callbacks are called with a TableEditEvent as the
first argument containing the column, row and value of the edited cell.

Parameters:
**callback: (callable)**
The callback to run on edit events.

stream(stream_value, rollover=None, reset_index=True, follow=True)
Streams (appends) the stream_value provided to the existing value in an
efficient manner.

Parameters:
**stream_value: (pd.DataFrame \| pd.Series \| Dict)**
The new value(s) to append to the existing value.

**rollover: int**
A maximum column size, above which data from the start of the column
begins to be discarded. If None, then columns will continue to grow
unbounded.

**reset_index: (bool, default=True)**
If True and the stream_value is a DataFrame, then its index is reset.
Helps to keep the index unique and named index

Raises:
ValueError: Raised if the stream_value is not a supported type.

Examples

Stream a Series to a DataFrame \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.Series({“x”: 4, “y”: “d”}) \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dataframe to a Dataframe \>\>\> value = pd.DataFrame({“x”: \[1,
2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = pd.DataFrame({“x”: \[3, 4\], “y”: \[“c”, “d”\]})
\>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

Stream a Dictionary row to a DataFrame \>\>\> value = pd.DataFrame({“x”:
\[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator = Tabulator(value=value)
\>\>\> stream_value = {“x”: 4, “y”: “d”} \>\>\>
tabulator.stream(stream_value) \>\>\> tabulator.value.to_dict(“list”)
{‘x’: \[1, 2, 4\], ‘y’: \[‘a’, ‘b’, ‘d’\]}

Stream a Dictionary of Columns to a Dataframe \>\>\> value =
pd.DataFrame({“x”: \[1, 2\], “y”: \[“a”, “b”\]}) \>\>\> tabulator =
Tabulator(value=value) \>\>\> stream_value = {“x”: \[3, 4\], “y”: \[“c”,
“d”\]} \>\>\> tabulator.stream(stream_value) \>\>\>
tabulator.value.to_dict(“list”) {‘x’: \[1, 2, 3, 4\], ‘y’: \[‘a’, ‘b’,
‘c’, ‘d’\]}

class panel.widgets.Terminal(output=None, **params)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The Terminal widget renders a live terminal in the browser using the
xterm.js library making it possible to display logs or even provide an
interactive terminal in a Panel application.

Reference:
[https://panel.holoviz.org/reference/widgets/Terminal.html](https://panel.holoviz.org/reference/widgets/Terminal.html)

Example:

\>\>\>
Terminal(
...  "Welcome to the Panel
Terminal!",
options={"cursorBlink":
True}
... )

Attributes:
**clear**

**closed**

[subprocess](#panel.widgets.Terminal.subprocess)
The subprocess enables running commands like ‘ls’, \[‘ls’, ‘-l’\],
‘bash’, ‘python’ and ‘ipython’ in the terminal.

Methods

|                |     |
|----------------|-----|
| **fileno**     |     |
| **flush**      |     |
| **getvalue**   |     |
| **read**       |     |
| **readable**   |     |
| **readlines**  |     |
| **seekable**   |     |
| **writable**   |     |
| **write**      |     |
| **writelines** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``String(constant=True,`` ``default='',`` ``readonly=True)`
User input received from the Terminal. Sent one character at the time.

`clear`` ``=`` ``Action(allow_None=True,`` ``constant=True,`` ``label='Clear')`
Clears the Terminal.

`options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Options')`
Initial Options for the Terminal Constructor. cf. [https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/](https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/)

`output`` ``=`` ``String(default='',`` ``label='Output')`
System output written to the Terminal

`ncols`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols',`` ``readonly=True)`
The number of columns in the terminal.

`nrows`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows',`` ``readonly=True)`
The number of rows in the terminal.

`write_to_console`` ``=`` ``Boolean(default=False,`` ``label='Write`` ``to`` ``console')`
Whether or not to write to the server console.

`_clears`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``clears')`
Sends a signal to clear the terminal

`_output`` ``=`` ``String(default='',`` ``label='`` ``output')`

property subprocess
The subprocess enables running commands like ‘ls’, \[‘ls’, ‘-l’\],
‘bash’, ‘python’ and ‘ipython’ in the terminal.

class panel.widgets.TextAreaInput(**params: Any)
Bases: `_TextInputBase`

>
>
> The TextAreaInput allows entering any multiline string using a text
> input box.
>
> Lines are joined with the newline character \`
>
>

[\`](#id5).

>
>
> Reference:
> [class="reference external">https://panel.holoviz.org/reference/widgets/TextAreaInput.html](https://panel.holoviz.org/reference/widgets/TextAreaInput.html)
> :Example:
>
>
>
>
>
> \>\>\>
> TextAreaInput(
> ...
> name='Description',
> placeholder='Enter
> your description here...' ...
> )
>
>
>
>
>
>

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

`auto_grow`` ``=`` ``Boolean(default=False,`` ``label='Auto`` ``grow')`
Whether the text area should automatically grow vertically to
accommodate the current text.

`cols`` ``=`` ``Integer(default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Cols')`
Number of columns in the text input field.

`max_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``rows')`
When combined with auto_grow this determines the maximum number of rows
the input area can grow.

`rows`` ``=`` ``Integer(default=2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Rows')`
Number of rows in the text input field.

`resizable`` ``=`` ``Selector(default='both',`` ``label='Resizable',`` ``names={},`` ``objects=['both',`` ``'width',`` ``'height',`` ``False])`
Whether the layout is interactively resizable, and if so in which
dimensions: width, height, or both. Can only be set during
initialization.

class panel.widgets.TextEditor(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The TextEditor widget provides a WYSIWYG (what-you-see-is-what-you-get)
rich text editor which outputs HTML.

The editor is built on top of the
\[Quill.js\]([https://quilljs.com/](https://quilljs.com/)) library.

Reference:
[https://panel.holoviz.org/reference/widgets/TextEditor.html](https://panel.holoviz.org/reference/widgets/TextEditor.html)

Example:

\>\>\>
TextEditor(placeholder='Enter
some text')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width
>
>

`value`` ``=`` ``String(default='',`` ``label='Value')`
State of the current text in the editor if on_keyup. Otherwise, only
upon loss of focus, i.e. clicking outside the editor, or pressing
\<Ctrl+Enter\> or \<Cmd+Enter\>.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the editor is disabled.

`mode`` ``=`` ``Selector(default='toolbar',`` ``label='Mode',`` ``names={},`` ``objects=['bubble',`` ``'toolbar'])`
Whether to display a toolbar or a bubble menu on highlight.

`on_keyup`` ``=`` ``Boolean(default=True,`` ``label='On`` ``keyup')`
Whether to update the value on every key press or only upon loss of
focus / hotkeys.

`toolbar`` ``=`` ``ClassSelector(class_=(<class`` ``'list'>,`` ``<class`` ``'bool'>),`` ``default=True,`` ``label='Toolbar')`
Toolbar configuration either as a boolean toggle or a configuration
specified as a list.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder output when the editor is empty.

`selection`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Selection')`
The current text selection in the editor, as
`{"text":`` ``"..."}`
when the user has a non-empty selection, else
`{}`. Updates live as the selection changes.

`value_input`` ``=`` ``String(default='',`` ``label='Value`` ``input')`
State of the current text updated on every key press. Identical to value
if on_keyup.

class panel.widgets.TextInput(**params: Any)
Bases: `_TextInputBase`

The TextInput widget allows entering any string using a text input box.

Reference:
[https://panel.holoviz.org/reference/widgets/TextInput.html](https://panel.holoviz.org/reference/widgets/TextInput.html)

Example:

\>\>\>
TextInput(name='Name',
placeholder='Enter
your name here ...')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

`enter_pressed`` ``=`` ``Event(allow_refs=True,`` ``default=False,`` ``label='Enter`` ``pressed')`
Event when the enter key has been pressed.

class panel.widgets.TextToSpeech(\*, \_voices, auto_speak, cancel, pause, resume, speak, lang, pitch, rate, voice, volume, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Utterance](panel.widgets.text_to_speech.md#panel.widgets.text_to_speech.Utterance),
[Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The TextToSpeech widget wraps the HTML5 SpeechSynthesis API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)

Reference:
[https://panel.holoviz.org/reference/widgets/TextToSpeech.html](https://panel.holoviz.org/reference/widgets/TextToSpeech.html)

Example:

\>\>\>
TextToSpeech(label="Speech
Synthesis",
value="Data
apps are nice")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> href="panel.widgets.text_to_speech.html#panel.widgets.text_to_speech.Utterance"
> class="reference internal"
> title="panel.widgets.text_to_speech.Utterance"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.text_to_speech.Utterance:
> value, lang, pitch, rate, voice, volume
>
>

`auto_speak`` ``=`` ``Boolean(default=True,`` ``label='Auto`` ``speak')`
Whether or not to automatically speak when the value changes.

`cancel`` ``=`` ``Event(default=False,`` ``label='Cancel')`
Removes all utterances from the utterance queue.

`pause`` ``=`` ``Event(default=False,`` ``label='Pause')`
Puts the TextToSpeak object into a paused state.

`resume`` ``=`` ``Event(default=False,`` ``label='Resume')`
Puts the TextToSpeak object into a non-paused state: resumes it if it
was already paused.

`paused`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Paused',`` ``readonly=True)`
A Boolean that returns true if the TextToSpeak object is in a paused
state.

`pending`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Pending',`` ``readonly=True)`
A Boolean that returns true if the utterance queue contains
as-yet-unspoken utterances.

`speak`` ``=`` ``Event(default=False,`` ``label='Speak')`
Speak. I.e. send a new Utterance to the browser

`speaking`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Speaking',`` ``readonly=True)`
A Boolean that returns true if an utterance is currently in the process
of being spoken — even if TextToSpeak is in a paused state.

`voices`` ``=`` ``List(bounds=(0,`` ``None),`` ``constant=True,`` ``default=[],`` ``item_type=<class`` ``'panel.widgets.text_to_speech.Voice'>,`` ``label='Voices',`` ``readonly=True)`
Returns a list of Voice objects representing all the available voices on
the current device.

`_voices`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.widgets.text_to_speech.Voice'>,`` ``label='`` ``voices')`

class panel.widgets.TimePicker(**params: Any)
Bases: `_TimeCommon`

The TimePicker allows selecting a time value using a text box and a
time-picking utility.

Reference:
[https://panel.holoviz.org/reference/widgets/TimePicker.html](https://panel.holoviz.org/reference/widgets/TimePicker.html)

Example:

\>\>\>
TimePicker(
...
value="12:59:31",
start="09:00:00",
end="18:00:00",
name="Time"
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.input._TimeCommon`:
> hour_increment, minute_increment, second_increment, seconds, clock
>
>

`value`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='Value')`
The current value

`start`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='Start')`
Inclusive lower bound of the allowed time selection

`end`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='End')`
Inclusive upper bound of the allowed time selection

`format`` ``=`` ``String(default='H:i',`` ``label='Format')`
Formatting specification for the display of the picked date.
+—+————————————+————+ \| H \| Hours (24 hours) \| 00 to 23 \| \| h \|
Hours \| 1 to 12 \| \| G \| Hours, 2 digits with leading zeros \| 1 to
12 \| \| i \| Minutes \| 00 to 59 \| \| S \| Seconds, 2 digits \| 00 to
59 \| \| s \| Seconds \| 0, 1 to 59 \| \| K \| AM/PM \| AM or PM \|
+—+————————————+————+ See also
[https://flatpickr.js.org/formatting/#date-formatting-tokens](https://flatpickr.js.org/formatting/#date-formatting-tokens).

class panel.widgets.Toggle(**params: Any)
Bases: `_ButtonBase`,
[IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin)

The Toggle widget allows toggling a single condition between True/False
states.

This widget is interchangeable with the Checkbox widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Toggle.html](https://panel.holoviz.org/reference/widgets/Toggle.html)

Example:

\>\>\>
Toggle(name='Toggle',
color='success')

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.button.IconMixin"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.button.IconMixin](panel.widgets.button.md#panel.widgets.button.IconMixin):
> icon, icon_size
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Whether the button is currently toggled.

class panel.widgets.ToggleGroup(\*, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](panel.widgets.select.md#panel.widgets.select.SingleSelectBase)

This class is a factory of ToggleGroup widgets.

A ToggleGroup is a group of widgets which can be switched ‘on’ or ‘off’.

Two types of widgets are available through the widget_type argument :
- ‘button’ (default)

- ‘box’

Two different behaviors are available through behavior argument:
- ‘check’ (default)boolean
  Any number of widgets can be selected. In this case value is a ‘list’
  of objects.

- ‘radio’boolean
  One and only one widget is switched on. In this case value is an
  ‘object’.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> [class="reference internal" title="panel.widgets.select.SelectBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](panel.widgets.select.md#panel.widgets.select.SelectBase):
> options
>
> href="panel.widgets.select.html#panel.widgets.select.SingleSelectBase"
> class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase:
> value
>
>

class panel.widgets.ToggleIcon(**params: Any)
Bases: `_ClickableIcon`,
`TooltipMixin`

The ToggleIcon widget allows toggling a single condition between
True/False states. This widget is interchangeable with the Checkbox and
Toggle widget.

This widget incorporates a value attribute, which alternates between
False and True.

Reference:
[https://panel.holoviz.org/reference/widgets/ToggleIcon.html](https://panel.holoviz.org/reference/widgets/ToggleIcon.html)

Example:

\>\>\>
pn.widgets.ToggleIcon(
...
icon="thumb-up",
active_icon="thumb-down",
size="4em",
description="Like"
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.icon._ClickableIcon`: value,
> active_icon, icon, size
>
>

class panel.widgets.TooltipIcon(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The TooltipIcon displays a small ? icon. When you hover over the ? icon,
the value will display.

Use the TooltipIcon to provide

- helpful information to users without taking up a lot of screen space

- tooltips next to Panel widgets that do not support tooltips yet.

Reference: [https://panel.holoviz.org/reference/indicators/TooltipIcon.html](https://panel.holoviz.org/reference/indicators/TooltipIcon.html)

Example:

\>\>\>
pn.widgets.TooltipIcon(value="This
is a simple tooltip by using a string")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> aspect_ratio, css_classes, design, min_width, min_height, max_width,
> max_height, styles, stylesheets, tags, width_policy, height_policy,
> sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``ClassSelector(class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.ui.tooltips.Tooltip'>),`` ``default='Description',`` ``label='Value')`
The description in the tooltip.

`align`` ``=`` ``Align(default='center',`` ``label='Align')`
Whether the object should be aligned with the start, end or center of
its container. If set as a tuple it will declare (vertical, horizontal)
alignment.

class panel.widgets.Tqdm(\*, layout, lock, max, progress, text, text_pane, write_to_console, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `Indicator`

The Tqdm indicator wraps the well known tqdm progress indicator and
displays the progress towards some target in your Panel app.

Reference:
[https://panel.holoviz.org/reference/indicators/Tqdm.html](https://panel.holoviz.org/reference/indicators/Tqdm.html)

Example:

\>\>\> tqdm
=
Tqdm()
\>\>\> for
i in
tqdm(range(0,10),
desc="My
loop",
leave=True,
colour='#666666'):
...
time.sleep(timeout)

Methods

|  |  |
|----|----|
| `get_lock`() |  |
| [reset](#panel.widgets.Tqdm.reset)() | Resets the parameters |
| `set_lock`(lock) |  |

|            |     |
|------------|-----|
| **pandas** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Integer(bounds=(-1,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value of the progress bar. If set to -1 the progress bar
will be indeterminate and animate depending on the active parameter.

`margin`` ``=`` ``Margin(allow_None=True,`` ``default=0,`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=400,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`layout`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'panel.layout.base.Column'>,`` ``<class`` ``'panel.layout.base.Row'>),`` ``constant=True,`` ``label='Layout')`
The layout for the text and progress indicator.

`lock`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'object'>,`` ``label='Lock')`
The multithreading.Lock or multiprocessing.Lock object to be used by
Tqdm.

`max`` ``=`` ``Integer(default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max')`
The maximum value of the progress bar.

`progress`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.widgets.indicators.Progress'>,`` ``label='Progress')`
The Progress indicator used to display the progress.

`text`` ``=`` ``String(default='',`` ``label='Text')`
The current tqdm style progress text.

`text_pane`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.pane.markup.Str'>,`` ``label='Text`` ``pane')`
The pane to display the text to.

`write_to_console`` ``=`` ``Boolean(default=False,`` ``label='Write`` ``to`` ``console')`
Whether or not to also write to the console.

reset()
Resets the parameters

class panel.widgets.Trend(\*, data, layout, neg_color, plot_color, plot_type, plot_x, plot_y, pos_color, value_change, selection, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `SyncableData`,
`Indicator`

The Trend indicator enables the user to display a dashboard kpi card.

The card can be layout out as:

- a column (text and plot on top of each other) or a row (text and

- plot after each other)

Reference:
[https://panel.holoviz.org/reference/indicators/Trend.html](https://panel.holoviz.org/reference/indicators/Trend.html)

Example:

\>\>\> data
=
{'x':
np.arange(50),
'y':
np.random.randn(50).cumsum()}
\>\>\>
Trend(label='Price',
data=data,
plot_type='area',
width=200,
height=200)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.reactive.SyncableData`: selection
>
>

`label`` ``=`` ``String(default='',`` ``label='Label')`
The label or a short description of the card.

`value`` ``=`` ``Parameter(default='auto',`` ``label='Value')`
The primary value to be displayed.

`sizing_mode`` ``=`` ``Selector(label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

`data`` ``=`` ``Parameter(allow_None=True,`` ``label='Data')`
The plot data declared as a dictionary of arrays or a DataFrame.

`layout`` ``=`` ``Selector(default='column',`` ``label='Layout',`` ``names={},`` ``objects=['column',`` ``'row'])`
The layout of the indicator, either a column (text and plot on top of
each other) or a row (text and plot after each other).

`plot_x`` ``=`` ``String(default='x',`` ``label='Plot`` ``x')`
The name of the key in the plot_data to use on the x-axis.

`plot_y`` ``=`` ``String(default='y',`` ``label='Plot`` ``y')`
The name of the key in the plot_data to use on the y-axis.

`plot_color`` ``=`` ``String(default='#428bca',`` ``label='Plot`` ``color')`
The color to use in the plot.

`plot_type`` ``=`` ``Selector(default='bar',`` ``label='Plot`` ``type',`` ``names={},`` ``objects=['line',`` ``'step',`` ``'area',`` ``'bar'])`
The plot type to render the plot data as.

`pos_color`` ``=`` ``String(default='#5cb85c',`` ``label='Pos`` ``color')`
The color used to indicate a positive change.

`neg_color`` ``=`` ``String(default='#d9534f',`` ``label='Neg`` ``color')`
The color used to indicate a negative change.

`value_change`` ``=`` ``Parameter(default='auto',`` ``label='Value`` ``change')`
A secondary value. For example the change in percent.

sizing_mode: t.Literal\['fixed', 'stretch_width', 'stretch_height', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'\] \| None = None

class panel.widgets.Utterance(\*, lang, pitch, rate, value, voice, volume, name)
Bases: `Parameterized`

An *utterance* is the smallest unit of speech in spoken language
analysis.

The Utterance Model wraps the HTML5 SpeechSynthesisUtterance API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance)

Methods

|  |  |
|----|----|
| [set_voices](#panel.widgets.Utterance.set_voices)(voices) | Updates the lang and voice parameter objects, default and value |
| [to_dict](#panel.widgets.Utterance.to_dict)(\[include_uuid\]) | Returns the object parameter values in a dictionary |

**Parameter Definitions**

------------------------------------------------------------------------

`value`` ``=`` ``String(default='',`` ``label='Value')`
The text that will be synthesised when the utterance is spoken. The text
may be provided as plain text, or a well-formed SSML document.

`lang`` ``=`` ``Selector(default='',`` ``label='Lang',`` ``names={},`` ``objects=[''])`
The language of the utterance.

`pitch`` ``=`` ``Number(bounds=(0.0,`` ``2.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Pitch')`
The pitch at which the utterance will be spoken at expressed as a number
between 0 and 2.

`rate`` ``=`` ``Number(bounds=(0.1,`` ``10.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Rate')`
The speed at which the utterance will be spoken at expressed as a number
between 0.1 and 10.

`voice`` ``=`` ``Selector(label='Voice',`` ``names={},`` ``objects=[])`
The voice that will be used to speak the utterance.

`volume`` ``=`` ``Number(bounds=(0.0,`` ``1.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Volume')`
The volume that the utterance will be spoken at expressed as a number
between 0 and 1.

set_voices(voices)
Updates the lang and voice parameter objects, default and value

to_dict(include_uuid=True)
Returns the object parameter values in a dictionary

Returns:
Dict: \[description\]

class panel.widgets.VideoStream(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The VideoStream displays a video from a local stream (for example from a
webcam) and allows accessing the streamed video data from Python.

Reference:
[https://panel.holoviz.org/reference/widgets/VideoStream.html](https://panel.holoviz.org/reference/widgets/VideoStream.html)

Example:

\>\>\>
VideoStream(label='Video
Stream',
timeout=100)

Methods

|  |  |
|----|----|
| [snapshot](#panel.widgets.VideoStream.snapshot)() | Triggers a snapshot of the current VideoStream state to sync the widget value. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``String(default='',`` ``label='Value')`
A base64 representation of the video stream snapshot.

`format`` ``=`` ``Selector(default='png',`` ``label='Format',`` ``names={},`` ``objects=['png',`` ``'jpeg'])`
The file format as which the video is returned.

`paused`` ``=`` ``Boolean(default=False,`` ``label='Paused')`
Whether the video is currently paused

`timeout`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timeout')`
Interval between snapshots in millisecons

snapshot()
Triggers a snapshot of the current VideoStream state to sync the widget
value.

class panel.widgets.Voice(\*, default, lang, local_service, voice_uri, name)
Bases: `Parameterized`

The current device (i.e. OS and Browser) provides a list of Voices. Each
with a unique name and speaking a specific language.

Wraps the HTML5 SpeecSynthesisVoice API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice)

Methods

|  |  |
|----|----|
| [group_by_lang](#panel.widgets.Voice.group_by_lang)(voices) | Returns a dictionary where the key is the lang and the value is a list of voices for that language. |
| [to_voices_list](#panel.widgets.Voice.to_voices_list)(voices) | Returns a list of Voice objects from the list of dicts provided |

**Parameter Definitions**

------------------------------------------------------------------------

`default`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Default')`
A Boolean indicating whether the voice is the default voice for the
current app language (True), or not (False.)

`lang`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Lang')`
Returns a BCP 47 language tag indicating the language of the voice.

`local_service`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Local`` ``service')`
A Boolean indicating whether the voice is supplied by a local speech
synthesizer service (True), or a remote speech synthesizer service
(False.)

`voice_uri`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Voice`` ``uri')`
Returns the type of URI and location of the speech synthesis service for
this voice.

static group_by_lang(voices)
Returns a dictionary where the key is the lang and the value is a list
of voices for that language.

static to_voices_list(voices)
Returns a list of Voice objects from the list of dicts provided

class panel.widgets.Widget(**params: Any)
Bases: [Reactive](panel.reactive.md#panel.reactive.Reactive),
[WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase)

Widgets allow syncing changes in bokeh widget models with the parameters
on the Widget instance.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=(5,`` ``10),`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`disabled`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Disabled')`
Whether the widget is disabled.

class panel.widgets.WidgetBase(**params: Any)
Bases: `Parameterized`

WidgetBase provides an abstract baseclass for widget components which
can be used to implement a custom widget-like type without implementing
the methods associated with a Reactive Panel component, e.g. it may be
used as a mix-in to a PyComponent or JSComponent.

Attributes:
**rx**

Methods

|  |  |
|----|----|
| [from_param](#panel.widgets.WidgetBase.from_param)(parameter, **params) | Construct a widget from a Parameter and link the two bi-directionally. |
| [from_values](#panel.widgets.WidgetBase.from_values)(values, **params) | Creates an instance of this Widget where the parameters are inferred from the data. |

**Parameter Definitions**

------------------------------------------------------------------------

`label`` ``=`` ``String(allow_refs=True,`` ``default='',`` ``label='Label')`
The label for the widget.

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

classmethod from_param(parameter: param.Parameter, **params) → T
Construct a widget from a Parameter and link the two bi-directionally.

Parameters:
**parameter: param.Parameter**
A parameter to create the widget from.

Returns:
Widget instance linked to the supplied parameter

classmethod from_values(values, **params)
Creates an instance of this Widget where the parameters are inferred
from the data.

Parameters:
**values: Iterable**
The values to infer the parameters from.

**params: dict**
Additional parameters to pass to the widget.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
