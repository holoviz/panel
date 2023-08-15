```python
import asyncio
import panel as pn

pn.extension()
```

The `ChatFeed` is a mid-level widget, that lets you manage a list of [`ChatEntry`](ChatEntry.ipynb) items.

This widget provides backend methods to:
- Send (append) messages to the chat log.
- Stream tokens to the latest `ChatEntry` in the chat log.
- Execute callbacks when a user sends a message.
- Undo a number of sent `ChatEntry` objects.
- Clear the chat log of all `ChatEntry` objects.

See [`ChatInterface`](ChatInterface.ipynb) for a high-level, *easy to use*, *ChatGPT like* interface.

![Chat Design Specification](../../assets/ChatDesignSpecification.png)

#### Parameters:

##### Core

* **`value`** (`List[ChatEntry]`): The entries added to the chat feed.
* **`callback`** (callable): Callback to execute when a user sends a message or when `respond` is called. The signature must include the previous message value `contents`, the previous `user` name, and the component `instance`.

##### Styling

* **`card_params`** (Dict): Parameters to pass to Card, such as `header`, `header_background`, `header_color`, etc.
* **`entry_params`** (Dict): Parameters to pass to each ChatEntry, such as `reaction_icons`, `timestamp_format`, `show_avatar`, `show_user`, and `show_timestamp`.

##### Other

* **`header`** (Any): The header of the chat feed; commonly used for the title. Can be a string, pane, or widget.
* **`callback_user`** (str): The default user name to use for the entry provided by the callback.
* **`callback_avatar`** (str | BinaryIO): The avatar to use for the user. Can be a single character text, an emoji, or anything supported by `pn.pane.Image`. If not set, uses the first character of the name.
* **`placeholder`** (any): Placeholder to display while the callback is running. Defaults to a LoadingSpinner.
* **`placeholder_text`** (any): If placeholder is the default LoadingSpinner, the text to display next to it.
* **`placeholder_threshold`** (float): Min duration in seconds of buffering before displaying the placeholder. If 0, the placeholder will be disabled. Defaults to 0.2.
* **`auto_scroll_limit`** (int): Max pixel distance from the latest object in the Column to activate automatic scrolling upon update. Setting to 0 disables auto-scrolling.
* **`scroll_button_threshold`** (int): Min pixel distance from the latest object in the Column to display the scroll button. Setting to 0 disables the scroll button.
* **`view_latest`** (bool): Whether to scroll to the latest object on init. If not enabled the view will be on the first object. Defaults to True.

#### Methods

##### Core

* **`send`**: Sends a value and creates a new entry in the chat log. If `respond` is `True`, additionally executes the callback, if provided.
* **`stream`**: Streams a token and updates the provided entry, if provided. Otherwise creates a new entry in the chat log, so be sure the returned entry is passed back into the method, e.g. `entry = chat.stream(token, entry=entry)`. This method is primarily for outputs that are not generators--notably LangChain. For most cases, use the send method instead.

##### Other

* **`clear`**: Clears the chat log and returns the entries that were cleared.
* **`respond`**: Executes the callback with the latest entry in the chat log.
* **`undo`**: Removes the last `count` of entries from the chat log and returns them. Default `count` is 1.

___

`ChatFeed` can be initialized without any arguments.


```python
chat_feed = pn.widgets.ChatFeed()
chat_feed
```

You can send chat entries with the `send` method.


```python
entry = chat_feed.send("Hello world!", user="Bot", avatar="B")
```

The `send` method returns a [`ChatEntry`](ChatEntry.ipynb), which can display any object that Panel can display. You can **interact with chat entries** like any other Panel component. You can find examples in the [`ChatEntry` Reference Notebook](ChatEntry.ipynb).


```python
entry
```

Besides messages of `str` type, the `send` method can also accept `dict`s containing the key `value` and `ChatEntry` objects.


```python
entry = chat_feed.send({"value": "Welcome!", "user": "Bot", "avatar": "B"})
```

`avatar` can also accept emojis, paths/URLs to images, and/or file-like objects.


```python
pn.widgets.ChatFeed(value=[
    pn.widgets.ChatEntry(value="I'm an emoji!", avatar="🤖"),
    pn.widgets.ChatEntry(value="I'm an image!", avatar="https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"),
])
```

Note if you provide both the user/avatar in the `dict` and keyword argument, the keyword argument takes precedence.


```python
entry = chat_feed.send({"value": "Overtaken!", "user": "Bot"}, user="MegaBot")
```

A `callback` can be attached for a much more interesting `ChatFeed`.

The signature must include the latest available message value `contents`, the latest available `user` name, and the chat `instance`.


```python
def echo_message(contents, user, instance):
    return f"Echoing... {contents}"

chat_feed = pn.widgets.ChatFeed(callback=echo_message)
chat_feed
```


```python
entry = chat_feed.send("Hello!")
```

Update `callback_user` and `callback_avatar` to change the default name and avatar of responder.


```python
chat_feed = pn.widgets.ChatFeed(callback=echo_message, callback_user="Echo Bot", callback_avatar="E")
chat_feed
```


```python
entry = chat_feed.send("Hey!")
```

The specified `callback` can also return a `dict` and `ChatEntry` object, which **must contain** a `value` key, and optionally a `user` and a `avatar` key, that overrides the default `callback_user` and `callback_avatar`.


```python
def parrot_message(contents, user, instance):
    return {"value": f"No, {contents.lower()}", "user": "Parrot", "avatar": "🦜"}

chat_feed = pn.widgets.ChatFeed(callback=parrot_message, callback_user="Echo Bot", callback_avatar="E")
chat_feed
```


```python
entry = chat_feed.send("Are you a parrot?")
```

If you do not want the callback to be triggered alongside `send`, set `respond=False`.


```python
entry = chat_feed.send("Don't parrot this.", respond=False)
```

The `ChatFeed` also support *async* `callback`s.

In fact, we recommend using *async* `callback`s whenever possible to keep your app fast and responsive.


```python
import panel as pn
import asyncio
pn.extension()

async def parrot_message(contents, user, instance):
    await asyncio.sleep(2.8)
    return {"value": f"No, {contents.lower()}", "user": "Parrot", "avatar": "🦜"}

chat_feed = pn.widgets.ChatFeed(callback=parrot_message, callback_user="Echo Bot", callback_avatar="E")
chat_feed
```


```python
entry = chat_feed.send("Are you a parrot?")
```

The easiest and most optimal way to stream output is through *async generators*.

If you're unfamiliar with this term, don't fret!

It's simply prefixing your function with `async` and replacing `return` with `yield`.


```python
async def stream_message(contents, user, instance):
    message = ""
    for character in contents:
        message += character
        yield message

chat_feed = pn.widgets.ChatFeed(callback=stream_message)
chat_feed
```


```python
entry = chat_feed.send("Streaming...")
```

You can also continuously replace the original message if you do not concatenate the characters.


```python
async def replace_message(contents, user, instance):
    for character in contents:
        await asyncio.sleep(0.1)
        yield character

chat_feed = pn.widgets.ChatFeed(callback=replace_message)
chat_feed
```


```python
entry = chat_feed.send("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
```

This works extremely well with OpenAI's `create` and `acreate` functions--just be sure that `stream` is set to `True`!

```python
import openai
import panel as pn

pn.extension()

async def openai_callback(contents, user, instance):
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": contents}],
        stream=True,
    )
    message = ""
    async for chunk in response:
        message += chunk["choices"][0]["delta"].get("content", "")
        yield message

chat_feed = pn.widgets.ChatFeed(callback=openai_callback)
chat_feed.send("Have you heard of HoloViz Panel?")
```

![OpenAI ACreate App](https://user-images.githubusercontent.com/42288570/260281672-09da9517-9336-42df-a502-b61530bd89b3.gif)

It's also possible to manually trigger the callback with `respond`. This could be useful to achieve a chain of responses from the initial message!


```python
async def chain_message(contents, user, instance):
    await asyncio.sleep(1.8)
    if user == "User":
        yield {"user": "Bot 1", "value": "Hi User! I'm Bot 1--here to greet you."}
        instance.respond()
    elif user == "Bot 1":
        yield {
            "user": "Bot 2",
            "value": "Hi User; I see that Bot 1 already greeted you; I'm Bot 2.",
        }
        instance.respond()
    elif user == "Bot 2":
        yield {
            "user": "Bot 3",
            "value": "I'm Bot 3; the last bot that will respond. See ya!",
        }


chat_feed = pn.widgets.ChatFeed(callback=chain_message)
chat_feed
```


```python
entry = chat_feed.send("Hello bots!")
```

It can be fun to watch bots talking to each other. Beware of the token usage!

```python
import openai
import panel as pn

pn.extension()


async def openai_self_chat(contents, user, instance):
    if user == "User" or user == "ChatBot B":
        user = "ChatBot A"
        avatar = "https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"
    elif user == "ChatBot A":
        user = "ChatBot B"
        avatar = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Outreachy-bot-avatar.svg/193px-Outreachy-bot-avatar.svg.png"

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": contents}],
        temperature=0,
        max_tokens=500,
        stream=True,
    )
    message = ""
    async for chunk in response:
        message += chunk["choices"][0]["delta"].get("content", "")
        yield {"user": user, "value": message, "avatar": avatar}
    instance.respond()


chat_feed = pn.widgets.ChatFeed(callback=openai_self_chat, sizing_mode="stretch_width", height=1000).servable()
chat_feed.send("What is HoloViz Panel?")
```

![OpenAI Bot Conversation](https://user-images.githubusercontent.com/42288570/260283078-de8f56c2-becc-4566-9813-618bfc81f3c2.gif)

If a returned object is not a generator (notably LangChain output), it's still possible to stream the output with the `stream` method.


```python
chat_feed = pn.widgets.ChatFeed()

# creates a new entry
entry = chat_feed.stream("Hello", user="Aspiring User", avatar="🤓")
chat_feed
```


```python
# streams (appends) to the previous entry

entry = chat_feed.stream(" World!", user="Aspiring User", avatar="🤓", entry=entry)
```

The `stream` method is commonly used with for loops.


```python
chat_feed = pn.widgets.ChatFeed()
chat_feed
```


```python
entry = None
for n in "123456789 abcdefghijklmnopqrstuvxyz":
    await asyncio.sleep(0.1)
    entry = chat_feed.stream(n, entry=entry)
```

You can build your own custom chat interface too on top of `ChatFeed`, but remember there's a pre-built [`ChatInterface`](ChatInterface.ipynb)!


```python
import asyncio
import panel as pn
from panel.widgets.chat import ChatEntry, ChatFeed

pn.extension()


async def get_response(contents, user, instance):
    await asyncio.sleep(0.88)
    return {
        "Marc": "It is 2",
        "Andrew": "It is 4",
    }.get(user, "I don't know")


ASSISTANT_AVATAR = (
    "https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"
)

chat_feed = ChatFeed(
    value=[ChatEntry(user="Assistant", value="Hi There!", avatar=ASSISTANT_AVATAR)],
    callback=get_response,
    height=500,
    callback_avatar=ASSISTANT_AVATAR,
)

marc_button = pn.widgets.Button(
    name="Marc",
    on_click=lambda event: chat_feed.send(
        user="Marc", value="What is the square root of 4?", avatar="🚴"
    ),
    align="center",
    disabled=chat_feed.param.disabled,
)
andrew_button = pn.widgets.Button(
    name="Andrew",
    on_click=lambda event: chat_feed.send(
        user="Andrew", value="What is the square root of 4 squared?", avatar="🏊"
    ),
    align="center",
    disabled=chat_feed.param.disabled,
)
undo_button = pn.widgets.Button(
    name="Undo",
    on_click=lambda event: chat_feed.undo(2),
    align="center",
    disabled=chat_feed.param.disabled,
)
clear_button = pn.widgets.Button(
    name="Clear",
    on_click=lambda event: chat_feed.clear(),
    align="center",
    disabled=chat_feed.param.disabled,
)


pn.Column(
    chat_feed,
    pn.layout.Divider(),
    pn.Row(
        "Click a button",
        andrew_button,
        marc_button,
        undo_button,
        clear_button,
    ),
)
```
