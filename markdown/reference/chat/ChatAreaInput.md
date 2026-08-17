# ChatAreaInput
---
```python
import panel as pn

pn.extension()
```

The `ChatAreaInput` inherits from `TextAreaInput`, allowing entering any multiline string using a text input
box, with the ability to click the "Enter" key or optionally the "Ctrl-Enter" key to submit the message.

Whether "Enter" or "Ctrl-Enter" sends the message depends on whether the `enter_sends` parameter is set to True (the default) or False.

Unlike TextAreaInput, the `ChatAreaInput` defaults to auto_grow=True and
max_rows=10, and the `value` is not synced to the server until the message is actually sent, so watch `value_input` if you need to access what's currently
available in the text input box.

Lines are joined with the newline character `\n`.

The primary purpose of `ChatAreaInput` is its use with `ChatInterface` for a high-level, *easy to use*, *ChatGPT like* interface.

#### Parameters:

For layout and styling-related parameters see the [Control the size](../../tutorials/basic/size.md), [Align Content](../../tutorials/basic/align.md) and [Style](../../tutorials/basic/style.md) tutorials.

##### Core

* **``disabled_enter``** (bool): If True, disables sending the message by pressing the `enter_sends` key.
* **``enter_sends``** (bool): If True, pressing the Enter key sends the message, if False it is sent by pressing the Ctrl-Enter. Defaults to True.
* **``value``** (str): The value when the "Enter" or "Ctrl-Enter" key is pressed. Only to be used with `watch` or `bind` because the `value` resets to `""` after the message is sent; use `value_input` instead to access what's currently available in the text input box.
* **``value_input``** (str): The current value updated on every key press.
* **`enter_pressed`** (bool): Event when the Enter/Ctrl+Enter key has been pressed.

##### Display

* **`auto_grow`** (boolean, default=True): Whether the TextArea should automatically grow in height to fit the content.
* **`cols`** (int, default=2): The number of columns in the text input field.
* **`disabled`** (boolean, default=False): Whether the widget is editable
* **`max_length`** (int, default=50000): Max character length of the input field. Defaults to 50000
* **`max_rows`** (int, default=10): The maximum number of rows in the text input field when `auto_grow=True`.
* **`name`** (str): The title of the widget
* **`placeholder`** (str): A placeholder string displayed when no value is entered
* **`rows`** (int, default=2): The number of rows in the text input field.
* **`resizable`** (boolean | str, default='both'): Whether the layout is interactively resizable, and if so in which dimensions: `width`, `height`, or `both`.

___

#### Basics

To submit a message, press the "Enter" key if **``enter_sends``** is True (the default), else press "Ctrl-Enter".

```python
pn.chat.ChatAreaInput(placeholder="Type something, and press Enter to clear!")
```

The `ChatAreaInput` is useful alongside `pn.bind` or `param.depends`.

```python
def output(value):
    return f"Submitted: {value}"

chat_area_input = pn.chat.ChatAreaInput(placeholder="Type something, and press Enter to submit!")
output_markdown = pn.bind(output, chat_area_input.param.value)
pn.Row(chat_area_input, output_markdown)
```

To see what's currently typed in, use `value_input` instead because `value` will only be set during submission and be `""` otherwise.

```python
chat_area_input = pn.chat.ChatAreaInput(enter_sends=False,   # To submit a message, press Ctrl-Enter
                                        placeholder="Type something, do not submit it, and run the next cell",)
output_markdown = pn.bind(output, chat_area_input.param.value)

pn.Row(chat_area_input, output_markdown)
```

```python
print(f'{chat_area_input.value_input=}, {chat_area_input.value=}')
```

---
