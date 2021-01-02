import panel as pn
import pytest
from panel.widgets import Grammar, GrammarList, SpeechToText
from panel.widgets.speech_to_text import RecognitionAlternative, RecognitionResult

CLASSES = [
    Grammar,
    GrammarList,
    SpeechToText,
    RecognitionAlternative,
    RecognitionResult,
]


@pytest.mark.parametrize("class_", CLASSES)
def test_constructor(class_):
    class_()


def test_can_construct_speech_grammar_from_src():
    # Given
    src = "#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige;"
    weight = 0.7
    # When
    grammar = Grammar(
        src=src,
        weight=weight,
    )
    serialized = grammar.serialize()
    # Then
    assert serialized == {"src": src, "weight": weight}


def test_can_construct_speech_grammar_from_uri():
    # Given
    uri = "http://www.example.com/grammar.txt"
    weight = 0.7
    # When
    grammar = Grammar(
        uri=uri,
        weight=weight,
    )
    serialized = grammar.serialize()
    # Then
    assert serialized == {"uri": uri, "weight": weight}


def test_add_from_string_to_speech_grammar_list():
    # Given
    src = "#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque | black | blue | brown | chocolate | coral | crimson | cyan | fuchsia | ghostwhite | gold | goldenrod | gray | green | indigo | ivory | khaki | lavender | lime | linen | magenta | maroon | moccasin | navy | olive | orange | orchid | peru | pink | plum | purple | red | salmon | sienna | silver | snow | tan | teal | thistle | tomato | turquoise | violet | white | yellow ;"
    weight = 0.5
    grammar_list = GrammarList()
    # When
    result = grammar_list.add_from_string(src, weight)
    serialized = grammar_list.serialize()
    # Then
    assert isinstance(result, Grammar)
    assert result in grammar_list
    assert serialized == [{"src": src, "weight": weight}]


def test_add_from_uri_to_speech_grammar_list():
    # Given
    uri = "http://www.example.com/grammar.txt"
    weight = 0.5
    grammar_list = GrammarList()
    # When
    result = grammar_list.add_from_uri(uri, weight)
    serialized = grammar_list.serialize()
    # Then
    assert isinstance(result, Grammar)
    assert result in grammar_list
    assert serialized == [{"uri": uri, "weight": weight}]


def test_can_deserialize_alternative():
    # Given
    alternative = {"confidence": 0.9190853834152222, "transcript": "but why"}
    # When
    actual = RecognitionAlternative(**alternative)
    # Then
    assert actual.confidence == alternative["confidence"]
    assert actual.transcript == alternative["transcript"]


def test_can_create_result_from_dict():
    # Given
    result = {
        "is_final": True,
        "alternatives": [{"confidence": 0.9190853834152222, "transcript": "and why"}],
    }
    # When
    actual = RecognitionResult.create_from_dict(result)
    # Then
    assert actual.is_final == result["is_final"]
    assert len(actual.alternatives) == 1
    assert actual.alternatives[0].confidence == 0.9190853834152222
    assert actual.alternatives[0].transcript == "and why"


def test_can_create_result_from_list():
    # Given
    results = [
        {
            "is_final": True,
            "alternatives": [{"confidence": 0.9190853834152222, "transcript": "and why"}],
        }
    ]
    # When
    actual = RecognitionResult.create_from_list(results)
    # Then
    assert len(actual) == 1
    assert actual[0].is_final == results[0]["is_final"]
    assert len(actual[0].alternatives) == 1
    assert actual[0].alternatives[0].confidence == 0.9190853834152222
    assert actual[0].alternatives[0].transcript == "and why"


def test_get_app():
    src = "#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque | black | blue | brown | chocolate | coral | crimson | cyan | fuchsia | ghostwhite | gold | goldenrod | gray | green | indigo | ivory | khaki | lavender | lime | linen | magenta | maroon | moccasin | navy | olive | orange | orchid | peru | pink | plum | purple | red | salmon | sienna | silver | snow | tan | teal | thistle | tomato | turquoise | violet | white | yellow ;"
    speech_to_text = SpeechToText(button_type="success", continuous=True)

    grammar_list = GrammarList()
    grammar_list.add_from_string(src, 1)
    speech_to_text.grammars = grammar_list
    results_as_html_panel = pn.pane.Markdown(margin=(0, 15, 0, 15))

    @pn.depends(speech_to_text.param.results_serialized, watch=True)
    def update_results_html_panel(results_serialized):
        results_as_html_panel.object = speech_to_text.results_as_html

    speech_to_text_settings = pn.WidgetBox(
        pn.Param(
            speech_to_text,
            parameters=[
                "stop",
                "abort",
                "grammars",
                "lang",
                "continuous",
                "interim_results",
                "max_alternatives",
                "service_uri",
                "started",
                "results",
                "results_last",
                "results_serialized",
                "started",
                "audio_started",
                "sound_started",
                "speech_started",
                "button_type",
            ],
        ),
    )
    app = pn.Column(
        pn.pane.HTML(
            "<h1>Speech to Text <img style='float:right;height:40px;width:164px;margin-right:40px' src='https://panel.holoviz.org/_static/logo_horizontal.png'></h1>",
            background="black",
            style={"color": "white", "margin-left": "20px"},
            margin=(0, 0, 15, 0),
        ),
        speech_to_text,
        pn.Row(
            pn.Column(pn.pane.Markdown("## Settings"), speech_to_text_settings),
            pn.layout.VSpacer(width=25),
            pn.Column(
                pn.pane.Markdown("## Results"),
                results_as_html_panel,
            ),
        ),
        width=800,
        sizing_mode="fixed",
    )
    return app


if __name__.startswith("bokeh"):
    pn.config.sizing_mode = "stretch_width"
    test_get_app().servable()
