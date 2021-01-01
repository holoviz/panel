"""Bokeh Model of the Panel SpeechToText widget"""
from bokeh.core.properties import Int, String, List, Dict, Any
from bokeh.core.property.primitive import Bool
from bokeh.models.widgets.widget import Widget

class SpeechToText(Widget):
    """Bokeh Model of the Panel SpeechToText widget

    Controls the speech recognition service.

    On some browsers, like Chrome, using Speech Recognition on a web page involves a server-based
    recognition engine. Your audio is sent to a web service for recognition processing, so it won't
    work offline.

    Wraps the HTML5 SpeechRecognition API.
    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition"""
    stops = Int()
    aborts = Int()

    grammars = List(Dict(String,Any))
    lang = String()
    continous = Bool()
    interim_results = Bool()
    max_alternatives = Int()
    service_uri = String()

    started = Bool()
    audio_started = Bool()
    sound_started = Bool()
    speech_started = Bool()
    button_type = String()

    results = List(Dict(String, Any))
