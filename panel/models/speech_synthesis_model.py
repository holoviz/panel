"""Bokeh Model for the HTML5 SpeechSynthesis API

See Wrapper of the HTML5 SpeecSynthesisVoice API

See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice
"""
from bokeh.core.properties import (
    Any,
    Bool,
    Dict,
    Either,
    Enum,
    Float,
    Int,
    List,
    Override,
    String,
    Tuple,
)
from bokeh.models.layouts import HTMLBox
from bokeh.models.widgets import InputWidget, Widget


class SpeechSynthesisModel(Widget):
    """Wrapper of the HTML5 SpeechSynthesis API

    See https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis

    Please note an *utterance* is the smallest unit of speech in spoken language analysis.
    """

    paused = Bool()
    pending = Bool()
    speaking = Bool()

    voices = List(Dict(String, Any))

    cancels = Int()
    pauses = Int()
    resumes = Int()
    speaks = Dict(String, Any)
