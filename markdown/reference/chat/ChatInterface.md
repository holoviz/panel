# ChatInterface
---
```python
import asyncio
import panel as pn
from panel.chat import ChatInterface

pn.extension("perspective")
```

The `ChatInterface` is a high-level layout, providing a user-friendly front-end interface for inputting different kinds of messages: text, images, PDFs, etc.

This layout provides front-end methods to:

- Input (append) messages to the chat log.
- Re-run (resend) the most recent `user` input `ChatMessage`.
- Remove messages until the previous `user` input `ChatMessage`.
- Clear the chat log, erasing all `ChatMessage` objects.

**Since `ChatInterface` inherits from `ChatFeed`, it features all the capabilities of `ChatFeed`; please see `ChatFeed.ipynb` for its backend capabilities.**

Check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs to see applicable examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc. If you have an example to demo, we'd love to add it to the panel-chat-examples gallery!

#### Parameters:

##### Core

* **`widgets`** (`Widget | List[Widget]`): Widgets to use for the input. If not provided, defaults to `[TextInput]`.
* **`user`** (`str`): Name of the ChatInterface user.
* **`avatar`** (`str | bytes | BytesIO | pn.pane.Image`): The avatar to use for the user. Can be a single character text, an emoji, or anything supported by `pn.pane.Image`. If not set, uses the first character of the name.
* **`adaptive`** (`bool`): Whether to allow interrupting and restarting the callback when new messages are sent while a callback is already running. When True, sending a new message will cancel the current callback and start a new one with the latest message. Default is False.
* **`reset_on_send`** (`bool`): Whether to reset the widget's value after sending a message; has no effect for `TextInput`.
* **`auto_send_types`** (`tuple`): The widget types to automatically send when the user presses enter or clicks away from the widget. If not provided, defaults to `[TextInput]`.
* **`button_properties`** (`Dict[Dict[str, Any]]`): Allows addition of functionality or customization of buttons by supplying a mapping from the button name to a dictionary containing the `icon`, `callback`, `post_callback`, and/or `js_on_click` keys.
  * If the button names correspond to default buttons
(send, rerun, undo, clear), the default icon can be
updated and if a `callback` key value pair is provided,
the specified callback functionality runs before the existing one.
  * For button names that don't match existing ones,
new buttons are created and must include a
`callback`, `post_callback`, and/or `js_on_click` key.
  * The provided callbacks should have a signature that accepts
two positional arguments: instance (the ChatInterface instance)
and event (the button click event).
  * The `js_on_click` key should be a str or dict. If str,
provide the JavaScript code; else if dict, it must have a
`code` key, containing the JavaScript code
to execute when the button is clicked, and optionally an `args` key,
containing dictionary of arguments to pass to the JavaScript
code.

##### Styling

* **`show_send`** (`bool`): Whether to show the send button. Default is True.
* **`show_stop`** (`bool`): Whether to show the stop button, temporarily replacing the send button during callback; has no effect if `callback` is not async.
* **`show_rerun`** (`bool`): Whether to show the rerun button. Default is True.
* **`show_undo`** (`bool`): Whether to show the undo button. Default is True.
* **`show_clear`** (`bool`): Whether to show the clear button. Default is True.
* **`show_button_name`** (`bool`): Whether to show the button name. Default is True.

#### Properties:

* **`active_widget`** (`Widget`): The currently active widget.
* **`active`** (`int`): The currently active input widget tab index; -1 if there is only one widget available which is not in a tab.

___

#### Basics

```python
ChatInterface()
```

Although `ChatInterface` can be initialized without any arguments, it becomes much more useful, and interesting, with a `callback`.

```python
def even_or_odd(contents):
    if len(contents) % 2 == 0:
        return "Even number of characters."
    return "Odd number of characters."

ChatInterface(callback=even_or_odd)
```

You may also provide a more relevant, default `user` name and `avatar`.

```python
ChatInterface(
    callback=even_or_odd,
    user="Asker",
    avatar="?",
    callback_user="Counter",
)
```

#### Input Widgets

You can also use a different type of widget for input, like `TextInput` instead of the default `ChatAreaInput`, by setting `widgets`.

```python
def count_chars(contents):
    return f"Found {len(contents)} characters."

ChatInterface(
    callback=count_chars,
    widgets=pn.widgets.TextInput(
        placeholder="Enter some text to get a count!"
    ),
)
```

Multiple `widgets` can be set, which will be nested under a `Tabs` layout.

```python
def get_num(contents):
    if isinstance(contents, str):
        num = len(contents)
    else:
        num = contents
    return f"Got {num}."

ChatInterface(
    callback=get_num,
    widgets=[
        pn.chat.ChatAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(label="Number Input", end=10)
    ],
)
```

Widgets other than `TextInput` and `ChatAreaInput` will require the user to manually click the `Send` button, unless the type is specified in `auto_send_types`.

```python
ChatInterface(
    callback=get_num,
    widgets=[
        pn.chat.ChatAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(label="Number Input", end=10)
    ],
    auto_send_types=[pn.widgets.IntSlider],
)
```

If you include a `FileInput` in the list of widgets you can enable the user to upload files.

```python
ChatInterface(widgets=pn.widgets.FileInput(label="CSV File", accept=".csv"))
```

Try uploading a dataset! If you don't have a dataset in hand, download this sample dataset, `penguins.csv`.

Note, if you don't like the default renderer, `pn.pane.DataFrame` for CSVs, you can specify `renderers` to use `pn.pane.Perspective`; just be sure you have the `"perspective"` extension added to `pn.extension(...)` at the top of your file!

```python
ChatInterface(
    widgets=pn.widgets.FileInput(label="CSV File", accept=".csv"),
    renderers=pn.pane.Perspective
)
```

If a list is provided to `renderers`, will attempt to use the first renderer that does not raise an exception.

In addition, you may render the input however you'd like with a custom renderer as long as the signature accepts one argument, namely `value`!

```python
def bad_renderer(value):
    raise Exception("Won't render using this...")

def custom_renderer(value):
    return pn.Column(
        f"Found {len(value)} rows in the CSV.",
        pn.pane.Perspective(value, height=600)
    )

ChatInterface(
    widgets=pn.widgets.FileInput(label="CSV File", accept=".csv"),
    renderers=[bad_renderer, custom_renderer]
)
```

If you'd like to guide the user into using one widget after another, you can set `active` in the callback.

```python
def guided_get_num(contents, user, instance):
    if isinstance(contents, str):
        num = len(contents)
        instance.active = 1  # change to IntSlider tab
    else:
        num = contents
        instance.active = 0  # Change to TextAreaInput tab
    return f"Got {num}."

pn.chat.ChatInterface(
    callback=guided_get_num,
    widgets=[
        pn.chat.ChatAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(label="Number Input", end=10)
    ],
)
```

Or, simply initialize with a single widget first, then replace with another widget in the callback.

```python
def get_num_guided(contents, user, instance):
    if isinstance(contents, str):
        num = len(contents)
        instance.widgets = [widgets[1]]  # change to IntSlider
    else:
        num = contents
        instance.widgets = [widgets[0]]  # Change to ChatAreaInput
    return f"Got {num}."

widgets = [
    pn.chat.ChatAreaInput(placeholder="Enter some text to get a count!"),
    pn.widgets.IntSlider(label="Number Input", end=10)
]
pn.chat.ChatInterface(
    callback=get_num_guided,
    widgets=widgets[0],
)
```

The currently active widget can be accessed with the `active_widget` property.

```python
widgets = [
    pn.chat.ChatAreaInput(placeholder="Enter some text to get a count!"),
    pn.widgets.IntSlider(label="Number Input", end=10)
]
chat_interface = pn.chat.ChatInterface(
    widgets=widgets,
)
print(chat_interface.active_widget)
```

Sometimes, you may not want the widget to be reset after its contents has been sent.

To have the widgets' `value` persist, set `reset_on_send=False`.

```python
pn.chat.ChatInterface(
    widgets=pn.chat.ChatAreaInput(),
    reset_on_send=False,
)
```

#### Buttons

If you're not using an LLM to respond, the `Rerun` button may not be practical so it can be hidden by setting `show_rerun=False`.

The same can be done for other buttons as well with `show_send`, `show_undo`, and `show_clear`.

```python
pn.chat.ChatInterface(callback=get_num, show_rerun=False, show_undo=False)
```

If you want a slimmer `ChatInterface`, use `show_button_name=False` to hide the labels of the buttons and/ or `width` to set the total width of the component.

```python
pn.chat.ChatInterface(callback=get_num, show_button_name=False, width=400)
```

New buttons with custom functionality can be added to the input row through `button_properties`.

```python
def show_notice(instance, event):
    instance.send("This is how you add buttons!", respond=False, user="System")

pn.chat.ChatInterface(
    button_properties={"help": {"callback": show_notice, "icon": "help"}}
)
```

Default buttons can also be updated with custom behaviors, before using `callback` and after using `post_callback`.

```python
def run_before(instance, event):
    instance.send(
        "This will be cleared so it won't show after clear!",
        respond=False,
        user="System",
    )

def run_after(instance, event):
    instance.send("This will show after clear!", respond=False, user="System")

pn.chat.ChatInterface(
    button_properties={
        "clear": {"callback": run_before, "post_callback": run_after, "icon": "help"}
    }
)
```

You may also use custom Javascript code with `js_on_click` containing `code` and `args` keys for the buttons, and also set the `button_properties` after definition.

Try typing something in the chat input, and then click the new `Help` button on the bottom right.

```python
chat_interface = pn.chat.ChatInterface()
chat_interface.button_properties = {
    "help": {
        "icon": "help",
        "js_on_click": {
            "code": "alert(`Typed: '${chat_input.value}'`)",
            "args": {"chat_input": chat_interface.active_widget},
        },
    },
}
chat_interface
```

#### Adaptive Mode

When `adaptive=True` is set, the chat interface allows interrupting ongoing callback responses by sending new messages. This enables real-time adaptation and redirection of conversations.

```python
async def adaptive_callback(message, user, instance):
    # Simulate a long-running response
    for i in range(10):
        await asyncio.sleep(1)
        instance.send(f"Step {i+1}: Processing '{message}'...", respond=False)
    return f"Completed processing: {message}"

ChatInterface(
    callback=adaptive_callback,
    adaptive=True,  # Allow interrupting responses
    placeholder_text="Send follow-ups anytime to interrupt and redirect!"
)
```

With `adaptive=True`, users can:
- Send clarifications while responses are being generated
- Interrupt and redirect conversations in real-time
- Provide new requirements without waiting for completion

Try sending a message, then immediately send another to see the first response get interrupted!

Check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs for more examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc.

Also, since `ChatInterface` inherits from `ChatFeed`, be sure to also read `ChatFeed.ipynb` to understand `ChatInterface`'s full potential!

---
