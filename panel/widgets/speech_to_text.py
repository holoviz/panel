"""
The SpeechToText widget controls the speech recognition service of the
browser.

It wraps the HTML5 SpeechRecognition API.  See
https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition

This functionality is **experimental** and only supported by Chrome
and a few other browsers.  Checkout
https://caniuse.com/speech-recognition for a up to date list of
browsers supporting the SpeechRecognition Api. Or alternatively
https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility

On some browsers, like Chrome, using Speech Recognition on a web page
involves a server-based recognition engine. Your audio is sent to a
web service for recognition processing, so it won't work
offline. Whether this is secure and confidential enough for your use
case is up to you to evaluate.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar

import param

from ..models.speech_to_text import SpeechToText as _BkSpeechToText
from .base import Widget
from .button import BUTTON_TYPES

if TYPE_CHECKING:
    from bokeh.model import Model

BUTTON_TYPES = BUTTON_TYPES+['light', 'dark']


class Language(param.Parameterized):

    country = param.String(doc="A country like 'United States'")

    name = param.String(constant=False, doc="""
        The bcp 47 code uniquely identifying the language. For example
        'en-US'.""")

    family = param.String(doc="""
        The overall language family. For example 'English'.""")

    def __str__(self):
        return f"{self.family} - {self.country} ({self.name})"

# Source: https://stackoverflow.com/questions/14257598/what-are-language-codes-in-chromes-implementation-of-the-html5-speech-recogniti
# See also https://cloud.google.com/speech-to-text/docs/languages
LANGUAGES = [
    Language(country='South Africa', family='Afrikaans', name='af-ZA'),
    Language(country='Algeria', family='Arabic', name='ar-DZ'),
    Language(country='Bahrain', family='Arabic', name='ar-BH'),
    Language(country='Egypt', family='Arabic', name='ar-EG'),
    Language(country='Israel', family='Arabic', name='ar-IL'),
    Language(country='Iraq', family='Arabic', name='ar-IQ'),
    Language(country='Jordan', family='Arabic', name='ar-JO'),
    Language(country='Kuwait', family='Arabic', name='ar-KW'),
    Language(country='Lebanon', family='Arabic', name='ar-LB'),
    Language(country='Morocco', family='Arabic', name='ar-MA'),
    Language(country='Oman', family='Arabic', name='ar-OM'),
    Language(country='Palestinian Territory', family='Arabic', name='ar-PS'),
    Language(country='Qatar', family='Arabic', name='ar-QA'),
    Language(country='Saudi Arabia', family='Arabic', name='ar-SA'),
    Language(country='Tunisia', family='Arabic', name='ar-TN'),
    Language(country='UAE', family='Arabic', name='ar-AE'),
    Language(country='Spain', family='Basque', name='eu-ES'),
    Language(country='Bulgaria', family='Bulgarian', name='bg-BG'),
    Language(country='Spain', family='Catalan', name='ca-ES'),
    Language(country='China (Simp.)', family='Chinese Mandarin', name='cmn-Hans-CN'),
    Language(country='Hong Kong SAR (Trad.)', family='Chinese Mandarin', name='cmn-Hans-HK'),
    Language(country='Taiwan (Trad.)', family='Chinese Mandarin', name='cmn-Hant-TW'),
    Language(country='Hong Kong', family='Chinese Cantonese', name='yue-Hant-HK'),
    Language(country='Croatia', family='Croatian', name='hr_HR'),
    Language(country='Czech Republic', family='Czech', name='cs-CZ'),
    Language(country='Denmark', family='Danish', name='da-DK'),
    Language(country='Australia', family='English', name='en-AU'),
    Language(country='Canada', family='English', name='en-CA'),
    Language(country='India', family='English', name='en-IN'),
    Language(country='Ireland', family='English', name='en-IE'),
    Language(country='New Zealand', family='English', name='en-NZ'),
    Language(country='Philippines', family='English', name='en-PH'),
    Language(country='South Africa', family='English', name='en-ZA'),
    Language(country='United Kingdom', family='English', name='en-GB'),
    Language(country='United States', family='English', name='en-US'),
    Language(country='Iran', family='Farsi', name='fa-IR'),
    Language(country='France', family='French', name='fr-FR'),
    Language(country='Philippines', family='Filipino', name='fil-PH'),
    Language(country='Spain', family='Galician', name='gl-ES'),
    Language(country='Germany', family='German', name='de-DE'),
    Language(country='Greece', family='Greek', name='el-GR'),
    Language(country='Finland', family='Finnish', name='fi-FI'),
    Language(country='Israel', family='Hebrew', name='he-IL'),
    Language(country='India', family='Hindi', name='hi-IN'),
    Language(country='Hungary', family='Hungarian', name='hu-HU'),
    Language(country='Indonesia', family='Indonesian', name='id-ID'),
    Language(country='Iceland', family='Icelandic', name='is-IS'),
    Language(country='Italy', family='Italian', name='it-IT'),
    Language(country='Switzerland', family='Italian', name='it-CH'),
    Language(country='Japan', family='Japanese', name='ja-JP'),
    Language(country='Korea', family='Korean', name='ko-KR'),
    Language(country='Lithuania', family='Lithuanian', name='lt-LT'),
    Language(country='Malaysia', family='Malaysian', name='ms-MY'),
    Language(country='Netherlands', family='Dutch', name='nl-NL'),
    Language(country='Norway', family='Norwegian', name='nb-NO'),
    Language(country='Poland', family='Polish', name='pl-PL'),
    Language(country='Brazil', family='Portuguese', name='pt-BR'),
    Language(country='Portugal', family='Portuguese', name='pt-PT'),
    Language(country='Romania', family='Romanian', name='ro-RO'),
    Language(country='Russia', family='Russian', name='ru-RU'),
    Language(country='Serbia', family='Serbian', name='sr-RS'),
    Language(country='Slovakia', family='Slovak', name='sk-SK'),
    Language(country='Slovenia', family='Slovenian', name='sl-SI'),
    Language(country='Argentina', family='Spanish', name='es-AR'),
    Language(country='Bolivia', family='Spanish', name='es-BO'),
    Language(country='Chile', family='Spanish', name='es-CL'),
    Language(country='Colombia', family='Spanish', name='es-CO'),
    Language(country='Costa Rica', family='Spanish', name='es-CR'),
    Language(country='Dominican Republic', family='Spanish', name='es-DO'),
    Language(country='Ecuador', family='Spanish', name='es-EC'),
    Language(country='El Salvador', family='Spanish', name='es-SV'),
    Language(country='Guatemala', family='Spanish', name='es-GT'),
    Language(country='Honduras', family='Spanish', name='es-HN'),
    Language(country='México', family='Spanish', name='es-MX'),
    Language(country='Nicaragua', family='Spanish', name='es-NI'),
    Language(country='Panamá', family='Spanish', name='es-PA'),
    Language(country='Paraguay', family='Spanish', name='es-PY'),
    Language(country='Perú', family='Spanish', name='es-PE'),
    Language(country='Puerto Rico', family='Spanish', name='es-PR'),
    Language(country='Spain', family='Spanish', name='es-ES'),
    Language(country='Uruguay', family='Spanish', name='es-UY'),
    Language(country='United States', family='Spanish', name='es-US'),
    Language(country='Venezuela', family='Spanish', name='es-VE'),
    Language(country='Sweden', family='Swedish', name='sv-SE'),
    Language(country='Thailand', family='Thai', name='th-TH'),
    Language(country='Turkey', family='Turkish', name='tr-TR'),
    Language(country='Ukraine', family='Ukrainian', name='uk-UA'),
    Language(country='Viet Nam', family='Vietnamese', name='vi-VN'),
    Language(country='South Africa', family='Zulu', name='zu-ZA'),
]
LANGUAGES.sort(key=lambda x: x.name)
LANGUAGE_CODES = [lang.name for lang in LANGUAGES]


class Grammar(param.Parameterized):
    """A set of words or patterns of words that we want the speech recognition service to recognize

    For example

    grammar = Grammar(
        src='#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige;',
        weight=0.7
    )

    Wraps the HTML SpeechGrammar API.
    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammar
    """

    src = param.String(doc="""
        A set of words or patterns of words that we want the
        recognition service to recognize. Defined using JSpeech
        Grammar Format. See https://www.w3.org/TR/jsgf/.""")

    uri = param.String(doc="""
        An uri pointing to the definition. If src is available it will
        be used. Otherwise uri. The uri will be loaded on the client
        side only.""")

    weight = param.Number(default=1, bounds=(0.0, 1.0), step=0.01, doc="""
       The weight of the grammar. A number in the range 0–1. Default is 1.""")

    def serialize(self):
        """Returns the grammar as dict"""
        if self.src:
            return {"src": self.src, "weight": self.weight}
        if self.uri:
            return {"uri": self.uri, "weight": self.weight}
        raise ValueError("One of src or uri must be set")


class GrammarList(list):
    """A list of Grammar objects containing words or patterns of words that we want the
    recognition service to recognize.

    Example:

    grammar = '#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque ;'
    grammar_list = GrammarList()
    grammar_list.add_from_string(grammar, 1)

    Wraps the HTML 5 SpeechGrammarList API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammarList
    """

    def add_from_string(self, src, weight=1.0):
        """
        Takes a src and weight and adds it to the GrammarList as a new
        Grammar object. The new Grammar object is returned.
        """
        grammar = Grammar(src=src, weight=weight)
        self.append(grammar)
        return grammar

    def add_from_uri(self, uri, weight=1.0):
        """
        Takes a grammar present at a specific uri, and adds it to the
        GrammarList as a new Grammar object. The new Grammar object is
        returned.
        """
        grammar = Grammar(uri=uri, weight=weight)
        self.append(grammar)
        return grammar

    def serialize(self):
        """Returns a list of serialized grammars"""
        return [grammar.serialize() for grammar in self]


class RecognitionAlternative(param.Parameterized):
    """The RecognitionAlternative represents a word or
    sentence that has been recognised by the speech recognition service.

    Wraps the HTML5 SpeechRecognitionAlternative API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionAlternative
    """

    confidence = param.Number(bounds=(0.0, 1.0), constant=True, doc="""
        A numeric estimate between 0 and 1 of how confident the speech recognition
        system is that the recognition is correct.""")

    transcript = param.String(constant=True, doc="""
        The transcript of the recognised word or sentence.""")


class RecognitionResult(param.Parameterized):
    """The Result represents a single recognition match, which may contain
    multiple RecognitionAlternative objects.

    Wraps the HTML5 SpeechRecognitionResult API.

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult
    """

    alternatives = param.List(item_type=RecognitionAlternative, constant=True, doc="""
        The list of the n-best alternatives""")

    is_final = param.Boolean(constant=True, doc="""
        A Boolean that states whether this result is final (True) or
        not (False) — if so, then this is the final time this result
        will be returned; if not, then this result is an interim
        result, and may be updated later on.""")

    @classmethod
    def create_from_dict(cls, result):
        """
        Deserializes a serialized RecognitionResult
        """
        result = result.copy()
        alternatives = result.get("alternatives", [])
        _alternatives = []
        for alternative in alternatives:
            _alternatives.append(RecognitionAlternative(**alternative))
        result["alternatives"] = _alternatives
        return cls(**result)

    @classmethod
    def create_from_list(cls, results):
        """
        Deserializes a list of serialized RecognitionResults.
        """
        return [cls.create_from_dict(result) for result in results]


class SpeechToText(Widget):
    """
    The SpeechToText widget controls the speech recognition service of
    the browser.

    It wraps the HTML5 SpeechRecognition API.  See
    https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition

    Reference: https://panel.holoviz.org/reference/widgets/SpeechToText.html

    :Example:

    >>> SpeechToText(button_type="light")

    This functionality is **experimental** and only supported by
    Chrome and a few other browsers.  Checkout
    https://caniuse.com/speech-recognition for a up to date list of
    browsers supporting the SpeechRecognition Api. Or alternatively
    https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility

    On some browsers, like Chrome, using Speech Recognition on a web
    page involves a server-based recognition engine. Your audio is
    sent to a web service for recognition processing, so it won't work
    offline. Whether this is secure and confidential enough for your
    use case is up to you to evaluate.
    """

    abort = param.Event(doc="""
        Stops the speech recognition service from listening to
        incoming audio, and doesn't attempt to return a
        RecognitionResult.""")

    start = param.Event(doc="""
        Starts the speech recognition service listening to incoming
        audio with intent to recognize grammars associated with the
        current SpeechRecognition.""")

    stop = param.Event(doc="""
        Stops the speech recognition service from listening to
        incoming audio, and attempts to return a RecognitionResult
        using the audio captured so far.""")

    lang = param.Selector(default="", objects=[""] + LANGUAGE_CODES,
                                allow_None=True, label="Language", doc="""
        The language of the current SpeechRecognition in BCP 47
        format. For example 'en-US'. If not specified, this defaults
        to the HTML lang attribute value, or the user agent's language
        setting if that isn't set either.  """)

    continuous = param.Boolean(default=False, doc="""
        Controls whether continuous results are returned for each
        recognition, or only a single result. Defaults to False""")

    interim_results = param.Boolean(default=False, doc="""
        Controls whether interim results should be returned (True) or
        not (False.) Interim results are results that are not yet
        final (e.g. the RecognitionResult.is_final property is
        False).""")

    max_alternatives = param.Integer(default=1, bounds=(1, 5), doc="""
        Sets the maximum number of RecognitionAlternatives provided
        per result.  A number between 1 and 5. The default value is
        1.""")

    service_uri = param.String(doc="""
        Specifies the location of the speech recognition service used
        by the current SpeechRecognition to handle the actual
        recognition. The default is the user agent's default speech
        service.""")

    grammars = param.ClassSelector(class_=GrammarList, doc="""
        A GrammarList object that represents the grammars that will be
        understood by the current SpeechRecognition service""")

    button_hide = param.Boolean(default=False, label="Hide the Button", doc="""
        If True no button is shown. If False a toggle Start/ Stop button is shown.""")

    button_type = param.Selector(default="light", objects=BUTTON_TYPES, doc="""
        The button styling.""")

    button_not_started = param.String(label="Button Text when not started", doc="""
        The text to show on the button when the SpeechRecognition
        service is NOT started.  If '' a *muted microphone* icon is
        shown.""")

    button_started = param.String(label="Button Text when started", doc="""
        The text to show on the button when the SpeechRecognition
        service is started. If '' a *muted microphone* icon is
        shown.""")

    started = param.Boolean(constant=True, doc="""
        Returns True if the Speech Recognition Service is started and
        False otherwise.""")

    audio_started = param.Boolean(constant=True, doc="""
        Returns True if the Audio is started and False otherwise.""")

    sound_started = param.Boolean(constant=True, doc="""
        Returns True if the Sound is started and False otherwise.""")

    speech_started = param.Boolean(constant=True, doc="""
        Returns True if the the User has started speaking and False otherwise.""")

    results = param.List(constant=True, doc="""
        The `results` as a list of Dictionaries.""")

    value = param.String(default="", constant=True, label="Last Result", doc="""
        The transcipt of the highest confidence RecognitionAlternative
        of the last RecognitionResult. Please note we strip the
        transcript for leading spaces.""")

    _grammars = param.List(constant=True, doc="""
        List used to transfer the serialized grammars from server to
        browser.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'grammars': None, '_grammars': 'grammars', 'name': None, 'value': None,
    }

    _widget_type: ClassVar[type[Model]] = _BkSpeechToText

    def __init__(self, **params):
        super().__init__(**params)
        if self.grammars:
            self._update_grammars()

    def __repr__(self, depth=None):
        # Custom repr needed to avoid infinite recursion because this Parameterized class has
        # multiple actions
        return f"SpeechToText(name='{self.name}')"

    @param.depends('grammars', watch=True)
    def _update_grammars(self):
        with param.edit_constant(self):
            if self.grammars:
                self._grammars = self.grammars.serialize()  # pylint: disable=no-member
            else:
                self._grammars = []

    @param.depends('results', watch=True)
    def _update_results(self):
        # pylint: disable=unsubscriptable-object
        with param.edit_constant(self):
            if self.results and 'alternatives' in self.results[-1]:
                self.value = (self.results[-1]['alternatives'][0]['transcript']).lstrip()
            else:
                self.value = ''

    @property
    def results_deserialized(self):
        """
        Returns the results as a List of RecognitionResults
        """
        return RecognitionResult.create_from_list(self.results)

    @property
    def results_as_html(self) -> str:
        """
        Returns the `results` formatted as html

        Convenience method for ease of use
        """
        if not self.results:
            return 'No results'
        html = '<div class="pn-speech-recognition-result">'
        total = len(self.results) - 1
        for index, result in enumerate(reversed(self.results_deserialized)):
            if len(self.results) > 1:
                html += f'<h3>Result {total-index}</h3>'
            html += f'<span>Is Final: {result.is_final}</span><br/>'
            for index2, alternative in enumerate(result.alternatives):
                if len(result.alternatives) > 1:
                    html += f'<h4>Alternative {index2}</h4>'
                html += f"""
                <span>Confidence: {alternative.confidence:.2f}</span>
                </br>
                <p>
                  <strong>{alternative.transcript}</strong>
                </p>
                """
        html += '</div>'
        return html
