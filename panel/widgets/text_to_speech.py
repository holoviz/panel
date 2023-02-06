"""
The Panel TextToSpeak Widget provides functionality for *text to
speech* via the the HTML5 SpeechSynthesis API.

See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis

The term *utterance* is used throughout the API. It is the smallest
unit of speech in spoken language analysis.
"""
from __future__ import annotations

import uuid

from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Type,
)

import param

from panel.widgets import Widget

from ..models.text_to_speech import TextToSpeech as _BkTextToSpeech

if TYPE_CHECKING:
    from bokeh.model import Model


class Voice(param.Parameterized):
    """
    The current device (i.e. OS and Browser) provides a list of
    Voices. Each with a unique name and speaking a specific language.

    Wraps the HTML5 SpeecSynthesisVoice API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice
    """

    default = param.Boolean(constant=True, default=False, doc="""
        A Boolean indicating whether the voice is the default voice
        for the current app language (True), or not (False.)""")

    lang = param.String(constant=True, doc="""
        Returns a BCP 47 language tag indicating the language of the voice.""")

    local_service = param.Boolean(constant=True, doc="""
        A Boolean indicating whether the voice is supplied by a local
        speech synthesizer service (True), or a remote speech
        synthesizer service (False.)""")

    name = param.String(constant=True, doc="""
        Returns a human-readable name that represents the voice.""")

    voice_uri = param.String(constant=True, doc="""
        Returns the type of URI and location of the speech synthesis
        service for this voice.""")

    @staticmethod
    def to_voices_list(voices):
        """Returns a list of Voice objects from the list of dicts provided"""
        result = []
        for _voice in voices:  # pylint: disable=not-an-iterable
            voice = Voice(**_voice)
            result.append(voice)
        return result

    @staticmethod
    def group_by_lang(voices):
        """Returns a dictionary where the key is the `lang` and the value is a list of voices
        for that language."""
        if not voices:
            return {}

        sorted_lang = sorted(list(set(voice.lang for voice in voices)))
        result = {lang: [] for lang in sorted_lang}
        for voice in voices:
            result[voice.lang].append(voice)
        result = {key: sorted(value, key=lambda x: x.name) for key, value in result.items()}
        return result


class Utterance(param.Parameterized):
    """
    An *utterance* is the smallest unit of speech in spoken language analysis.

    The Utterance Model wraps the HTML5 SpeechSynthesisUtterance API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance
    """

    value = param.String(default="", doc="""
        The text that will be synthesised when the utterance is
        spoken. The text may be provided as plain text, or a
        well-formed SSML document.""")

    lang = param.ObjectSelector(default="", doc="""
        The language of the utterance.""")

    pitch = param.Number(default=1.0, bounds=(0.0, 2.0), doc="""
        The pitch at which the utterance will be spoken at expressed
        as a number between 0 and 2.""")

    rate = param.Number(default=1.0, bounds=(0.1, 10.0), doc="""
        The speed at which the utterance will be spoken at expressed
        as a number between 0.1 and 10.""" )

    voice = param.ObjectSelector(doc="""
        The voice that will be used to speak the utterance.""")

    volume = param.Number(default=1.0, bounds=(0.0, 1.0), doc=""" The
        volume that the utterance will be spoken at expressed as a
        number between 0 and 1.""")

    def __init__(self, **params):
        voices = params.pop('voices', [])
        super().__init__(**params)
        self._voices_by_language = {}
        self.set_voices(voices)

    def to_dict(self, include_uuid=True):
        """Returns the object parameter values in a dictionary

        Returns:
            Dict: [description]
        """
        result = {
            "lang": self.lang,
            "pitch": self.pitch,
            "rate": self.rate,
            "text": self.value,
            "volume": self.volume,
        }
        if self.voice and self.voice.name:
            result["voice"] = self.voice.name
        if include_uuid:
            result["uuid"] = str(uuid.uuid4())
        return result

    def set_voices(self, voices):
        """Updates the `lang` and `voice` parameter objects, default and value"""
        if not voices:
            self.param.lang.objects = ["en-US"]
            self.param.lang.default = "en-US"
            self.lang = "en-US"
            return

        self._voices_by_language = Voice.group_by_lang(voices)
        self.param.lang.objects = list(self._voices_by_language.keys())
        if "en-US" in self._voices_by_language:
            default_lang = "en-US"
        else:
            default_lang = list(self._voices_by_language.keys())[0]
        self.param.lang.default = default_lang
        self.lang = default_lang
        self.param.trigger("lang")

    @param.depends("lang", watch=True)
    def _handle_lang_changed(self):
        if not self._voices_by_language or not self.lang:
            self.param.voice.default = None
            self.voice = None
            self.param.voice.objects = []
            return

        voices = self._voices_by_language[self.lang]
        if self.voice and self.voice in voices:
            default_voice = self.voice
        else:
            default_voice = voices[0]
            for voice in voices:
                if voice.default:
                    default_voice = voice

        self.param.voice.objects = voices
        self.param.voice.default = default_voice
        self.voice = default_voice


class TextToSpeech(Utterance, Widget):
    """
    The `TextToSpeech` widget wraps the HTML5 SpeechSynthesis API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis

    Reference: https://panel.holoviz.org/reference/widgets/TextToSpeech.html

    :Example:

    >>> TextToSpeech(name="Speech Synthesis", value="Data apps are nice")
    """

    auto_speak = param.Boolean(default=True, doc="""
        Whether or not to automatically speak when the value changes.""")

    cancel = param.Event(doc="""
        Removes all utterances from the utterance queue.""")

    pause = param.Event(doc="""
        Puts the TextToSpeak object into a paused state.""")

    resume = param.Event(doc="""
        Puts the TextToSpeak object into a non-paused state: resumes
        it if it was already paused.""")

    paused = param.Boolean(readonly=True, doc="""
        A Boolean that returns true if the TextToSpeak object is in a
        paused state.""")

    pending = param.Boolean(readonly=True, doc="""
        A Boolean that returns true if the utterance queue contains
        as-yet-unspoken utterances.""")

    speak = param.Event(doc="""
        Speak. I.e. send a new Utterance to the browser""")

    speaking = param.Boolean(readonly=True, doc="""
        A Boolean that returns true if an utterance is currently in
        the process of being spoken — even if TextToSpeak is in a
        paused state.""")

    voices = param.List(readonly=True, doc="""
        Returns a list of Voice objects representing all the available
        voices on the current device.""")

    _voices = param.List()

    _rename: ClassVar[Mapping[str, str | None]] = {
        'auto_speak': None, 'lang': None, 'name': None, 'pitch': None,
        'rate': None, 'speak': None, 'value': None, 'voice': None,
        'voices': None, 'volume': None, '_voices': 'voices',
    }

    _widget_type: ClassVar[Type[Model]] = _BkTextToSpeech

    def _process_param_change(self, msg):
        speak = msg.get('speak') or ('value' in msg and self.auto_speak)
        msg = super()._process_param_change(msg)
        if speak:
            msg['speak'] = self.to_dict()
        return msg

    @param.depends('_voices', watch=True)
    def _update_voices(self):
        voices = []
        for _voice in self._voices:  # pylint: disable=not-an-iterable
            voice = Voice(**_voice)
            voices.append(voice)
        self.voices = voices
        self.set_voices(self.voices)

    def __repr__(self, depth=None):
        # We need to do this because otherwise a error is raised when used in notebook
        # due to infinite recursion
        return f'TextToSpeech(name={self.name!r})'

    def __str__(self):
        return f'TextToSpeech(name={self.name!r})'
