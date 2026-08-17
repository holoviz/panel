# TextToSpeech
---
```python
import panel as pn

pn.extension()
```

The `TextToSpeech` Widget provides brings *text to speech* to Panel. It wraps the wraps the [HTML5 SpeechSynthesis API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) and [HTML SpeechSynthesisUtterance API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance).

An *utterance* is the smallest unit of speech in spoken language analysis. The `Utterance` provides fine grained control over the `text`, `voice`, `volume`, `pitch` and `rate`.

#### Parameters:

##### Core

* **``value``** (str): The text that will be synthesised when the utterance is spoken. The text may be provided as plain text, or a well-formed SSML document
* **``auto_speak``** (boolean): Whether or not to speak automatically whenever the value changes. Default it True.
* **``lang``** (str): The language of the utterance.
* **``voice``** (SpeechSynthesisVoice): The voice that will be used to speak the utterance.
* **``pitch``** (float): The pitch at which the utterance will be spoken at. A number between 0 and 2. Default is 1
* **``rate``** (float): The speed at which the utterance will be spoken at. A number between 0.1 and 10. Default is 1
* **``volume``** (float): The volume that the utterance will be spoken at. A number between 0 and 1. Default is 1

##### Actions

* **``speak``**: Speaks the utterance. Note an utterance is also spoken whenever you change the `value`.
* **``cancel``** (): Removes all Utterances from the Utterance queue.
* **``pause``** (): Puts the SpeechSynthesis object into a paused state.
* **``resume``** (): Puts the SpeechSynthesis object into a non-paused state: resumes it if it was already paused.

##### Readonly Parameters:

* **``voices``** (List[Voice]): Returns a list of Voice objects representing all the available voices in the current device.

The `voices` parameter is populated by your browser and are not available before 1) The `TextToSpeech` instance is included in your app 2) the app has loaded and 3) the browser has loaded its list of `voices`. The available voices depend on your OS and browser.

* **``paused``** (boolean): Returns true if the TextToSpeech object is in a paused state.
* **``pending``** (boolean): Returns true if the utterance queue contains as-yet-unspoken
        utterances.
* **``speaking``** (boolean): returns true if an utterance is currently in the process of being
        spoken — even if TextToSpeech is in a paused state.

The `paused`, `pending` and `speaking` parameters are being updated by your browser every 1 sec only. So they arrive with a small time lag.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

Instantiate and display the `TextToSpeech` widget without any text:

```python
basic_speaker = pn.widgets.TextToSpeech(label="Speech Synthesis")
basic_speaker
```

Please note this does not visually display any widget. But you still need to add it to your notebook or server app.

As long as `auto_speak` is true setting the `value` will cause it to speak:

```python
basic_speaker.value = "Hello Panel World"
```

We can also trigger speaking by setting the `speak` parameter to `True`:

```python
basic_speaker.speak = True
```

Now let us create a longer text:

```python
TEXT = """By Aesop

There was a time, so the story goes, when all the animals lived together in harmony. The lion didn’t chase the oxen, the wolf didn’t hunt the sheep, and owls didn’t swoop on the mice in the field.

Once a year they would get together and choose a king, who would then reign over the animal kingdom for the next twelve months. Those animals who thought they would like a turn at being king would put themselves forward and would make speeches and give demonstrations of their prowess or their wisdom. Then all the animals gathered together would vote, and the animal with the most votes was crowned king. That’s probably where us humans got the idea of elections!

Now, monkey knew very well that he was neither very strong nor very wise, and he was not exactly a great orator, but, boy, could he dance! So he did what he does best, and he danced acrobatically and energetically, performing enormous leaps, back somersaults and cartwheels that truly dazzled his audience. Compared to monkey, the elephant was grave and cumbersome, the lion was powerful and authoritarian, and the snake was sly and sinister.

Nobody who was there remembers exactly how it happened, but somehow monkey scraped through with a clear majority of all the votes cast, and he was announced the king of the animal kingdom for the coming year. Most of the animals seemed quite content with this outcome, because they knew that monkey would not take his duties too seriously and make all kinds of onerous demands on them, or demand too much of a formal show of obedience. But there were some who thought that the election of monkey diminished the stature of the kingship, and one of these was fox; in fact fox was pretty disgusted, and he didn’t mind who knew it. So he set about concocting a scheme to make monkey look stupid.

He gathered together some fine fresh fruit from the forest, mangos, figs and dates, and laid them out on a trap he’d found. He waited for the monkey to pass by, and called out to him: “Sire, look at these delicious dainty morsels I discovered here by the wayside. I was tempted to gorge myself on them, but then I remembered fruits are your favourite repast, and I thought I should keep them for you, our beloved king!”

Monkey could not resist either the flattery or the fruit, and just managed to compose himself long enough to whisper a hurried “Why, thank you, Mr Fox” and made a beeline for the fruit. “Swish” and “Clunk” went the trap, and “AAAYYY AAAYYY” went our unfortunate monkey king, the trap firmly clasped around his paw.

Monkey bitterly reproached fox for leading him into such a dangerous situation, but fox just laughed and laughed. “You call yourself king of all the animals,” he cried, “and you allow yourself to be taken in just like that!”

Aesop
"""

text_to_speech = pn.widgets.TextToSpeech(label="Text to Speech Widget", value=TEXT, auto_speak=False)
```

And controls to the widget so you can test what the various parameters do:

```python
text = pn.Param(text_to_speech.param.value, widgets={"value": {"widget_type": pn.widgets.TextAreaInput, "height": 300}})

pn.Row(text_to_speech.controls(jslink=False), text, text_to_speech, width=600)
```

Try changing the `value`, `lang`, `voice` etc.

---
