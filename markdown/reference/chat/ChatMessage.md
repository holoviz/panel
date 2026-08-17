# ChatMessage
---
```python
import asyncio
import pandas as pd
import panel as pn

from panel.chat import ChatMessage

pn.extension("vega")
```

The `ChatMessage` is a pane for displaying chat messages with support for various content types.

This pane provides a structured view of chat messages, including features like:
- Displaying user avatars, which can be text, emoji, or images.
- Showing the user's name.
- Displaying the message timestamp in a customizable format.
- Associating reactions with messages and mapping them to icons.
- Rendering various content types including text, images, audio, video, and more.

See `ChatFeed` for a structured and straightforward way to build a list of `ChatMessage` objects.

See `ChatInterface` for a high-level, *easy to use*, *ChatGPT like* interface.

#### Parameters:

For layout and styling-related parameters see the [Control the size](../../tutorials/basic/size.md), [Align Content](../../tutorials/basic/align.md) and [Style](../../tutorials/basic/style.md) tutorials.

##### Core

* **`object`** (object): The message contents. Can be a string, pane, widget, layout, etc.
* **`renderers`** (List[Callable]): A callable or list of callables that accept the value and return a Panel object to render the value. If a list is provided, will attempt to use the first renderer that does not raise an exception. If None, will attempt to infer the renderer from the value.
* **`user`** (str): Name of the user who sent the message.
* **`avatar`** (str | BinaryIO): The avatar to use for the user. Can be a single character text, an emoji, or anything supported by `pn.pane.Image`. If not set, uses the first character of the name.
* **`default_avatars`** (Dict[str, str | BinaryIO]): A default mapping of user names to their corresponding avatars to use when the user is set but the avatar is not. You can modify, but not replace the dictionary. Note, the keys are *only* alphanumeric sensitive, meaning spaces, special characters, and case sensitivity is disregarded, e.g. `"Chat-GPT3.5"`, `"chatgpt 3.5"` and `"Chat GPT 3.5"` all map to the same value.
* **`edited`** (bool): An event that is triggered when the message is edited
* **`footer_objects`** (List): A list of objects to display in the column of the footer of the message.
* **`header_objects`** (List): A list of objects to display in the row of the header of the message.
* **`avatar_lookup`** (Callable): A function that can lookup an `avatar` from a user name. The function signature should be `(user: str) -> Avatar`. If this is set, `default_avatars` is disregarded.
* **`reactions`** (List): Reactions associated with the message.
* **`reaction_icons`** (ChatReactionIcons | dict): A mapping of reactions to their reaction icons; if not provided defaults to `{"favorite": "heart"}`. Provides a visual representation of reactions.
* **`timestamp`** (datetime): Timestamp of the message. Defaults to the instantiation time.
* **`timestamp_format`** (str): The format in which the timestamp should be displayed.
* **`timestamp_tz`** (str): The timezone to used for the creation timestamp; only applicable if timestamp is not set. If None, uses the default timezone of datetime.datetime.now(); see `zoneinfo.available_timezones()` for a list of valid timezones.

##### Display

* **`show_avatar`** (bool): Whether to display the avatar of the user.
* **`show_user`** (bool): Whether to display the name of the user.
* **`show_timestamp`** (bool): Whether to display the timestamp of the message.
* **`show_reaction_icons`** (bool): Whether to display the reaction icons.
* **`show_copy_icon`** (bool): Whether to show the copy icon.
* **`show_edit_icon`** (bool): Whether to display the edit icon.
* **`show_activity_dot`** (bool): Whether to show the activity dot.
* **`name`** (str): The title or name of the chat message widget, if any.

___

#### Basics

```python
ChatMessage("Hi and welcome!")
```

The `ChatMessage` can display any Python object that Panel can display! For example Panel components, dataframes and plot figures.

```python
df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

vegalite = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "https://raw.githubusercontent.com/vega/vega/master/docs/data/barley.json"},
  "mark": "bar",
  "encoding": {
    "x": {"aggregate": "sum", "field": "yield", "type": "quantitative"},
    "y": {"field": "variety", "type": "nominal"},
    "color": {"field": "site", "type": "nominal"}
  },
  "width": "container",
}
vgl_pane = pn.pane.Vega(vegalite, height=240)

pn.Column(
    ChatMessage(pn.widgets.Button(label="Click")),
    ChatMessage(df),
    ChatMessage(vgl_pane),
)
```

You can specify a custom `user` name and `avatar`

```python
ChatMessage("Want to hear some beat boxing?", user="Beat Boxer", avatar="🎶")
```

Instead of searching for emojis online, you can also set a personalized emoji avatar by using its name wrapped in `\N{}`!

```python
ChatMessage("Want to hear some beat boxing?", user="Beat Boxer", avatar="\N{musical note}")
```

You can combine `ChatMessage` with other Panel components as you like.

```python
pn.Column(
    ChatMessage(
        "Yes. I want to hear some beat boxing", user="Music Lover", avatar="🎸"
    ),
    ChatMessage(
        pn.Column(
            "Here goes. Hope you like this one?",
            pn.pane.Audio(
                "https://assets.holoviz.org/panel/samples/beatboxing.mp3"
            ),
        ),
        user="Beat Boxer",
        avatar="🎶",
    ),
)
```

However, if you're serializing output, it's better practice to put other objects into the `header_objects` or `footer_objects` of the `ChatMessage` so that you don't have to write a custom serializer to handle nested Panel components.

```python
pn.Column(
    ChatMessage(
        "Yes. I want to hear some beat boxing", user="Music Lover", avatar="🎸"
    ),
    ChatMessage(
        pn.pane.Audio(
            "https://assets.holoviz.org/panel/samples/beatboxing.mp3",
        ),
        header_objects=[pn.pane.HTML("Here goes. Hope you like this one?", margin=(5, 0))],
        footer_objects=[pn.widgets.ButtonIcon(icon="download", description="Download this! (not implemented here)")],
        user="Beat Boxer",
        avatar="🎶",
    ),
)
```

`ChatMessage` can be initialized without any input.

```python
chat_message = pn.chat.ChatMessage()
chat_message
```

#### Updates

That way, the `value`, `user`, and/or `avatar` can be dynamically updated either by setting the `value` like this...

```python
chat_message.object = pn.pane.Markdown("## Cheers!")
```

Or updating multiple values at once with the `.param.update` method!

```python
chat_message.param.update(user="Jolly Guy", avatar="🎅");
```

The easiest and most optimal way to stream output to the `ChatMessage` is through async generators.

If you're unfamiliar with this term, don't fret!

It's simply prefixing your function with `async` and replacing `return` with `yield`.

This example will show you how to **replace** the `ChatMessage` `value`.

```python
async def replace_response():
    for value in range(0, 28):
        await asyncio.sleep(0.2)
        yield value

ChatMessage(replace_response)
```

This example will show you how to **append** to the `ChatMessage` `value`.

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

ChatMessage(append_response, user="Wise guy", avatar="🤓")
```

#### Styling

If you'd like a plain interface with only the `value` displayed, set `show_user`, `show_copy_icon`, `show_avatar`, and `show_timestamp` to `False` and provide an empty `dict` to `reaction_icons`.

```python
ChatMessage(
    "Plain and simple",
    show_avatar=False,
    show_user=False,
    show_timestamp=False,
    show_copy_icon=False,
    reaction_icons={},
)
```

You can set the usual styling and layout parameters like `sizing_mode`, `height`, `width`, `max_height`, `max_width`, and `styles`.

```python
ChatMessage(
    "Want to hear some beat boxing?",
    user="Beat Boxer",
    avatar="🎶",
    height=250,
    sizing_mode="stretch_width",
    max_width=600,
    styles={"background": "#CBC3E3"},
)
```

You can also use stylesheets to target parts of the `ChatMessage`

Note, it's best practice to use a path to a `.css` stylesheet, but for demo purposes, we will be using a multi-line string here.

```python
path_to_stylesheet = """
    .message {
        background-color: tan;
        font-size: 24px;
        font-family: "Courier New";
    }
    .avatar {
        background-color: red;
        border-radius: 5%;
    }
    .meta {
        background-color: lightgreen;
    }
    .header {
        background-color: green;
    }
    .footer {
        background-color: blue;
    }
    .icons {
        background-color: lightblue;
    }
    .name {
        background-color: orange;
    }
    .timestamp {
        background-color: purple;
    }
    .activity-dot {
        background-color: black;
    }
    .reaction-icons {
        background-color: white;
    }
    .copy-icon {
        background-color: gold;
    }
    .right {
        background-color: grey;
    }
    .center {
        background-color: pink;
    }
    .left {
        background-color: yellow;
    }
"""

pn.chat.ChatMessage(
    "Style me up!",
    show_activity_dot=True,
    stylesheets=[path_to_stylesheet],
    footer_objects=[pn.widgets.Button(label="Reply", color="primary")],
    header_objects=[pn.widgets.TextInput(placeholder="Name")],
)
```

## Code Highlighting

To enable code highlighting in code blocks, `pip install pygments`
:::

#### Reactions

Some active `reactions` can be associated with the message too.

```python
pn.chat.ChatMessage("Love this!", reactions=["favorite"])
```

If you'd like to display other `reactions_icons`, pass a pair of `reaction` key to tabler `icon` name.

```python
message = pn.chat.ChatMessage(
    "Looks good!",
    reactions=["like"],
    reaction_icons={"like": "thumb-up", "dislike": "thumb-down"},
)
message
```

You may bind a callback to the selected `reactions`.

Here, when the user clicks or sets `reactions`, `print_reactions` activates.

```python
def print_reactions(reactions):
    print(f"{reactions} selected.")

pn.bind(print_reactions, message.param.reactions)
```

#### Misc

If you don't specify an `avatar` on construction, then an `avatar` will be looked up in the `default_avatars` dictionary.

```python
ChatMessage.default_avatars
```

You can modify the `ChatMessage.default_avatars` in-place.

Note, the keys are *only* alphanumeric sensitive, meaning spaces, special characters, and case sensitivity is disregarded, e.g. `"Chat-GPT3.5"`, `"chatgpt 3.5"` and `"Chat GPT 3.5"` all map to the same value.

```python
ChatMessage.default_avatars["Wolfram"] = "🐺"
ChatMessage.default_avatars["#1 good-to-go guy"] = "👍"

pn.Column(
    ChatMessage("Mathematics!", user="Wolfram"),
    ChatMessage("Good to go!", user="#1 Good-to-Go Guy"),
    ChatMessage("What's up?", user="Other Guy"),
    max_width=300,
)
```

The `timestamp` can be formatted using `timestamp_format`. Additionally, a timestamp_tz can be provided to use any timezones supported by `zoneinfo`.

```python
pn.chat.ChatMessage(timestamp_format="%b %d, %Y %I:%M %p", timestamp_tz="US/Pacific")
```

The `ChatMessage` can serialized into a string.

```python
widget = pn.widgets.FloatSlider(value=3, label="Number selected")
pn.chat.ChatMessage(widget).serialize()
```

For an example on `renderers`, see `ChatInterface`.

---
