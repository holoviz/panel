# panel.models.speech_to_text module

Bokeh Model of the Panel SpeechToText widget

class panel.models.speech_to_text.SpeechToText(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `Widget`

Bokeh Model of the Panel SpeechToText widget

Controls the speech recognition service.

On some browsers, like Chrome, using Speech Recognition on a web page
involves a server-based recognition engine. Your audio is sent to a web
service for recognition processing, so it won’t work offline.

Wraps the HTML5 SpeechRecognition API. See [https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)

Attributes:
**abort**

**audio_started**

**button_hide**

**button_not_started**

**button_started**

**button_type**

**continuous**

**grammars**

**interim_results**

**lang**

**max_alternatives**

**results**

**service_uri**

**sound_started**

**speech_started**

**start**

**started**

**stop**

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
