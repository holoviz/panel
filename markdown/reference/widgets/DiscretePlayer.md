# DiscretePlayer
---
```python
import panel as pn

pn.extension()
```

The ``DiscretePlayer`` widget displays media-player-like controls that allow playing and stepping through the provided options. When playing it triggers events at a pre-defined interval on the frontend, advancing the player value each time. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the ```AutocompleteInput```, ```Select``` and ```DiscreteSlider``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``direction``** (int): Current play direction of the Player (-1: playing in reverse,
0: paused, 1: playing).
* **``interval``** (int): Interval in milliseconds between updates
* **``loop_policy``** (str): Looping policy; must be one of 'once', 'loop', or 'reflect'
* **``options``** (list or dict): A list or dictionary of options to select from
* **``value``** (object): The current value; must be one of the option values
* **``value_throttled``** (object): The current value throttled until mouseup  (when selected using slider)

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

The widget has a number of buttons to go to the first or last value, step forward or backward, and play and pause the widget. It also provides control over the ``loop_policy``, which determines whether to play 'once', 'loop', or 'reflect'. Additionally ``-`` and ``+`` buttons slow down and speed up the player speed.

```python
discrete_player = pn.widgets.DiscretePlayer(label='Discrete Player', options=[2, 4, 8, 16, 32, 64, 128],
                                            value=8, loop_policy='loop', show_value=True, value_align='start')

discrete_player
```

Like most other widgets, ``DiscretePlayer`` has a value parameter that can be accessed or set:

```python
discrete_player.value
```

The `DiscretePlayer` can be controlled programmatically using the `direction` parameter which has three possible states:

- `-1`: playing in reverse
-  `0`: paused
-  `1`: playing

Alternatively it can be controlled via the `.play`, `.pause` and `.reverse` methods:

```python
import time

discrete_player.play()
time.sleep(2)
discrete_player.reverse()
time.sleep(2)
discrete_player.pause()
```

The `DiscretePlayer` can be slimmed down by setting `scale_buttons`, `show_loop_controls`, `visible_buttons`, and/or `visible_loop_options`.

```python
discrete_player = pn.widgets.DiscretePlayer(label='Player', visible_buttons=["play", "pause"], scale_buttons=0.9, show_loop_controls=False, width=150)
discrete_player
```

### Controls

The `DiscretePlayer` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(discrete_player.controls(jslink=True), discrete_player)
```

---
