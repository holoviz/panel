from typing import Any, Dict, List

import panel as pn
import pytest
from panel.widgets import TextToSpeech, Utterance, Voice

TEXT = """By Aesop

There was a time, so the story goes, when all the animals lived together in harmony. The lion
didn’t chase the oxen, the wolf didn’t hunt the sheep, and owls didn’t swoop on the mice in the
field.

Once a year they would get together and choose a king, who would then reign over the animal
kingdom for the next twelve months. Those animals who thought they would like a turn at being king
would put themselves forward and would make speeches and give demonstrations of their prowess or
their wisdom. Then all the animals gathered together would vote, and the animal with the most
votes was crowned king. That’s probably where us humans got the idea of elections!

Now, monkey knew very well that he was neither very strong nor very wise, and he was not exactly
a great orator, but, boy, could he dance! So he did what he does best, and he danced acrobatically
and energetically, performing enormous leaps, back somersaults and cartwheels that truly dazzled
his audience. Compared to monkey, the elephant was grave and cumbersome, the lion was powerful and
authoritarian, and the snake was sly and sinister.

Nobody who was there remembers exactly how it happened, but somehow monkey scraped through with a
clear majority of all the votes cast, and he was announced the king of the animal kingdom for the
coming year. Most of the animals seemed quite content with this outcome, because they knew that
monkey would not take his duties too seriously and make all kinds of onerous demands on them, or
demand too much of a formal show of obedience. But there were some who thought that the election
of monkey diminished the stature of the kingship, and one of these was fox; in fact fox was pretty
disgusted, and he didn’t mind who knew it. So he set about concocting a scheme to make monkey look
stupid.

He gathered together some fine fresh fruit from the forest, mangos, figs and dates, and laid them
out on a trap he’d found. He waited for the monkey to pass by, and called out to him: “Sire, look
at these delicious dainty morsels I discovered here by the wayside. I was tempted to gorge myself
on them, but then I remembered fruits are your favourite repast, and I thought I should keep them
for you, our beloved king!”

Monkey could not resist either the flattery or the fruit, and just managed to compose himself long
enough to whisper a hurried “Why, thank you, Mr Fox” and made a beeline for the fruit. “Swish” and
“Clunk” went the trap, and “AAAYYY AAAYYY” went our unfortunate monkey king, the trap firmly
clasped around his paw.

Monkey bitterly reproached fox for leading him into such a dangerous situation, but fox just
laughed and laughed. “You call yourself king of all the animals,” he cried, “and you allow
yourself to be taken in just like that!”

Aesop
"""
_VOICES_NONE: List[Dict[str, Any]] = []
_VOICES_FIREFOX_WIN10: List[Dict[str, Any]] = [
    {
        "default": False,
        "lang": "en-US",
        "local_service": True,
        "name": "Microsoft David Desktop - English (United States)",
        "voice_uri": "urn:moz-tts:sapi:Microsoft David Desktop - English (United States)?en-US",
    },
    {
        "default": False,
        "lang": "en-US",
        "local_service": True,
        "name": "Microsoft Zira Desktop - English (United States)",
        "voice_uri": "urn:moz-tts:sapi:Microsoft Zira Desktop - English (United States)?en-US",
    },
]
_VOICES_CHROME_WIN10: List[Dict[str, Any]] = [
    {
        "default": True,
        "lang": "en-US",
        "local_service": True,
        "name": "Microsoft David Desktop - English (United States)",
        "voice_uri": "Microsoft David Desktop - English (United States)",
    },
    {
        "default": False,
        "lang": "en-US",
        "local_service": True,
        "name": "Microsoft Zira Desktop - English (United States)",
        "voice_uri": "Microsoft Zira Desktop - English (United States)",
    },
    {
        "default": False,
        "lang": "de-DE",
        "local_service": False,
        "name": "Google Deutsch",
        "voice_uri": "Google Deutsch",
    },
    {
        "default": False,
        "lang": "en-US",
        "local_service": False,
        "name": "Google US English",
        "voice_uri": "Google US English",
    },
    {
        "default": False,
        "lang": "en-GB",
        "local_service": False,
        "name": "Google UK English Female",
        "voice_uri": "Google UK English Female",
    },
    {
        "default": False,
        "lang": "en-GB",
        "local_service": False,
        "name": "Google UK English Male",
        "voice_uri": "Google UK English Male",
    },
    {
        "default": False,
        "lang": "es-ES",
        "local_service": False,
        "name": "Google español",
        "voice_uri": "Google español",
    },
    {
        "default": False,
        "lang": "es-US",
        "local_service": False,
        "name": "Google español de Estados Unidos",
        "voice_uri": "Google español de Estados Unidos",
    },
    {
        "default": False,
        "lang": "fr-FR",
        "local_service": False,
        "name": "Google français",
        "voice_uri": "Google français",
    },
    {
        "default": False,
        "lang": "hi-IN",
        "local_service": False,
        "name": "Google हिन्दी",
        "voice_uri": "Google हिन्दी",
    },
    {
        "default": False,
        "lang": "id-ID",
        "local_service": False,
        "name": "Google Bahasa Indonesia",
        "voice_uri": "Google Bahasa Indonesia",
    },
    {
        "default": False,
        "lang": "it-IT",
        "local_service": False,
        "name": "Google italiano",
        "voice_uri": "Google italiano",
    },
    {
        "default": False,
        "lang": "ja-JP",
        "local_service": False,
        "name": "Google 日本語",
        "voice_uri": "Google 日本語",
    },
    {
        "default": False,
        "lang": "ko-KR",
        "local_service": False,
        "name": "Google 한국의",
        "voice_uri": "Google한국의",
    },
    {
        "default": False,
        "lang": "nl-NL",
        "local_service": False,
        "name": "Google Nederlands",
        "voice_uri": "Google Nederlands",
    },
    {
        "default": False,
        "lang": "pl-PL",
        "local_service": False,
        "name": "Google polski",
        "voice_uri": "Google polski",
    },
    {
        "default": False,
        "lang": "pt-BR",
        "local_service": False,
        "name": "Google português do Brasil",
        "voice_uri": "Google português do Brasil",
    },
    {
        "default": False,
        "lang": "ru-RU",
        "local_service": False,
        "name": "Googleрусский",
        "voice_uri": "Google русский",
    },
    {
        "default": False,
        "lang": "zh-CN",
        "local_service": False,
        "name": "Google\xa0普通话（中国大陆）",
        "voice_uri": "Google\xa0普通话（中国大陆）",
    },
    {
        "default": False,
        "lang": "zh-HK",
        "local_service": False,
        "name": "Google\xa0粤語（香港）",
        "voice_uri": "Google\xa0粤語（香港）",
    },
    {
        "default": False,
        "lang": "zh-TW",
        "local_service": False,
        "name": "Google 國語（臺灣）",
        "voice_uri": "Google 國語（臺灣）",
    },
]


@pytest.fixture
def voices():
    return Voice.to_voices_list(_VOICES_FIREFOX_WIN10)


def test_to_voices_dict_firefox_win10():
    # Given
    voices = Voice.to_voices_list(_VOICES_FIREFOX_WIN10)
    # When
    actual = Voice.group_by_lang(voices)
    # Then
    assert "en-US" in actual
    assert len(actual["en-US"]) == 2


def test_can_speak():
    text = "Give me back my money!"
    # When
    speaker = TextToSpeech()
    speaker.value = text

    model = speaker.get_root()
    assert model.speak["text"] == text


def test_can_set_voices():
    # Given
    voices = Voice.to_voices_list(_VOICES_CHROME_WIN10)
    utterance = Utterance()
    # When
    utterance.set_voices(voices)
    # Then
    assert utterance.param.lang.default == "en-US"
    assert utterance.lang == "en-US"

    assert utterance.param.voice.default.lang == "en-US"
    assert utterance.voice == utterance.param.voice.default


def test_get_app():
    text_to_speech = TextToSpeech(name="Speaker", value=TEXT, auto_speak=False)
    speaker_settings = pn.Param(
        text_to_speech,
        parameters=[
            "value",
            "speak",
            "paused",
            "speaking",
            "pending",
            "pause",
            "resume",
            "cancel",
            "lang",
            "voice",
            "pitch",
            "rate",
            "volume",
            "speak",
            "value",
        ],
        widgets={
            "speak": {"button_type": "success"},
            "value": {"widget_type": pn.widgets.TextAreaInput, "height": 300},
        },
        expand_button=False,
        show_name=False,
    )

    component = pn.Column(
        text_to_speech,
        speaker_settings,
        width=500,
        sizing_mode="fixed",
    )
    template = pn.template.MaterialTemplate(title="Panel - TextToSpeech Widget")
    template.main.append(component)
    return template


if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")
    test_get_app().servable()
