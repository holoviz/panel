```python
import asyncio

import panel as pn
from panel.widgets import ChatEntry

pn.extension()

```

The `ChatEntry` is a widget for displaying chat messages with support for various content types.

This widget provides a structured view of chat messages, including features like:
- Displaying user avatars, which can be text, emoji, or images.
- Showing the user's name.
- Displaying the message timestamp in a customizable format.
- Associating reactions with messages and mapping them to icons.
- Rendering various content types including text, images, audio, video, and more.

See [`ChatFeed`](ChatFeed.ipynb) for a structured and straightforward way to build a list of `ChatEntry` objects.

See [`ChatInterface`](ChatInterface.ipynb) for a high-level, *easy to use*, *ChatGPT like* interface.

![Chat Design Specification](../../assets/ChatDesignSpecification.png)

#### Parameters:

For layout and styling related parameters see the [customization user guide](../../user_guide/Customization.ipynb).

##### Core

* **`value`** (object): The message contents. Can be a string, pane, widget, layout, etc.
* **`user`** (str): Name of the user who sent the message.
* **`avatar`** (str | BinaryIO): The avatar to use for the user. Can be a single character text, an emoji, or anything supported by `pn.pane.Image`. If not set, uses the first character of the name.
* **`reactions`** (List): Reactions associated with the message.
* **`reaction_icons`** (ChatReactionIcons | dict): A mapping of reactions to their reaction icons; if not provided defaults to `{"favorite": "heart"}`. Provides a visual representation of reactions.
* **`timestamp`** (datetime): Timestamp of the message. Defaults to the instantiation time.
* **`timestamp_format`** (str): The format in which the timestamp should be displayed.
* **`renderers`** (List[Callable]): A callable or list of callables that accept the value and return a Panel object to render the value. If a list is provided, will attempt to use the first renderer that does not raise an exception. If None, will attempt to infer the renderer from the value.

##### Display

* **`show_avatar`** (bool): Whether to display the avatar of the user.
* **`show_user`** (bool): Whether to display the name of the user.
* **`show_timestamp`** (bool): Whether to display the timestamp of the message.
* **`name`** (str): The title or name of the chat entry widget, if any.

___


```python
ChatEntry(value="Hi. Welcome")

```

The `ChatEntry` can display any Python object that Panel can display! For example Panel components, dataframes and plot figures.


```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

fig, axes = plt.subplots()
axes.plot(df["x"], df["y"])
plt.close(fig)

pn.Column(
    ChatEntry(value=pn.widgets.Button(name="Click")),
    ChatEntry(value=df),
    ChatEntry(value=fig),
)

```

You can specify a custom `user` name and `avatar`


```python
ChatEntry(value="Want to hear some beat boxing?", user="Beat Boxer", avatar="🎶")

```

You can combine `ChatEntry` with other Panel components as you like.


```python
pn.Column(
    ChatEntry(
        value="Yes. I want to hear some beat boxing", user="Music Lover", avatar="🎸"
    ),
    ChatEntry(
        value=pn.Column(
            "Here goes. Hope you like this one?",
            pn.pane.Audio(
                "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg"
            ),
        ),
        user="Beat Boxer",
        avatar="🎶",
    ),
)

```

`ChatEntry` can be initialized without any input.


```python
chat_entry = pn.widgets.ChatEntry()
chat_entry

```

That way, the `value`, `user`, and/or `avatar` can be dynamically updated either by setting the `value` like this...


```python
chat_entry.value = pn.widgets.StaticText(value="Cheers!")

```

Or updating multiple values at once with the `.param.update` method!


```python
chat_entry.param.update(user="Jolly Guy", avatar="🎅")

```

The `timestamp` can be formatted using `timestamp_format`.


```python
pn.widgets.ChatEntry(timestamp_format="%b %d, %Y %I:%M %p")

```

If you'd like a plain interface with only the `value` displayed, set `show_user`, `show_avatar`, and `show_timestamp` to `False` and provide an empty `dict` to `reaction_icons`.


```python
ChatEntry(
    value="Plain and simple",
    show_avatar=False,
    show_user=False,
    show_timestamp=False,
    reaction_icons={},
)
```

You can set the usual styling and layout parameters like `sizing_mode`, `height`, `width`, `max_height`, `max_width`, `styles` and `stylesheet`.


```python
ChatEntry(
    value="Want to hear some beat boxing?",
    user="Beat Boxer",
    avatar="🎶",
    height=250,
    sizing_mode="stretch_width",
    max_width=600,
    styles={"background": "#CBC3E3"},
)
```

Some active `reactions` can be associated with the message too.


```python
pn.widgets.ChatEntry(value="Love this!", reactions=["favorite"])
```

If you'd like to display other `reactions_icons`, pass a pair of `reaction` key to tabler `icon` name.


```python
entry = pn.widgets.ChatEntry(
    value="Looks good!",
    reactions=["like"],
    reaction_icons={"like": "thumb-up", "dislike": "thumb-down"},
)
entry
```

You may bind a callback to the selected `reactions`.

Here, when the user clicks or sets `reactions`, `print_reactions` activates.


```python
def print_reactions(reactions):
    print(f"{reactions} selected.")

pn.bind(print_reactions, entry.param.reactions, watch=True)
```

The easiest and most optimal way to stream output to the `ChatEntry` is through async generators.

If you're unfamiliar with this term, don't fret!

It's simply prefixing your function with `async` and replacing `return` with `yield`.

This example will show you how to **replace** the `ChatEntry` `value`.


```python
async def replace_response():
    for value in range(0, 28):
        await asyncio.sleep(0.2)
        yield value


ChatEntry(value=replace_response)
```

This example will show you how to **append** to the `ChatEntry` `value`.


```python
sentence = """
    The greatest glory in living lies not in never falling,
    but in rising every time we fall.
"""


async def append_response():
    value = ""
    for token in sentence.split():
        value += f" {token}"
        await asyncio.sleep(0.2)
        yield value


ChatEntry(value=append_response, user="Wise guy", avatar="🤓")

```

You can also use this to provide parts of responses as soon as they are ready.


```python
async def respond_when_ready():
    spinner = pn.indicators.LoadingSpinner(value=True, size=25, color="light")
    layout = pn.Column("Love your question. Let me think.", spinner)
    yield layout

    await asyncio.sleep(1)  # Waiting for some external response...
    layout.insert(-1, "I can use Matplotlib to create the Figure")
    yield layout

    await asyncio.sleep(1)  # Calculating ...
    layout.insert(-1, fig)
    layout[-1] = "I hope that answered your question?"
    yield layout


ChatEntry(
    value=respond_when_ready,
    user="Assistant",
    avatar="https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png",
)

```
