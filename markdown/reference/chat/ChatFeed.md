# ChatFeed
---
```python
import panel as pn

pn.extension()
```

The `ChatFeed` is a mid-level layout, that lets you manage a list of `ChatMessage` items.

This layout provides backend methods to:
- Send (append) messages to the chat log.
- Stream tokens to the latest `ChatMessage` in the chat log.
- Execute callbacks when a user sends a message.
- Undo a number of sent `ChatMessage` objects.
- Clear the chat log of all `ChatMessage` objects.

See `ChatInterface` for a high-level, *easy to use*, *ChatGPT like* interface.

Check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs to see applicable examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc. If you have an example to demo, we'd love to add it to the panel-chat-examples gallery!

#### Parameters:

##### Core

* **`objects`** (`List[ChatMessage]`): The messages added to the chat feed.
* **`renderers`** (List[Callable]): A callable or list of callables that accept the value and return a Panel object to render the value. If a list is provided, will attempt to use the first renderer that does not raise an exception. If None, will attempt to infer the renderer from the value.
* **`callback`** (callable): Callback to execute when a user sends a message or when `respond` is called. The signature must include the previous message value `contents`, the previous `user` name, and the component `instance`.

##### Styling

* **`card_params`** (Dict): Parameters to pass to Card, such as `header`, `header_background`, `header_color`, etc.
* **`message_params`** (Dict): Parameters to pass to each ChatMessage, such as `reaction_icons`, `timestamp_format`, `show_avatar`, `show_user`, and `show_timestamp` Params passed that are not ChatFeed params will be forwarded into `message_params`.

##### Other

* **`header`** (Any): The header of the chat feed; commonly used for the title. Can be a string, pane, or widget.
* **`callback_user`** (str): The default user name to use for the message provided by the callback.
* **`callback_avatar`** (str, BytesIO, bytes, ImageBase): The default avatar to use for the entry provided by the callback. Takes precedence over `ChatMessage.default_avatars` if set; else, if None, defaults to the avatar set in `ChatMessage.default_avatars` if matching key exists. Otherwise defaults to the first character of the `callback_user`.
* **`callback_exception`** (str, Callable): How to handle exceptions raised by the callback. If "raise", the exception will be raised. If "summary", a summary will be sent to the chat feed. If "verbose" or "traceback", the full traceback will be sent to the chat feed. If "ignore", the exception will be ignored. If a callable is provided, the signature must contain the `exception` and `instance` arguments and it will be called with the exception.
* **`edit_callback`** (callable): Callback to execute when a user edits a message. The signature must include the previous message value `contents`, the previous `user` name, and the component `instance`.
* **`help_text`** (str): If provided, initializes a chat message in the chat log using the provided help text as the message object and `help` as the user. This is useful for providing instructions, and will not be included in the `serialize` method by default.
* **`placeholder_text`** (str): The text to display next to the placeholder icon.
* **`placeholder_params`** (dict) Defaults to `{"user": " ", "reaction_icons": {}, "show_copy_icon": False, "show_timestamp": False}` Params to pass to the placeholder `ChatMessage`, like `reaction_icons`, `timestamp_format`, `show_avatar`, `show_user`, `show_timestamp`.
* **`placeholder_threshold`** (float): Min duration in seconds of buffering before displaying the placeholder. If 0, the placeholder will be disabled. Defaults to 0.2.
* **`post_hook`** (callable): A hook to execute after a new message is *completely* added, i.e. the generator is exhausted. The `stream` method will trigger this callback on every call. The signature must include the  `message` and `instance` arguments.
* **`auto_scroll_limit`** (int): Max pixel distance from the latest object in the Column to activate automatic scrolling upon update. Setting to 0 disables auto-scrolling.
* **`scroll_button_threshold`** (int): Min pixel distance from the latest object in the Column to display the scroll button. Setting to 0 disables the scroll button.
* **`load_buffer`** (int): The number of objects loaded on each side of the visible objects. When scrolled halfway into the buffer, the feed will automatically load additional objects while unloading objects on the opposite side.
* **`show_activity_dot`** (bool): Whether to show an activity dot on the ChatMessage while streaming the callback response.
* **`view_latest`** (bool): Whether to scroll to the latest object on init. If not enabled the view will be on the first object. Defaults to True.

#### Methods

##### Core

* **`send`**: Sends a value and creates a new message in the chat log. If `respond` is `True`, additionally executes the callback, if provided.
* **`serialize`**: Exports the chat log as a dict; primarily for use with `transformers`.
* **`stream`**: Streams a token and updates the provided message, if provided. Otherwise creates a new message in the chat log, so be sure the returned message is passed back into the method, e.g. `message = chat.stream(token, message=message)`. This method is primarily for outputs that are not generators--notably LangChain. For most cases, use the send method instead.

##### Other

* **`clear`**: Clears the chat log and returns the messages that were cleared.
* **`respond`**: Executes the callback with the latest message in the chat log. Typically called after streaming is completed, i.e. after a for loop where `stream` is called multiple times. If not streaming, use the `respond` keyword argument inside the `send` method instead.
* **`trigger_post_hook`**: Triggers the post hook with the latest message in the chat log. Typically called after streaming is completed, i.e. after a for loop where `stream` is called multiple times. If not streaming, use the `trigger_post_hook` keyword argument inside the `send` method instead.
* **`stop`**: Cancels the current callback task if possible.
* **`scroll_to(index: int)`**: Column will scroll to the object at the specified index.
* **`undo`**: Removes the last `count` of messages from the chat log and returns them. Default `count` is 1.

___

#### Basics

`ChatFeed` can be initialized without any arguments.

```python
chat_feed = pn.chat.ChatFeed()
chat_feed
```

You can send chat messages with the `send` method.

```python
message = chat_feed.send(
    "Hello world!",
    user="Bot",
    avatar="B",
    footer_objects=[pn.widgets.Button(label="Footer Object")],
)
```

The `send` method returns a `ChatEntry`, which can display any object that Panel can display. You can **interact with chat messages** like any other Panel component. You can find examples in the [`ChatEntry` Reference Notebook](ChatEntry.md).

```python
message
```

Besides messages of `str` type, the `send` method can also accept `dict`s containing the key `value` and `ChatEntry` objects.

```python
message = chat_feed.send({"object": "Welcome!", "user": "Bot", "avatar": "B", "footer_objects": [pn.widgets.Button(label="Footer Object")]})
```

`avatar` can also accept emojis, paths/URLs to images, and/or file-like objects.

```python
pn.chat.ChatFeed(
    pn.chat.ChatMessage("I'm an emoji!", avatar="🤖"),
    pn.chat.ChatMessage("I'm an image!", avatar="https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"),
)
```

Note if you provide both the user/avatar in the `dict` and keyword argument, the keyword argument takes precedence.

````python
contents = """
```python
import panel as pn

pn.chat.ChatMessage("I'm a code block!", avatar="🤖")
```
"""
message = chat_feed.send({"object": contents, "user": "Bot"}, user="MegaBot")
message
````

To enable code highlighting in code blocks, `pip install pygments`
:::

#### Callbacks

A `callback` can be attached for a much more interesting `ChatFeed`.

The signature must include the latest available message value `contents`.

```python
def echo_message(contents):
    return f"Echoing... {contents}"

chat_feed = pn.chat.ChatFeed(callback=echo_message)
chat_feed
```

```python
message = chat_feed.send("Hello!")
```

In addition to `contents`, the signature can also include the latest available `user` name and the chat `instance`.

```python
def echo_message(contents, user, instance):
    return f"Echoing {user!r}... {contents}\n\n{instance!r}"

chat_feed = pn.chat.ChatFeed(callback=echo_message)
chat_feed
```

```python
message = chat_feed.send("Hello!")
```

However, not all three arguments need to be in the signature.

- If there's only one, it will be `contents`.
- If there's two, it will be `contents` and `user`.
- If there's three, it will be `contents`, `user`, and `instance`.

```python
def echo_message(contents, user):
    return f"Echoing {user!r}... {contents}"

chat_feed = pn.chat.ChatFeed(callback=echo_message)
chat_feed
```

Update `callback_user` to change the default name and `callback_avatar` to update the default avatar of the responder.

```python
chat_feed = pn.chat.ChatFeed(callback=echo_message, callback_user="Echo Bot", callback_avatar="🛸")
chat_feed
```

```python
message = chat_feed.send("Hey!")
```

The specified `callback` can also return a `dict` and `ChatEntry` object, which **must contain** a `value` key, and optionally a `user` and a `avatar` key, that overrides the default `callback_user` and `callback_avatar`.

```python
def parrot_message(contents):
    return {"value": f"No, {contents.lower()}", "user": "Parrot", "avatar": "🦜"}

chat_feed = pn.chat.ChatFeed(callback=parrot_message, callback_user="Echo Bot", callback_avatar="🛸")
chat_feed
```

```python
message = chat_feed.send("Are you a parrot?")
```

If you do not want the callback to be triggered alongside `send`, set `respond=False`.

```python
message = chat_feed.send("Don't parrot this.", respond=False)
```

You can surface exceptions by setting `callback_exception` to `"summary"`.

```python
def bad_callback(contents):
    return 1 / 0

chat_feed = pn.chat.ChatFeed(callback=bad_callback, callback_exception="summary")
chat_feed
```

```python
chat_feed.send("This will fail...")
```

To see the entire traceback, you can set it to `"verbose"`.

```python
def bad_callback(contents):
    return 1 / 0

chat_feed = pn.chat.ChatFeed(callback=bad_callback, callback_exception="verbose")
chat_feed
```

```python
chat_feed.send("This will fail...")
```

Alternatively, you can provide a callable that accepts the exception and the instance as arguments to handle different exception scenarios.

```python
import random

def callback(content):
    if random.random() < 0.5:
        raise RuntimeError("This is an unhandled error")
    raise ValueError("This is a handled error")

def callback_exception_handler(exception, instance):
    if isinstance(exception, ValueError):
        instance.stream("I can handle this", user="System")
        return
    instance.stream("Fatal error occurred", user="System")

    # you can raise a new exception here if desired
    # raise RuntimeError("Fatal error occurred") from exception

chat_feed = pn.chat.ChatFeed(
    callback=callback, callback_exception=callback_exception_handler
)
```

```python
chat_feed.send("This will sometimes fail...")
```

#### Async Callbacks

The `ChatFeed` also support *async* `callback`s.

In fact, we recommend using *async* `callback`s whenever possible to keep your app fast and responsive, *as long as there's nothing blocking the event loop in the function*.

```python
import panel as pn
import asyncio
pn.extension()

async def parrot_message(contents):
    await asyncio.sleep(2.8)
    return {"value": f"No, {contents.lower()}", "user": "Parrot", "avatar": "🦜"}

chat_feed = pn.chat.ChatFeed(callback=parrot_message, callback_user="Echo Bot")
chat_feed
```

```python
message = chat_feed.send("Are you a parrot?")
```

Do not mark the function as async if there's something blocking your event loop--if you do, the placeholder will **not** appear.

```python
import panel as pn
import time
pn.extension()

async def parrot_message(contents):
    time.sleep(2.8)
    return {"value": f"No, {contents.lower()}", "user": "Parrot", "avatar": "🦜"}

chat_feed = pn.chat.ChatFeed(callback=parrot_message, callback_user="Echo Bot")
chat_feed
```

```python
message = chat_feed.send("Are you a parrot?")
```

The easiest and most optimal way to stream output is through *async generators*.

If you're unfamiliar with this term, don't fret!

It's simply prefixing your function with `async` and replacing `return` with `yield`.

```python
async def stream_message(contents):
    message = ""
    for character in contents:
        message += character
        yield message

chat_feed = pn.chat.ChatFeed(callback=stream_message)
chat_feed
```

```python
message = chat_feed.send("Streaming...")
```

You can also continuously replace the original message if you do not concatenate the characters.

```python
async def replace_message(contents):
    for character in contents:
        await asyncio.sleep(0.1)
        yield character

chat_feed = pn.chat.ChatFeed(callback=replace_message)
chat_feed
```

```python
message = chat_feed.send("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
```

This works extremely well with OpenAI's `AsyncOpenAI` client `chat.completions.create` method--just be sure that `stream` is set to `True`!

```python
import openai
import panel as pn

pn.extension()

client = openai.AsyncOpenAI()

async def openai_callback(contents):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": contents}],
        stream=True,
    )
    message = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            message += chunk.choices[0].delta.content
            yield message

chat_feed = pn.chat.ChatFeed(callback=openai_callback)
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

chat_feed = pn.chat.ChatFeed(callback=chain_message)
chat_feed
```

```python
message = chat_feed.send("Hello bots!")
```

#### Edit Callbacks

An `edit_callback` can be attached to the `ChatFeed` to handle message edits.

The signature must include the latest available message value `contents`, the index of the edited message, and the chat `instance`.

Here, when the user edits the first message, the downstream message is updated to match the edited message.

```python
def echo_callback(content, index, instance):
    return content

def edit_callback(content, index, instance):
    instance.objects[index + 1].object = content

chat_feed = pn.chat.ChatFeed(
    edit_callback=edit_callback, callback=echo_callback, callback_user="Echo Guy"
)
chat_feed.send("Edit this")
```

#### Steps

Intermediate steps, like chain of thoughts, can be provided through a series of ``ChatStep`s`.

```python
chat_feed = pn.chat.ChatFeed()
chat_feed
```

These can easily be added using the `.add_step` method:

```python
with chat_feed.add_step("To answer the user's query, I need to first create a plan.", title="Create a plan", user='Agent') as step:
    step.stream("\n\n...Okay the plan is to demo this!")
```

By default this method will attempt to append the step to an existing message as long as the last message is a step and the user matches.

```python
with chat_feed.add_step(title="Execute the plan", status="running") as step:
    step.stream("\n\n...Executing plan...")
    time.sleep(1)
    step.stream("\n\n...Handing over to SQL Agent")
```

If the user does not match a new message will be created:

```python
with chat_feed.add_step(title="Running SQL query", user='SQL Agent') as step:
    step.stream('Querying...')
    time.sleep(1)
    step.stream('\nSELECT * FROM TABLE')
```

See `ChatStep` for more details on how to use those components.

#### Prompt User

It is possible to temporarily pause the execution of code and prompt the user to answer a question, or fill out a form, using `prompt_user`, which accepts any Panel `component` and a follow-up `callback` (with `component` and `instance` as args) to execute upon submission.

```python
def repeat_answer(component, instance):
    contents = component.value
    instance.send(f"Wow, {contents}, that's my favorite flavor too!", respond=False, user="Ice Cream Bot")

def show_interest(contents, user, instance):
    if "ice" in contents or "cream" in contents:
        answer_input = pn.widgets.TextInput(
            placeholder="Enter your favorite ice cream flavor"
        )
        instance.prompt_user(answer_input, callback=repeat_answer)
    else:
        return "I'm not interested in that topic."

chat_feed = pn.chat.ChatFeed(
    callback=show_interest,
    callback_user="Ice Cream Bot",
)
chat_feed
```

```python
chat_feed.send("food");
```

You can also set a `predicate` to evaluate the component's state, e.g. widget has value. If provided, the submit button will be enabled when the predicate returns `True`. The `predicate` should accept the component as an argument.

```python
def is_chocolate(component):
    return "chocolate" in component.value.lower()

def repeat_answer(component, instance):
    contents = component.value
    instance.send(f"Wow, {contents}, that's my favorite flavor too!", respond=False, user="Ice Cream Bot")

def show_interest(contents, user, instance):
    if "ice" in contents or "cream" in contents:
        answer_input = pn.widgets.TextInput(
            placeholder="Enter your favorite ice cream flavor"
        )
        instance.prompt_user(answer_input, callback=repeat_answer, predicate=is_chocolate)
    else:
        return "I'm not interested in that topic."
```

You can also set a `timeout` in seconds and `timeout_message` to prevent submission after a certain time.

```python
def is_chocolate(component):
    return "chocolate" in component.value.lower()

def repeat_answer(component, instance):
    contents = component.value
    instance.send(f"Wow, {contents}, that's my favorite flavor too!", respond=False, user="Ice Cream Bot")

def show_interest(contents, user, instance):
    if "ice" in contents or "cream" in contents:
        answer_input = pn.widgets.TextInput(
            placeholder="Enter your favorite ice cream flavor"
        )
        instance.prompt_user(answer_input, callback=repeat_answer, predicate=is_chocolate, timeout=10, timeout_message="You're too slow!")
    else:
        return "I'm not interested in that topic."
```

Lastly, use `button_params` and `timeout_button_params` to customize the appearance of the buttons and timeout button, respectively.

#### Serialize

The chat history can be serialized for use with the `transformers` or `openai` packages through either `serialize` with `format="transformers"`.

```python
chat_feed.serialize(format="transformers")
```

`role_names` can be set to explicitly map the role to the ChatMessage's user name.

```python
chat_feed.serialize(
    format="transformers", role_names={"assistant": ["Bot 1", "Bot 2", "Bot 3"]}
)
```

A `default_role` can also be set to use if the user name is not found in `role_names`.

If this is set to None, raises a ValueError if the user name is not found.

```python
chat_feed.serialize(
    format="transformers",
    default_role="assistant"
)
```

The messages can be filtered by using a custom `filter_by` function.

```python
def filter_by_reactions(messages):
    return [message for message in messages if "favorite" in message.reactions]

chat_feed.send(
    pn.chat.ChatMessage("I'm a message with a reaction!", reactions=["favorite"])
)

chat_feed.serialize(filter_by=filter_by_reactions)
```

`help_text` is an easy way to provide instructions to the users about what the feed does.

```python
def say_hi(contents, user):
    return f"Hi {user}!"

chat_feed = pn.chat.ChatFeed(help_text="This chat feed will respond by saying hi!", callback=say_hi)
chat_feed.send("Hello there!")
chat_feed
```

By default, the `serialize` method will exclude the user `help` from its output. It can be changed by updating `exclude_users`.

```python
chat_feed.serialize()
```

If the output is complex, you can pass a `custom_serializer` to only keep the text part.

```python
complex_output = pn.Tabs(("Code", "`print('Hello World)`"), ("Output", "Hello World"))
chat_feed = pn.chat.ChatFeed(pn.chat.ChatMessage(complex_output))
chat_feed
```

Here's the output without:

```python
chat_feed.serialize()
```

Here's the output with a `custom_serializer`:

```python
def custom_serializer(obj):
    if isinstance(obj, pn.Tabs):
        # only keep the first tab's content
        return obj[0].object
    # fall back to the default serialization
    return obj.serialize()

chat_feed.serialize(custom_serializer=custom_serializer)
```

It can be fun to watch bots talking to each other. Beware of the token usage!

```python
import openai
import panel as pn

pn.extension()

client = openai.AsyncOpenAI()

async def openai_self_chat(contents, user, instance):
    if user == "User" or user == "ChatBot B":
        user = "ChatBot A"
        avatar = "https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"
    elif user == "ChatBot A":
        user = "ChatBot B"
        avatar = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Outreachy-bot-avatar.svg/193px-Outreachy-bot-avatar.svg.png"

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": contents}],
        temperature=0,
        max_tokens=500,
        stream=True,
    )
    message = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            message += chunk.choices[0].delta.content
            yield {"user": user, "value": message, "avatar": avatar}
    instance.respond()

chat_feed = pn.chat.ChatFeed(callback=openai_self_chat, sizing_mode="stretch_width", height=1000).servable()
chat_feed.send("What is HoloViz Panel?")
```

![OpenAI Bot Conversation](https://user-images.githubusercontent.com/42288570/260283078-de8f56c2-becc-4566-9813-618bfc81f3c2.gif)

#### Stream

If a returned object is not a generator (notably LangChain output), it's still possible to stream the output with the `stream` method.

Note, if you're working with `generator`s, use `yield` in your callback instead.

```python
chat_feed = pn.chat.ChatFeed()

# creates a new message
message = chat_feed.stream("Hello", user="Aspiring User", avatar="🤓")
chat_feed
```

```python
# streams (appends) to the previous message
message = chat_feed.stream(
    " World!",
    user="Aspiring User",
    avatar="🤓",
    message=message,
    footer_objects=[pn.widgets.Button(label="Footer Object")],
)
```

Be sure to check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs for more examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc.

The `stream` method is commonly used with for loops; here, we use `time.sleep`, but if you're using `async`, it's better to use `asyncio.sleep`.

```python
chat_feed = pn.chat.ChatFeed()
chat_feed
```

```python
message = None
for n in "123456789 abcdefghijklmnopqrstuvxyz":
    time.sleep(0.1)
    message = chat_feed.stream(n, message=message)
```

#### Customization

You can pass `ChatEntry` params through `message_params`.

```python
message_params = dict(
    default_avatars={"System": "S", "User": "👤"}, reaction_icons={"like": "thumb-up"}
)
chat_feed = pn.chat.ChatFeed(message_params=message_params)
chat_feed.send(user="System", value="This is the System speaking.")
chat_feed.send(user="User", value="This is the User speaking.")
chat_feed
```

Alternatively, directly pass those params to the ChatFeed constructor and it'll be forwarded into `message_params` automatically.

```python
chat_feed = pn.chat.ChatFeed(default_avatars={"System": "S", "User": "👤"}, reaction_icons={"like": "thumb-up"})
chat_feed.send(user="System", value="This is the System speaking.")
chat_feed.send(user="User", value="This is the User speaking.")
chat_feed
```

It's possible to customize the appearance of the chat feed by setting the `message_params` parameter.

Please visit `ChatMessage` for a full list of customizable, target CSS classes (e.g. `.avatar`, `.name`, etc).

```python
chat_feed = pn.chat.ChatFeed(
    show_activity_dot=True,
    message_params={
        "stylesheets": [
            """
            .message {
                background-color: tan;
                font-family: "Courier New";
                font-size: 24px;
            }
            """
        ]
    },
)
chat_feed.send("I am so stylish!")
chat_feed
```

You can build your own custom chat interface too on top of `ChatFeed`, but remember there's a pre-built `ChatInterface`!

```python
import asyncio
import panel as pn
from panel.chat import ChatMessage, ChatFeed

pn.extension()

async def get_response(contents, user):
    await asyncio.sleep(0.88)
    return {
        "Marc": "It is 2",
        "Andrew": "It is 4",
    }.get(user, "I don't know")

ASSISTANT_AVATAR = (
    "https://upload.wikimedia.org/wikipedia/commons/6/63/Yumi_UBports.png"
)

chat_feed = ChatFeed(
    ChatMessage("Hi There!", user="Assistant", avatar=ASSISTANT_AVATAR),
    callback=get_response,
    height=500,
    message_params=dict(
        default_avatars={"Assistant": ASSISTANT_AVATAR},
    ),
)

marc_button = pn.widgets.Button(
    label="Marc",
    on_click=lambda event: chat_feed.send(
        "What is the square root of 4?", user="Marc", avatar="🚴"
    ),
    align="center",
    disabled=chat_feed.param.disabled,
)
andrew_button = pn.widgets.Button(
    label="Andrew",
    on_click=lambda event: chat_feed.send(
        "What is the square root of 4 squared?", user="Andrew", avatar="🏊"
    ),
    align="center",
    disabled=chat_feed.param.disabled,
)
undo_button = pn.widgets.Button(
    label="Undo",
    on_click=lambda event: chat_feed.undo(2),
    align="center",
    disabled=chat_feed.param.disabled,
)
clear_button = pn.widgets.Button(
    label="Clear",
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

For an example on `renderers`, see `ChatInterface`.

Also, if you haven't already, check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs for more examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc.

---
