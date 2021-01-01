"""The SpeechToText widget controls the speech recognition service of the browser.

Wraps the HTML5 SpeechRecognition API.
See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition

This functionality is **experimental** and only supported by Chrome and a few other browsers.
Checkout https://caniuse.com/speech-recognition for a up to date list of browsers supporting
the SpeechRecognition Api. Or alternatively
https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility

On some browsers, like Chrome, using Speech Recognition on a web page involves a server-based
recognition engine. Your audio is sent to a web service for recognition processing, so it won't
work offline. Whether this is secure and confidential enough for your use case is up to you
to evaluate."""


from typing import Any, Dict, List

import param
from panel.models.speech_to_text import SpeechToText as _BkSpeechToText
from panel.widgets import Widget
from panel.widgets.speech_to_text_config import LANGUAGE_CODES


class SpeechGrammar(param.Parameterized):
    """A set of words or patterns of words that we want the recognition service to recognize

    For example

    grammar = SpeechGrammar(
        src='#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige;',
        weight=0.7
    )

    Wraps the HTML SpeechGrammar API.
    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammar
    """

    src = param.String(
        doc="""A set of words or patterns of words that we want the recognition service to
        recognize. Defined using JSpeech Grammar Format. See https://www.w3.org/TR/jsgf/.
        """
    )
    uri = param.String(
        doc="""An uri pointing to the definition. If src is available it will be used. Otherwise
        uri. The uri will be loaded on the client side only.
        """
    )
    weight = param.Number(
        default=1,
        bounds=(0.0, 1.0),
        step=0.01,
        doc="""The weight of the grammar. A number in the range 0.0–1.0. Default is 1.""",
    )

    def serialize(self) -> Dict[str, Any]:
        """Returns the grammar as dict"""
        if self.src:
            return {"src": self.src, "weight": self.weight}
        if self.uri:
            return {"uri": self.uri, "weight": self.weight}
        raise ValueError("One of src or uri must be set")


class SpeechGrammarList(list):
    """A list of SpeechGrammar objects containing words or patterns of words that we want the
    recognition service to recognize.

    Example:

    grammar = '#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque ;'
    speechRecognitionList = SpeechGrammarList()
    speechRecognitionList.add_from_string(grammar, 1)

    Wraps the HTML 5 SpeechGrammarList API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechGrammarList
    """

    def add_from_string(self, src: str, weight: float = 1.0) -> SpeechGrammar:
        """Takes a grammar and adds it to the SpeechGrammarList as a new SpeechGrammar object. The
        new speechGrammar object is returned."""
        grammar = SpeechGrammar(src=src, weight=weight)
        self.append(grammar)
        return grammar

    def add_from_uri(self, uri: str, weight: float = 1.0) -> SpeechGrammar:
        """Takes a grammar present at a specific URI, and adds it to the SpeechGrammarList as a new
        SpeechGrammar object. The new SpeechGrammar object is returned.
        """
        grammar = SpeechGrammar(uri=uri, weight=weight)
        self.append(grammar)
        return grammar

    def serialize(self) -> List[Dict]:
        """Returns the grammar list as a list of serialized grammars"""
        return [grammar.serialize() for grammar in self]


class SpeechRecognitionAlternative(param.Parameterized):
    """The SpeechRecognitionAlternative represents a word or
    sentence that has been recognised by the speech recognition service.

    Wraps the HTML5 SpeechRecognitionAlternative API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionAlternative
    """

    confidence = param.Number(
        constant=True,
        bounds=(0.0, 1.0),
        doc="""A numeric estimate of how confident the speech recognition
        system is that the recognition is correct.""",
    )
    transcript = param.String(constant=True, doc="the transcript of the recognised word.")


class SpeechRecognitionResult(param.Parameterized):
    """The SpeechRecognitionResult represents a single recognition match, which may contain
    multiple SpeechRecognitionAlternative objects.

    Wraps the HTML5 SpeechRecognitionResult.

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognitionResult
    """
    is_final = param.Boolean(
        constant=True,
        doc="""A Boolean that states whether this result is final (True) or not (False)
        — if so, then this is the final time this result will be returned; if not, then this
        result is an interim result, and may be updated later on.""",
    )
    alternatives = param.List(
        constant=True,
        doc="""The list of the best alternatives""",
        class_=SpeechRecognitionAlternative,
    )

    @classmethod
    def create_from_dict(cls, result: Dict) -> "SpeechRecognitionResult":
        """Deserializes a serialized SpeechRecognitionResult"""
        alternatives = result.get("alternatives", [])
        _alternatives = []
        for alternative in alternatives:
            _alternatives.append(SpeechRecognitionAlternative(**alternative))
        result["alternatives"] = _alternatives
        return cls(**result)

    @classmethod
    def create_from_list(cls, results: List) -> List["SpeechRecognitionResult"]:
        """Deserializes a list of serialized SpeechRecognitionResult"""
        return [cls.create_from_dict(result) for result in results]


class SpeechToText(Widget): # pylint: disable=too-many-ancestors
    """The SpeechToText widget controls the speech recognition service of the browser.

    Wraps the HTML5 SpeechRecognition API.
    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition

    This functionality is **experimental** and only supported by Chrome and a few other browsers.
    Checkout https://caniuse.com/speech-recognition for a up to date list of browsers supporting
    the SpeechRecognition Api. Or alternatively
    https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition#Browser_compatibility

    On some browsers, like Chrome, using Speech Recognition on a web page involves a server-based
    recognition engine. Your audio is sent to a web service for recognition processing, so it won't
    work offline. Whether this is secure and confidential enough for your use case is up to you
    to evaluate."""
    lang = param.ObjectSelector(
        default="",
        objects=[""] + LANGUAGE_CODES,
        allow_None=True,
        label="Language",
        doc="""The language of the current SpeechRecognition in
        BCP 47 format. For example 'en-US'. If not specified, this defaults to the HTML lang
        attribute value, or the user agent's language setting if that isn't set either.
        """,
    )
    continous = param.Boolean(
        default=False,
        doc="""Controls whether continuous results are returned for each recognition, or only a
        single result. Defaults to False""",
    )
    interim_results = param.Boolean(
        default=False,
        doc="""Controls whether interim results should be returned (True) or not (False.) Interim
        results are results that are not yet final (e.g. the SpeechRecognitionResult.isFinal
        property is False.""",
    )
    max_alternatives = param.Integer(
        default=1,
        bounds=(1, 10),
        doc="""Sets the maximum number of SpeechRecognitionAlternatives provided per result.
        A number between 1 and 10. The default value is 1.""",
    )
    service_uri = param.String(
        doc="""Specifies the location of the speech recognition service used by the current
        SpeechRecognition to handle the actual recognition. The default is the user agent's
        default speech service."""
    )
    grammars = param.ClassSelector(
        class_=SpeechGrammarList,
        doc="""A collection of SpeechGrammar objects that represent the grammars that will be
        understood by the current SpeechRecognition""",
    )
    started = param.Boolean(
        constant=True,
        doc="""Returns True if the Speech Recognition Service is started and False otherwise.""",
    )
    audio_started = param.Boolean(
        constant=True, doc="""Returns True if the Audio is started and False otherwise"""
    )
    sound_started = param.Boolean(
        constant=True, doc="""Returns True if the Sound is started and False otherwise"""
    )
    speech_started = param.Boolean(
        constant=True,
        doc="""Returns True if the the User has started speaking and False otherwise""",
    )
    button_type = param.ObjectSelector(default="light", objects=[
        'default', 'primary', 'success', 'warning', 'danger', 'light'])
    results = param.List(class_=SpeechRecognitionResult, constant=True)
    stop = param.Action(
        doc="""Stops the speech recognition service from listening to incoming audio, and attempts
        to return a SpeechRecognitionResult using the audio captured so far."""
    )
    abort = param.Action(
        doc="""Stops the speech recognition service from listening to incoming audio, and doesn't
        attempt to return a SpeechRecognitionResult."""
    )

    _stops = param.Integer(constant=True, doc="""Integer used to signal the stop action""")
    _aborts = param.Integer(constant=True, doc="""Integer used to signal the abort action""")
    _grammars = param.List(constant=True, doc="""List used to transfer the serialized grammars from
    server to browser""")
    _results = param.List(
        constant=True, doc="""List used to transfer the serialized SpeechRecognitionResults from
        browser to server"""
    )

    _widget_type = _BkSpeechToText

    _rename = {
        "stop": None,
        "abort": None,
        "grammars": None,
        "results": None,
        "_stops": "stops",
        "_aborts": "aborts",
        "_grammars": "grammars",
        "_results": "results",
    }

    def __init__(self, **params):
        super().__init__(**params)

        self.stop = self._stop
        self.abort = self._abort

        if self.grammars:
            self._update_grammars()

    def _stop(self, *_):
        with param.edit_constant(self):
            self._stops += 1

    def _abort(self, *_):
        with param.edit_constant(self):
            self._aborts += 1

    def __repr__(self, depth=None):
        # Custom repr needed to avoid infinite recursion because this Parameterized class has
        # multiple actions
        return f"TextToSpeech(name='{self.name}')"

    @param.depends("grammars", watch=True)
    def _update_grammars(self):
        with param.edit_constant(self):
            if self.grammars:
                self._grammars = self.grammars.serialize() # pylint: disable=no-member
            else:
                self._grammars = []

    @param.depends("_results", watch=True)
    def _update_results(self):
        with param.edit_constant(self):
            self.results = SpeechRecognitionResult.create_from_list(self._results)
            print(self.results)

    @property
    def results_as_html(self) -> str:
        """Returns the `results` formatted as html

        Convenience method for ease of use"""
        if not self.results:
            return "No results"
        html = "<div class='pn-speech-recognition-result'>"
        for index, result in enumerate(self.results):
            if len(self.results)>1:
                html += f"<h3>Result {index}</h3>"
            html += f"""
<span>Is Final: {result.is_final}</span><br/>
"""
            for index2, alternative in enumerate(result.alternatives):
                if len(result.alternatives)>1:
                    html += f"""
<h4>Alternative {index2}</h4>
"""
                html += f"""
<span>Confidence: {alternative.confidence:.2f}</span></br>
<p>
    <strong>{alternative.transcript}</strong>
</p>
"""
        html += "</div>"
        print(html)
        return html