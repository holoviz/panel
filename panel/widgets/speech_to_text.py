from panel.widgets.speech_to_text_config import LANGUAGES, LANGUAGE_CODES
import param
from panel.models.speech_to_text import SpeechToText as _BkSpeechToText
from panel.widgets import Widget

class SpeechGrammer:
    pass


class SpeechGrammerList:
    pass


class SpeechRecognitionAlternative:
    pass


class SpeechRecognitionError:
    pass


class SpeechRecognitionEvent:
    pass


class SpeechRecognitionResult:
    pass


class SpeechRecognitionResultList:
    pass


class SpeechToText(Widget):
    """Controls the speech recognition service.

    Wraps the HTML5 SpeechRecognition API.
    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition

    This functionality is **experimental** and only supported by Chrome and a few other browsers.
    Checkout https://caniuse.com/speech-recognition for a up to date list of browsers supporting
    the SpeechRecognition Api.

    On some browsers, like Chrome, using Speech Recognition on a web page involves a server-based
    recognition engine. Your audio is sent to a web service for recognition processing, so it won't
    work offline."""

    start = param.Action(
        doc="""Starts the speech recognition service listening to incoming audio with intent to
        recognize grammars associated with the current SpeechRecognition."""
    )
    stop = param.Action(
        doc="""Stops the speech recognition service from listening to incoming audio, and attempts
        to return a SpeechRecognitionResult using the audio captured so far."""
    )
    abort = param.Action(
        doc="""Stops the speech recognition service from listening to incoming audio, and doesn't
        attempt to return a SpeechRecognitionResult."""
    )
    lang = param.ObjectSelector(
        objects=[None]+LANGUAGE_CODES,
        allow_None=True,
        label="Language",
        doc="""The language of the current SpeechRecognition in
        BCP 47 format. For example 'en-US'. If not specified, this defaults to the HTML lang
        attribute value, or the user agent's language setting if that isn't set either.
        """
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
        class_=SpeechGrammerList,
        doc="""A collection of SpeechGrammar objects that represent the grammars that will be
        understood by the current SpeechRecognition""",
    )

    _starts = param.Integer(constant=True, doc="""Integer used to signal the start action""")
    _stops = param.Integer(constant=True, doc="""Integer used to signal the stop action""")
    _aborts = param.Integer(constant=True, doc="""Integer used to signal the abort action""")

    _widget_type = _BkSpeechToText

    _rename = {
        "start": None,
        "stop": None,
        "abort": None,
        "_starts": "starts",
        "_stops": "stops",
        "_aborts": "aborts",
    }

    def __init__(self, **params):
        super().__init__(**params)

        self.start = self._start
        self.stop = self._stop
        self.abort = self._abort

    def _start(self, *_):
        with param.edit_constant(self):
            self._starts +=1

    def _stop(self, *_):
        with param.edit_constant(self):
            self._stops +=1

    def _abort(self, *_):
        with param.edit_constant(self):
            self._aborts +=1


    def __repr__(self, depth=None):
        # Custom repr needed to avoid infinite recursion because this Parameterized class has
        # multiple actions
        return f"TextToSpeech(name='{self.name}')"

