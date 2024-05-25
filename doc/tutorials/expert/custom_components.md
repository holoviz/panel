# Custom Components

In this example we will build a *Mario style button* with sounds and animations.

![Mario chime button](https://private-user-images.githubusercontent.com/24403730/311924409-e8befac9-3ce5-4ffc-a9df-3b18479c809a.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTY2MTg1OTMsIm5iZiI6MTcxNjYxODI5MywicGF0aCI6Ii8yNDQwMzczMC8zMTE5MjQ0MDktZThiZWZhYzktM2NlNS00ZmZjLWE5ZGYtM2IxODQ3OWM4MDlhLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTI1VDA2MjQ1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWFjOWEwNWE4YTI1MTAxNzA3ZWIyMWMyMmVhZThhOTE0ZjFjMDI3NWJjNTQ1YzI2YTZhNGM5M2UwMGY1NDBiMmYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.VPirrIBLCuIi1OYsuGeHbEtIfV6bavkUHNUkyrvj1_Q)

:::info

This example is heavily inspired by the great [video tutorial](https://youtu.be/oZhyilx3gqI?si=dFPFiHua4TuuqCpu) and [code repository](https://github.com/manzt/ipymario) by [Trevor Manzt](https://github.com/manzt), the creator of [AnyWidget](https://anywidget.dev/).

We believe aligning with Trevors example will increase the shared knowledge and enable increased collaboration across the AnyWidget, Jupyter and Panel communities.

Kudos to Trevor 👍

:::

You can find the full code by expanding the dropdowns below.

:::{dropdown} `mario_button.py`

```python
import numpy as np
import param
from panel.custom import JSComponent
import panel as pn

colors = {
    "O": [0, 0, 0, 255],
    "X": [247, 82, 0, 255],
    " ": [247, 186, 119, 255],
}

# fmt: off
box = [
    ['O', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', 'O', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', 'X', 'X', 'X', 'X', 'X', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', 'X', 'X', 'O', 'O', 'O', 'X', 'X', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', 'X', 'X', 'O', ' ', ' ', 'X', 'X', 'O', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', 'X', 'X', 'O', ' ', ' ', 'X', 'X', 'O', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', 'O', 'O', ' ', 'X', 'X', 'X', 'O', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'O', 'O', 'O', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'O', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O', 'O', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'O', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['X', ' ', 'O', ' ', ' ', ' ', ' ', ' ', 'O', 'O', ' ', ' ', ' ', 'O', ' ', 'O'],
    ['X', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'O'],
    ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
]
# fmt: on

np_box = np.array([[colors[c] for c in row] for row in box], dtype=np.uint8)
np_box_as_list = [[[int(z) for z in y] for y in x] for x in np_box.tolist()]

class MarioButton(JSComponent):

    _esm = "mario_button.js"
    _stylesheets = ["mario_button.css"]

    _box = param.List(np_box_as_list)
    gain = param.Number(0.1, bounds=(0.1, 1.0), step=0.1)
    duration = param.Number(1.0, bounds=(0.5, 2), step=0.5,)
    size = param.Integer(100, bounds=(10, 1000), step=10)
    animate = param.Boolean(True)

    margin = param.Integer(10)

if pn.state.served:
    button = MarioButton()
    parameters = pn.Param(
        button, parameters=["gain", "duration", "size", "animate"]
    )
    settings=pn.Column(parameters, "Credits: Trevor Mantz")
    pn.FlexBox(settings, button).servable()
```

:::

:::{dropdown} `mario_button.js`

```javascript
/**
 * Makes a Mario chime sound using web `AudioContext` API.
 *
 * @see {@link https://twitter.com/mbostock/status/1765222176641437859}
 *
 */
function chime({ gain, duration }) {
    let c = new AudioContext();
    let g = c.createGain();
    let o = c.createOscillator();
    let of = o.frequency;
    g.connect(c.destination);
    g.gain.value = gain;
    g.gain.linearRampToValueAtTime(0, duration);
    o.connect(g);
    o.type = "square";
    of.setValueAtTime(988, 0);
    of.setValueAtTime(1319, 0.08);
    o.start();
    o.stop(duration);
  }

  /**
   * @typedef Data
   * @prop {object} _box
   * @prop {number} size
   * @prop {number} gain
   * @prop {number} duration
   * @prop {boolean} animate
   */
  export function render({ data, el }) {
    let size = () => `${data.size}px`
    let canvas = document.createElement("canvas");
    canvas.width = 16;
    canvas.height = 16;
    canvas.style.width = size();
    canvas.style.height = size()

    let pixelData=data._box
    const flattenedData = pixelData.flat(2);
    const imageDataArray = new Uint8ClampedArray(flattenedData);
    const imgData = new ImageData(imageDataArray, 16, 16);

    let ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    ctx.putImageData(imgData, 0, 0);

    canvas.addEventListener("click", () => {
      chime({
        gain: data.gain,
        duration: data.duration,
      });
      if (data.animate) {
        canvas.style.animation = "none";
        setTimeout(() => {
          canvas.style.animation = "ipymario-bounce 0.2s";
        }, 10);
      }
    });
    data.watch(() => {
        canvas.style.width = size();
        canvas.style.height = size()
        console.log("resized")
    }, 'size');

    el.classList.add("ipymario");
    return canvas
  }
```

:::

:::{dropdown} `mario_button.css`

```css
.ipymario > canvas {
    animation-fill-mode: both;
    image-rendering: pixelated; /* Ensures the image stays pixelated */
    image-rendering: crisp-edges; /* For additional support in some browsers */
}

@keyframes ipymario-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}
```

:::
