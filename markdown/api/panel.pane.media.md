# panel.pane.media module

Contains Media panes including renderers for Audio and Video content.

class panel.pane.media.Audio(object=None, **params)
Bases: `_MediaBase`

The Audio pane displays an audio player given a local or remote audio
file, a NumPy Array or Torch Tensor.

The pane also allows access and control over the player state including
toggling of playing/paused and loop state, the current time, and the
volume.

The audio player supports ogg, mp3, and wav files

If SciPy is installed, 1- or 2-dim Numpy Arrays and 1- or 2-dim Torch
Tensors are also supported. The dtype must be one of the following

- numpy: np.int16, np.uint16, np.float32, np.float64

- torch: torch.short, torch.int16, torch.half, torch.float16,
  torch.float, torch.float32,

torch.double, torch.float64

The array or Tensor input will be downsampled to 16bit and converted to
a wav file by SciPy.

Reference:
[https://panel.holoviz.org/reference/panes/Audio.html](https://panel.holoviz.org/reference/panes/Audio.html)

Example:

\>\>\>
Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3',
name='Audio')

Methods

|  |  |
|----|----|
| [applies](#panel.pane.media.Audio.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
> `panel.pane.media._MediaBase`: loop, time,
> throttle, paused, volume, autoplay, muted
>
>

`object`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'bytes'>,`` ``<class`` ``'pathlib.Path'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'numpy.ndarray'>,`` ``<class`` ``'panel.pane.media.TensorLike'>),`` ``default='',`` ``label='Object')`
The audio file either local or remote, a 1- or 2-dim NumPy ndarray or a
1- or 2-dim Torch Tensor or a bytes or BytesIO object.

`sample_rate`` ``=`` ``Integer(default=44100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sample`` ``rate')`
The sample_rate of the audio when given a NumPy array or Torch tensor.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.media.TensorLike
Bases: `object`

A class similar to torch.Tensor. We don’t want to make PyTorch a
dependency of this project

class panel.pane.media.TensorLikeMeta
Bases: `type`

See [https://blog.finxter.com/python-__instancecheck__-magic-method/](https://blog.finxter.com/python-__instancecheck__-magic-method/)

class panel.pane.media.Video(object=None, **params)
Bases: `_MediaBase`

The Video Pane displays a video player given a local or remote video
file.

The widget also allows access and control over the player state
including toggling of playing/paused and loop state, the current time,
and the volume.

Depending on the browser the video player supports mp4, webm, and ogg
containers and a variety of codecs.

Reference:
[https://panel.holoviz.org/reference/panes/Video.html](https://panel.holoviz.org/reference/panes/Video.html)

Example:

\>\>\>
Video(
...
'https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4',
...
width=640,
height=360,
loop=True
... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout
>
> `panel.pane.media._MediaBase`: loop, time,
> throttle, paused, autoplay, muted
>
>

`object`` ``=`` ``ClassSelector(allow_None=True,`` ``allow_refs=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'pathlib.Path'>,`` ``<class`` ``'_io.BytesIO'>,`` ``<class`` ``'bytes'>),`` ``default='',`` ``label='Object')`
The video file either local or remote as a string or URL or as a bytes
or BytesIO object.

`volume`` ``=`` ``Integer(bounds=(0,`` ``100),`` ``default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Volume')`
The volume of the media player.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
