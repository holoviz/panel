"""Bokeh Model of the Panel SpeechToText widget"""
from bokeh.core.properties import Any, Bool, Dict, Int, List, String
from bokeh.models.widgets.widget import Widget


class SpeechToText(Widget):
    """
    Bokeh Model of the Panel SpeechToText widget

    Controls the speech recognition service.

    On some browsers, like Chrome, using Speech Recognition on a web
    page involves a server-based recognition engine. Your audio is
    sent to a web service for recognition processing, so it won't work
    offline.

    Wraps the HTML5 SpeechRecognition API.  See
    https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
    """

    start = Bool()
    stop = Bool()
    abort = Bool()

    grammars = List(Dict(String,Any))
    lang = String()
    continuous = Bool()
    interim_results = Bool()
    max_alternatives = Int()
    service_uri = String()

    started = Bool()
    audio_started = Bool()
    sound_started = Bool()
    speech_started = Bool()

    button_type = String()
    button_hide = Bool()
    button_not_started = String()
    button_started = String()

    results = List(Dict(String, Any))
