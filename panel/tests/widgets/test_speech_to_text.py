from os import stat_result

import panel as pn
import pytest
from panel.widgets import (SpeechGrammer, SpeechGrammerList, SpeechToText,
                           speech_to_text)
from panel.widgets.speech_to_text import (SpeechRecognitionAlternative,
                                          SpeechRecognitionError,
                                          SpeechRecognitionEvent,
                                          SpeechRecognitionResult,
                                          SpeechRecognitionResultList)

CLASSES = [
    SpeechGrammer,
    SpeechGrammerList,
    SpeechToText,
    SpeechRecognitionAlternative,
    SpeechRecognitionError,
    SpeechRecognitionEvent,
    SpeechRecognitionResult,
    SpeechRecognitionResultList,
]


@pytest.mark.parametrize("class_", CLASSES)
def test_constructor(class_):
    class_()

def test_get_app():
    speech_to_text = SpeechToText()
    speech_to_text_settings = pn.Param(
        speech_to_text,
        parameters = [
            "start", "stop", "abort", "grammars", "lang", "continous", "interim_results", "max_alternatives", "service_uri", "_starts", "_stops", "_aborts"
        ]
    )
    app = pn.Column(
        pn.pane.Markdown("# Panel - Speech to Text App"),
        speech_to_text,
        speech_to_text_settings,
    )
    return app

if __name__.startswith("bokeh"):
    test_get_app().servable()
