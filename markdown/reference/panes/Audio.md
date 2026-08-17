# Audio
---
```python
import numpy as np
import panel as pn

pn.extension()
```

The ``Audio`` pane displays an audio player given a local or remote audio file, NumPy ndarray or a Torch Tensor.

The pane also allows access and control over the player state including toggling of playing/``paused`` and ``loop`` state, the current ``time``, and the ``volume``.

The audio player supports ``ogg``, ``mp3``, and ``wav`` file formats

If SciPy is installed, 1-dim Numpy ndarrys and 1-dim Torch Tensors are also supported. The dtype must be one of the following

- numpy: np.int16, np.uint16, np.float32, np.float64
- torch: torch.short, torch.int16, torch.half, torch.float16, torch.float, torch.float32, torch.double, torch.float64

The array or tensor input will be downsampled to 16bit and converted to a wav file by SciPy.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``autoplay``** (boolean): When True, it specifies that the output will play automatically. In Chromium browsers this requires the user to click play once
* **``loop``** (boolean): Whether to loop when reaching the end of playback
* **``muted``** (boolean): When True, it specifies that the output should be muted
* **``name``** (str): The title of the pane
* **``object``** (string): Local file path, remote URL pointing to audio file, 1-dim numpy array or 1-dim torch tensor
* **``paused``** (boolean): Whether the player is paused
* **``sample_rate``** (int): The sample_rate of the audio when given a NumPy array or Torch Tensor. Default is 44100.
* **``throttle``** (int): How frequently to sample the current playback in milliseconds
* **``time``** (float): Current playback time in seconds
* **``volume``** (int): Volume in the range 0-100

___

The `Audio` pane can be constructed with a URL pointing to a remote audio file or a local audio file (in which case the data is embedded).

```python
audio = pn.pane.Audio('https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3', name='Audio')

audio
```

The player can be controlled using its own widgets, as well as by using Python code as follows.  To pause or unpause it in code, use the ``paused`` property:

```python
#audio.paused = False
```

The current player ``time`` can be read and set with the time variable (in seconds):

```python
audio.time
```

The ``volume`` may also be read and set:

```python
audio.volume = 50
```

When providing a NumPy Array or Torch Tensor, you should specify the `sample_rate`.

In this example we plot a frequency modulated signal:

```python
sps = 44100 # Samples per second
duration = 10 # Duration in seconds

modulator_frequency = 2.0
carrier_frequency = 120.0
modulation_index = 2.0

time = np.arange(sps*duration) / sps
modulator = np.sin(2.0 * np.pi * modulator_frequency * time) * modulation_index
carrier = np.sin(2.0 * np.pi * carrier_frequency * time)
waveform = np.sin(2. * np.pi * (carrier_frequency * time + modulator))
    
waveform_quiet = waveform * 0.3

pn.pane.Audio(waveform_quiet, sample_rate=sps)
```

### Controls

The `Audio` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(audio.controls(), audio)
```

---
