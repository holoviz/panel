# VideoStream
---
```python
import panel as pn
pn.extension()
```

The ``VideoStream`` widget displays a video from a local stream (for example from a webcam) and allows accessing the streamed video data from Python.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``format``** (str): Format of the captured images, either 'png' (default) or 'jpeg'. Choose `jpeg` if you want the `VideoStream` to take high frequent snapshots as the image size is much smaller.
* **``paused``** (boolean): Whether the video stream is paused
* **``timeout``** (int): Interval between snapshots (if None then snapshot only taken if snapshot method is called)
* **``value``** (string): String representation of the current snapshot

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The ``VideoStream`` widget by default simply displays the video stream:

```python
video_stream = pn.widgets.VideoStream(label='Video Stream')
video_stream
```

To sync the state of the stream with Python we have two options. First, we can call the ``snapshot`` method, which will trigger the ``value`` of the widget to be updated:

```python
video_stream.snapshot()

html = pn.pane.HTML(width=320, height=240)

def update(event):
    html.object = ''
    
video_stream.param.watch(update, 'value')

html
```

Alternatively, we can create a video stream with a `timeout` that specifies how frequently the video stream will be updated:

```python
video = pn.widgets.VideoStream(timeout=100)
html = pn.pane.HTML()
pause = pn.widgets.Toggle(label='Pause')

pause.jslink(video, value='paused')
video.jslink(html, code={'value': """
target.text = ``
"""})

pn.Column(pause, pn.Row(video, html))
```

Lastly, the video stream can also be paused from Python:

```python
video.paused = True
```

### Controls

The `VideoStream` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(video_stream.controls(jslink=True), video_stream)
```

---
