# Video
---
```python
import panel as pn

pn.extension()
```

The ``Video`` Pane displays a video player given a local or remote video file. The widget also allows access and control over the player state including toggling of playing/``paused`` and ``loop`` state, the current ``time``, and the ``volume``. Depending on the browser the video player supports ``mp4``, ``webm``, and ``ogg`` containers and a variety of codecs.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``name``** (str): The title of the widget
* **``loop``** (boolean): Whether to loop when reaching the end of playback
* **``object``** (string): Local file path or remote URL pointing to audio file
* **``paused``** (boolean): Whether the player is paused
* **``autoplay``** (boolean): When True, it specifies that the output will play automatically. In Chromium browsers this requires the user to click play once
* **``muted``** (boolean): When True, it specifies that the output should be muted
* **``throttle``** (int): How frequently to sample the current playback time in milliseconds
* **``time``** (float): Current playback time in seconds
* **``volume``** (int): Volume in the range 0-100

___

The `Video` Pane can be constructed with a URL pointing to a remote video file or a local video file (in which case the data is embedded).

```python
video = pn.pane.Video('https://assets.holoviz.org/panel/samples/video_sample.mp4', width=640, loop=True)

video
```

The player can be controlled using its own widgets, as well as by using Python code as follows.  To pause or unpause it in code, use the ``paused`` property:

```python
#video.paused = False
```

The current player ``time`` can be read and set with the time variable (in seconds):

```python
video.time
```

The ``volume`` may also be read and set:

```python
video.volume = 50
```

### Controls

The `Video` pane exposes a number of options which can be changed from both Python and Javascript try out the effect of these parameters interactively:

```python
pn.Row(video.controls(jslink=True), video)
```

---
