# Creating a `MarioButton` with `JSComponent`

In this tutorial we will build a *[Mario](https://mario.nintendo.com/) style button* with sounds and animations using the [`AnyWidgetComponent`](../../reference/custom/AnyWidgetComponent.md) feature in Panel. It aims to help you learn how to push the boundaries of what can be achieved with HoloViz Panel by creating advanced components using modern JavaScript and CSS technologies.

![Mario chime button](https://assets.holoviz.org/panel/tutorials/ipymario.gif)

This tutorial draws heavily on the great [`ipymario` video and tutorial](https://youtu.be/oZhyilx3gqI?si=dFPFiHua4TuuqCpu) by [Trevor Manz](https://github.com/manzt).

## Overview

We'll build a `MarioButton` that displays a pixelated Mario icon and plays a chime sound when clicked. The button will also have customizable parameters for gain, duration, size, and animation, showcasing the powerful capabilities of `AnyWidgetComponent`.

### Prerequisites

Ensure you have HoloViz Panel installed:

```sh
pip install panel watchfiles
```

## Step 1: Define the `MarioButton` Component

We'll start by defining the Python class for the `MarioButton` component, including its parameters and rendering logic.

Create a file named `mario_button.py`:

```python
import numpy as np
import param
from panel.custom import AnyWidgetComponent
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

class MarioButton(AnyWidgetComponent):

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
    settings=pn.Column(parameters, "Credits: Trevor Manz")
    pn.FlexBox(settings, button).servable()
```

### Explanation - Python

- **`_esm`**: Specifies the path to the JavaScript file for the component.
- **`_stylesheets`**: Specifies the path to the CSS file for styling the component.
- **`_box`**: A parameter representing the pixel data for the Mario icon.
- **`gain`, `duration`, `size`, `animate`**: Parameters for customizing the button's behavior.
- **`pn.Param`**: Creates a Panel widget to control the parameters.

## Step 2: Define the JavaScript for the `MarioButton`

Create a file named `mario_button.js`:

```javascript
/**
 * Plays a Mario chime sound with the specified gain and duration.
 * @see {@link https://twitter.com/mbostock/status/1765222176641437859}
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

function createCanvas(model) {
  let size = () => `${model.get('size')}px`;
  let canvas = document.createElement("canvas");
  canvas.width = 16;
  canvas.height = 16;
  canvas.style.width = size();
  canvas.style.height = size();
  return canvas;
}

function drawImageData(canvas, pixelData) {
  const flattenedData = pixelData.flat(2);
  const imageDataArray = new Uint8ClampedArray(flattenedData);
  const imgData = new ImageData(imageDataArray, 16, 16);

  let ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  ctx.putImageData(imgData, 0, 0);
}

function addClickListener(canvas, model) {
  canvas.addEventListener("click", () => {
    chime({
      gain: model.get('gain'),
      duration: model.get('duration'),
    });
    if (model.get('animate')) {
      canvas.style.animation = "none";
      setTimeout(() => {
        canvas.style.animation = "ipymario-bounce 0.2s";
      }, 10);
    }
  });
}

function addResizeWatcher(canvas, model) {
  model.on('change:size', () => {
    let size = () => `${model.get('size')}px`;
    canvas.style.width = size();
    canvas.style.height = size();
  });
}

function render({ model, el }) {
  let canvas = createCanvas(model);
  drawImageData(canvas, model.get('_box'));
  addClickListener(canvas, model);
  addResizeWatcher(canvas, model);

  el.classList.add("ipymario");
  el.appendChild(canvas)
}
export default {render};
```

### Explanation - JavaScript

- **`chime`**: A function that generates the Mario chime sound using the Web Audio API.
- **`render`**: The main function that renders the button, sets up the canvas, handles click events, and manages parameter changes.

## Step 3: Define the CSS for the `MarioButton`

Create a file named `mario_button.css`:

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

### Explanation - CSS

- **`.ipymario > canvas`**: Styles the canvas to ensure the Mario icon remains pixelated.
- **`@keyframes ipymario-bounce`**: Defines the bounce animation for the button when clicked.

## Step 4: Serve the Application

To serve the application, run the following command in your terminal:

```sh
panel serve mario_button.py --autoreload
```

This command will start a Panel server and automatically reload changes as you edit the files.

The result should look like this:

<video muted controls loop poster="https://assets.holoviz.org/panel/tutorials/mario_button.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/mario_button.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

You'll have to turn on the sound to hear the chime.

## Step 4: Develop the Application with Autoreload

When you save your `.py`, `.js` or `.css` file, the Panel server will automatically reload the changes. This feature is called *auto reload* or *hot reload*.

Try changing `"ipymario-bounce 0.2s"` in the `mario_button.js` file to `"ipymario-bounce 2s"` and save the file. The Panel server will automatically reload the changes.

Try clicking the button to see the button bounce more slowly.

## Conclusion

You've now created a custom `MarioButton` component using  [`AnyWidgetComponent`](../../reference/panes/AnyWidgetComponent.md) in HoloViz Panel. This button features a pixelated Mario icon, plays a chime sound when clicked, and has customizable parameters for gain, duration, size, and animation.

## References

### Tutorials

- [Build Custom Components](../../how_to/custom_components/esm/custom_layout.md)

### How-To Guides

- [Convert `AnyWidget` widgets](../../how_to/migrate/anywidget/index.md)

### Reference Guides

- [`AnyWidgetComponent`](../../reference/panes/AnyWidgetComponent.md)
- [`JSComponent`](../../reference/panes/JSComponent.md)
- [`ReactComponent`](../../reference/panes/ReactComponent.md)
