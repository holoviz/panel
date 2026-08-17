# Player
---
```python
import panel as pn

pn.extension()
```

The ``Player`` widget displays media-player-like controls that allow playing and stepping through a range of values. When playing it triggers events at a pre-defined interval on the frontend, advancing the player value each time. It falls into the broad category of single-value slider widgets that provide a compatible API and includes the ```IntSlider``` and ```FloatSlider``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``direction``** (int): Current play direction of the Player (-1: playing in reverse,
0: paused, 1: playing).
* **``interval``** (int): Interval in milliseconds between updates
* **``loop_policy``** (str): Looping policy; must be one of 'once', 'loop', or 'reflect'
* **``start``** (int): The range's lower bound
* **``end``** (int): The range's upper bound
* **``step``** (int): The interval between values
* **``value``** (int): The current integer value
* **``value_throttled``** (int): The current integer value throttled until mouseup (when selected using slider)

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``scale_buttons``** (float): The scaling factor to resize the buttons
* **``show_loop_controls``** (boolean): Whether radio buttons allowing to switch between loop policies options are shown
* **``show_value``** (boolean): Whether to display the value of the player
* **``value_align``** (str): Where to display the value; must be one of 'start', 'center', 'end'
* **``visible_buttons``** (list[str]): The buttons to display on the player ('slower', 'first', 'previous', 'reverse', 'pause', 'play', 'next', 'last', 'faster')
* **``visible_loop_options``** (list[str]): The loop options to display on the player. ('once', 'loop', 'reflect')

___

The widget has a number of buttons to go to the first or last value, step forward or backward, or play and pause the widget. It also provides control over the ``loop_policy`` which determines whether to play 'once', 'loop', or 'reflect'. Additionally ``-`` and ``+`` buttons slow down and speed up the player speed.

```python
player = pn.widgets.Player(label='Player', start=0, end=100, value=32, loop_policy='loop',
                           show_value=True, value_align='start')

player
```

Like most other widgets, ``Player`` has a value parameter that can be accessed or set:

```python
player.value
```

The `Player` can be controlled programmatically using the `direction` parameter which has three possible states:

- `-1`: playing in reverse
-  `0`: paused
-  `1`: playing

Alternatively it can be controlled via the `.play`, `.pause` and `.reverse` methods:

```python
import time

player.play()
time.sleep(2)
player.reverse()
time.sleep(2)
player.pause()
```

The `Player` can be slimmed down by setting `scale_buttons`, `show_loop_controls`, `visible_buttons`, and/or `visible_loop_options`.

```python
player = pn.widgets.Player(label='Player', visible_buttons=["play", "pause"], scale_buttons=0.9, show_loop_controls=False, width=150)
player
```

### Controls

The `Player` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(player.controls(jslink=True), player)
```

---
