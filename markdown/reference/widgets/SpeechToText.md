# SpeechToText
---
```python
import panel as pn

from panel.widgets import SpeechToText, GrammarList

pn.extension()
```

The `SpeechToText` widget controls the speech recognition service of the browser by wrapping the [HTML5 `SpeechRecognition` API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition).

The functionality is **experimental** and **only supported by Chrome and a few other browsers**. See https://caniuse.com/speech-recognition or https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility for an up-to-date list of browsers supporting the SpeechRecognition API. Even in Chrome the `grammars`, `interim_results` and `max_alternatives` parameters are not yet supported.

On some browsers, like Chrome, using Speech Recognition on a web page involves a server-based recognition engine. **Your audio is sent to a web service for recognition processing, so it won't work offline**. Whether this is secure and confidential enough for your use case is up to you to evaluate.

#### Parameters:

* **``results``** (List\[Dict\]): The results recognized. A list of Dictionaries.
* **``value``** (str): The most recent SpeechRecognition result as a string.

* **``lang``** (str): The language of the current SpeechRecognition service in BCP 47 format. For example 'en-US'.
* **``continuous``** (bool): Controls whether continuous results are returned for each recognition, or only a single result. Defaults to False.
* **``interim_results``** (boolean): Controls whether interim results should be returned (True) or not (False.) Interim results are results that are not yet final (e.g. the RecognitionResult.is_final property is False).
* **``max_alternatives``** (int): Sets the maximum number of RecognitionAlternatives provided per result. A number between 1 and 5. The default value is 1.
* **``service_uri``** (str): Specifies the location of the speech recognition service used by the current SpeechRecognition service to handle the actual recognition. The default is the user agent's default speech service.
* **``grammars``** (GrammarList): A GrammarList object that represents the grammars that will be understood by the current SpeechRecognition service.

* **``started``** (boolean): Returns True if the Speech Recognition Service is started and False otherwise.
* **``audio_started``** (boolean): Returns True if the Audio is started and False otherwise
* **``sound_started``** (boolean): Returns True if the Sound is started and False otherwise
* **``speech_started``** (boolean): Returns True if the the User has started speaking and False otherwise

* **``button_hide``** (bool): Whether to show (False) or hide (True) the toggle start/ stop button.
* **``color``** (str): One of 'default', 'primary', 'success', 'warning', 'danger' and 'light'.
* **``button_not_started``** (str): The text to show on the button when the SpeechRecognition service is NOT started. If '' a *muted microphone* icon is shown.
* **``button_started``** (str): The text to show on the button when the SpeechRecognition service is started. If '' a *muted microphone* icon is shown.

##### Events

Events are transient boolean parameters which when set to true trigger an event and then immediately revert to False.

* **``start``** (bool): Starts the speech recognition service listening to incoming audio with intent to recognize grammars associated with the current SpeechRecognition.
* **``stop``** (bool): Stops the speech recognition service from listening to incoming audio, and attempts to return a list of RecognitionResult using the audio captured so far.
* **``abort``** (bool): Stops the speech recognition service from listening to incoming audio, and doesn't attempt to return a list of RecognitionResult.

#### Properties

* **``results_deserialized``** (List\[RecognitionResult\]): The results recognized. A list of RecognitionResult objects.
* **``results_as_html``** (str): Returns the `results` formatted as html. Convenience property for ease of use.

### Grammar

A set of words or patterns of words that we want the speech recognition service to recognize.

For example

```python
grammar = Grammar(
    src='#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige;',
    weight=0.7
)
```

Wraps the [HTML SpeechGrammar API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammar).

#### Parameters:

* **``src``** (str): A set of words or patterns of words that we want the recognition service to recognize. Defined using JSpeech Grammar Format. See https://www.w3.org/TR/jsgf/.
* **``uri``** (str): An uri pointing to the definition. If src is available it will be used. Otherwise uri. The uri will be loaded on the client side only.
* **``weight``** (float): The weight of the grammar. A number in the range 0–1. Default is 1.

### GrammarList

A list of Grammar objects containing words or patterns of words that we want the recognition service to recognize.

For example

```python
grammar = '#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque ;'
grammar_list = GrammarList()
grammar_list.add_from_string(grammar, 1)
```

Wraps the [HTML 5 SpeechGrammarList API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammarList).

#### Methods:

* **``add_from_string``** (src: str, weight: float): Takes a grammar src and weight and adds it to the GrammarList as a new Grammar object. The new Grammar object is returned.
* **``add_from_uri``** (uri: str, weight: float): Takes a grammar uri and weight and adds it to the GrammarList as a new Grammar object. The new Grammar object is returned.

### RecognitionAlternative

The RecognitionAlternative represents a word or sentence that has been recognised by the speech recognition service.

Wraps the [HTML5 SpeechRecognitionAlternative API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionAlternative).

#### Methods:

* **``confidence``** (float): A numeric estimate between 0 and 1 of how confident the speech recognition system is that the recognition is correct.
* **``transcript``** (str): The transcript of the recognised word or sentence.

### RecognitionResult

The Result represents a single recognition match, which may contain multiple RecognitionAlternative objects.

Wraps the [HTML5 SpeechRecognitionResult API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult).

#### Methods:

* **``is_final``** (boolean): A Boolean that states whether this result is final (True) or not (False) — if so, then this is the final time this result will be returned; if not, then this result is an interim result, and may be updated later on.
* **``alternatives``** (List\[RecognitionResult\]): The list of the n-best alternatives.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
speech_to_text_basic = SpeechToText(color="light")

pn.Row(speech_to_text_basic.controls(['value'], jslink=False), speech_to_text_basic)
```

To get the most recent result we can simply access the `value` parameter:

```python
speech_to_text_basic.value
```

For more detailed results including the confidence level access the `results` parameter:

```python
speech_to_text_basic.results
```

### Advanced Example

We start by instantiating a `SpeechToText` object with a `GrammarList`:

```python
grammar_list = GrammarList()

src = "#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque | black | blue | brown | chocolate | coral | crimson | cyan | fuchsia | ghostwhite | gold | goldenrod | gray | green | indigo | ivory | khaki | lavender | lime | linen | magenta | maroon | moccasin | navy | olive | orange | orchid | peru | pink | plum | purple | red | salmon | sienna | silver | snow | tan | teal | thistle | tomato | turquoise | violet | white | yellow ;"
grammar_list.add_from_string(src, 1)

speech_to_text = SpeechToText(color="light", grammars=grammar_list, height=50)

controls = speech_to_text.controls(jslink=False)
```

Next we create a callback which will render the `results_as_html`:

```python
def results(results):
    return pn.pane.HTML(speech_to_text.results_as_html, width=100, margin=(0, 15, 0, 15))
```

Finally we compose this into an `app`

```python
app = pn.Row(controls, speech_to_text, pn.bind(results, speech_to_text))
app.servable()
```

Try changing some of the parameters. For example changing the `continuous` parameter will keep the SpeechRecognition service open which lets you say multiple statements after each other.

---
