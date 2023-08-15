```python
import panel as pn

pn.extension()
```

The `ChatInterface` is a high-level widget, providing a user-friendly front-end interface for inputting different kinds of messages: text, images, PDFs, etc.

This widget provides front-end methods to:

- Input (append) messages to the chat log.
- Re-run (resend) the most recent `user` input `ChatEntry`.
- Remove entries until the previous `user` input `ChatEntry`.
- Clear the chat log, erasing all `ChatEntry` objects.

Since `ChatInterface` inherits from `ChatFeed`, it features all the capabilities of `ChatFeed`; please see [ChatFeed.ipynb](ChatFeed.ipynb) for its backend capabilities.

![Chat Design Specification](../../assets/ChatDesignSpecification.png)
#### Parameters:

##### Core

* **`widgets`** (`List[Widget]`): Widgets to use for the input. If not provided, defaults to `[TextInput]`.
* **`user`** (`str`): Name of the ChatInterface user.
* **`avatar`** (`str | BinaryIO`): The avatar to use for the user. Can be a single character text, an emoji, or anything supported by `pn.pane.Image`. If not set, uses the first character of the name.
* **`reset_on_send`** (`bool`): Whether to reset the widget's value after sending a message; has no effect for `TextInput`.
* **`auto_send_types`** (`tuple`): The widget types to automatically send when the user presses enter or clicks away from the widget. If not provided, defaults to `[TextInput]`.

##### Styling

* **`show_send`** (`bool`): Whether to show the send button.
* **`show_rerun`** (`bool`): Whether to show the rerun button.
* **`show_undo`** (`bool`): Whether to show the undo button.
* **`show_clear`** (`bool`): Whether to show the clear button.
* **`show_button_name`** (`bool`): Whether to show the button name.

#### Properties:

* **`active_widget`** (`Widget`): The currently active widget.
* **`active_tab`** (`int`): The currently active input widget tab index; -1 if there is only one widget available which is not in a tab.

___


```python
pn.widgets.ChatInterface()
```

Although `ChatInterface` can be initialized without any arguments, it becomes much more useful, and interesting, with a `callback`.


```python
def even_or_odd(contents, user, instance):
    if len(contents) % 2 == 0:
        return "Even number of characters."
    return "Odd number of characters."

pn.widgets.ChatInterface(callback=even_or_odd)
```

You may also provide a more relevant, default `user` name and `avatar`.


```python
pn.widgets.ChatInterface(
    callback=even_or_odd,
    user="Asker",
    avatar="?",
    callback_user="Counter",
    callback_avatar="#",
)
```

You can also use a different type of widget for input, like `TextAreaInput` instead of `TextInput`, by setting `widgets`.


```python
def count_chars(contents, user, instance):
    return f"Found {len(contents)} characters."

pn.widgets.ChatInterface(
    callback=count_chars,
    widgets=[pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!")],
)
```

Multiple `widgets` can be set, which will be nested under a `Tabs` layout.


```python
def get_num(contents, user, instance):
    if isinstance(contents, str):
        num = len(contents)
    else:
        num = contents
    return f"Got {num}."

pn.widgets.ChatInterface(
    callback=get_num,
    widgets=[
        pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(name="Number Input", end=10)
    ],
)
```

Widgets other than `TextInput` will require the user to manually click the `Send` button, unless the type is specified in `auto_send_types`.


```python
pn.widgets.ChatInterface(
    callback=get_num,
    widgets=[
        pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(name="Number Input", end=10)
    ],
    auto_send_types=[pn.widgets.IntSlider],
)
```

If you'd like to guide the user into using one widget after another, you can set `active_tab` in the callback.


```python
def guided_get_num(contents, user, instance):
    if isinstance(contents, str):
        num = len(contents)
        instance.active_tab = 1  # change to IntSlider tab
    else:
        num = contents
        instance.active_tab = 0  # Change to TextAreaInput tab
    return f"Got {num}."

pn.widgets.ChatInterface(
    callback=guided_get_num,
    widgets=[
        pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!"),
        pn.widgets.IntSlider(name="Number Input", end=10)
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
        instance.widgets = [widgets[0]]  # Change to TextAreaInput
    return f"Got {num}."


widgets = [
    pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!"),
    pn.widgets.IntSlider(name="Number Input", end=10)
]
pn.widgets.ChatInterface(
    callback=get_num_guided,
    widgets=[widgets[0]],
)
```

The currently active widget can be accessed with the `active_widget` property.


```python
widgets = [
    pn.widgets.TextAreaInput(placeholder="Enter some text to get a count!"),
    pn.widgets.IntSlider(name="Number Input", end=10)
]
chat_interface = pn.widgets.ChatInterface(
    widgets=widgets,
)
print(chat_interface.active_widget)
```

Sometimes, you may not want the widget to be reset after its contents has been sent.

To have the widgets' `value` persist, set `reset_on_send=False`.


```python
pn.widgets.ChatInterface(
    widgets=[pn.widgets.TextAreaInput()],
    reset_on_send=False,
)
```

If you're not using an LLM to respond, the `Rerun` button may not be practical so it can be hidden by setting `show_rerun=False`.

The same can be done for other buttons as well with `show_send`, `show_undo`, and `show_clear`.


```python
pn.widgets.ChatInterface(callback=get_num, show_rerun=False, show_undo=False)
```

If you want a slimmer `ChatInterface`, use `show_button_name=False` to hide the labels of the buttons.


```python
pn.widgets.ChatInterface(callback=get_num, show_button_name=False, width=400)
```
