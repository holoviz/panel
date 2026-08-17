# panel.widgets.text_to_speech module

The Panel TextToSpeak Widget provides functionality for *text to speech*
via the the HTML5 SpeechSynthesis API.

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)

The term *utterance* is used throughout the API. It is the smallest unit
of speech in spoken language analysis.

class panel.widgets.text_to_speech.TextToSpeech(\*, \_voices, auto_speak, cancel, pause, resume, speak, lang, pitch, rate, voice, volume, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Utterance](#panel.widgets.text_to_speech.Utterance),
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
> [class="reference internal"
> title="panel.widgets.text_to_speech.Utterance"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.text_to_speech.Utterance](#panel.widgets.text_to_speech.Utterance):
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

class panel.widgets.text_to_speech.Utterance(\*, lang, pitch, rate, value, voice, volume, name)
Bases: `Parameterized`

An *utterance* is the smallest unit of speech in spoken language
analysis.

The Utterance Model wraps the HTML5 SpeechSynthesisUtterance API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance)

Methods

|  |  |
|----|----|
| [set_voices](#panel.widgets.text_to_speech.Utterance.set_voices)(voices) | Updates the lang and voice parameter objects, default and value |
| [to_dict](#panel.widgets.text_to_speech.Utterance.to_dict)(\[include_uuid\]) | Returns the object parameter values in a dictionary |

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

class panel.widgets.text_to_speech.Voice(\*, default, lang, local_service, voice_uri, name)
Bases: `Parameterized`

The current device (i.e. OS and Browser) provides a list of Voices. Each
with a unique name and speaking a specific language.

Wraps the HTML5 SpeecSynthesisVoice API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice)

Methods

|  |  |
|----|----|
| [group_by_lang](#panel.widgets.text_to_speech.Voice.group_by_lang)(voices) | Returns a dictionary where the key is the lang and the value is a list of voices for that language. |
| [to_voices_list](#panel.widgets.text_to_speech.Voice.to_voices_list)(voices) | Returns a list of Voice objects from the list of dicts provided |

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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
