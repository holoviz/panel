# panel.widgets.speech_to_text module

The SpeechToText widget controls the speech recognition service of the
browser.

It wraps the HTML5 SpeechRecognition API. See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)

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

class panel.widgets.speech_to_text.Grammar(\*, src, uri, weight, name)
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
| [serialize](#panel.widgets.speech_to_text.Grammar.serialize)() | Returns the grammar as dict |

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

class panel.widgets.speech_to_text.GrammarList(iterable=(), /)
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
| [serialize](#panel.widgets.speech_to_text.GrammarList.serialize)() | Returns a list of serialized grammars |

add_from_string(src, weight=1.0)
Takes a src and weight and adds it to the GrammarList as a new Grammar
object. The new Grammar object is returned.

add_from_uri(uri, weight=1.0)
Takes a grammar present at a specific uri, and adds it to the
GrammarList as a new Grammar object. The new Grammar object is returned.

serialize()
Returns a list of serialized grammars

class panel.widgets.speech_to_text.Language(\*, country, family, name)
Bases: `Parameterized`

**Parameter Definitions**

------------------------------------------------------------------------

`country`` ``=`` ``String(default='',`` ``label='Country')`
A country like ‘United States’

`family`` ``=`` ``String(default='',`` ``label='Family')`
The overall language family. For example ‘English’.

class panel.widgets.speech_to_text.RecognitionAlternative(\*, confidence, transcript, name)
Bases: `Parameterized`

The RecognitionAlternative represents a word or sentence that has been
recognised by the speech recognition service.

Wraps the HTML5 SpeechRecognitionAlternative API

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionAlternative](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionAlternative)

**Parameter Definitions**

------------------------------------------------------------------------

`confidence`` ``=`` ``Number(bounds=(0.0,`` ``1.0),`` ``constant=True,`` ``default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Confidence')`
A numeric estimate between 0 and 1 of how confident the speech
recognition system is that the recognition is correct.

`transcript`` ``=`` ``String(constant=True,`` ``default='',`` ``label='Transcript')`
The transcript of the recognised word or sentence.

class panel.widgets.speech_to_text.RecognitionResult(\*, alternatives, is_final, name)
Bases: `Parameterized`

The Result represents a single recognition match, which may contain
multiple RecognitionAlternative objects.

Wraps the HTML5 SpeechRecognitionResult API.

See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult)

Methods

|  |  |
|----|----|
| [create_from_dict](#panel.widgets.speech_to_text.RecognitionResult.create_from_dict)(result) | Deserializes a serialized RecognitionResult |
| [create_from_list](#panel.widgets.speech_to_text.RecognitionResult.create_from_list)(results) | Deserializes a list of serialized RecognitionResults. |

**Parameter Definitions**

------------------------------------------------------------------------

`alternatives`` ``=`` ``List(bounds=(0,`` ``None),`` ``constant=True,`` ``default=[],`` ``item_type=<class`` ``'panel.widgets.speech_to_text.RecognitionAlternative'>,`` ``label='Alternatives')`
The list of the n-best alternatives

`is_final`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Is`` ``final')`
A Boolean that states whether this result is final (True) or not (False)
— if so, then this is the final time this result will be returned; if
not, then this result is an interim result, and may be updated later on.

classmethod create_from_dict(result)
Deserializes a serialized RecognitionResult

classmethod create_from_list(results)
Deserializes a list of serialized RecognitionResults.

class panel.widgets.speech_to_text.SpeechToText(\*, \_grammars, abort, audio_started, button_hide, button_not_started, button_started, button_type, color, continuous, grammars, interim_results, lang, max_alternatives, results, service_uri, sound_started, speech_started, start, started, stop, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
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
[results_as_html](#panel.widgets.speech_to_text.SpeechToText.results_as_html)
Returns the results formatted as html

[results_deserialized](#panel.widgets.speech_to_text.SpeechToText.results_deserialized)
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

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
