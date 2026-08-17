# ChatStep
---
```python
import time
import panel as pn

pn.extension()
```

The `ChatStep` opens up the possibility to display / hide intermediate steps prior to the final result.

Check out the [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/) docs to see applicable examples related to [LangChain](https://python.langchain.com/docs/get_started/introduction), [OpenAI](https://openai.com/blog/chatgpt), [Mistral](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjZtP35yvSBAxU00wIHHerUDZAQFnoECBEQAQ&url=https%3A%2F%2Fdocs.mistral.ai%2F&usg=AOvVaw2qpx09O_zOzSksgjBKiJY_&opi=89978449), [Llama](https://ai.meta.com/llama/), etc. If you have an example to demo, we'd love to add it to the panel-chat-examples gallery!

#### Parameters:

##### Core

* **`collapsed_on_success`** (`bool`): Whether to collapse the card on completion. Defaults to `True`.
* **`context_exception`** (`str`): How to handle exceptions raised upon exiting the context manager. If "raise", the exception will be raised. If "summary", a summary will be sent to the chat step. If "verbose", the full traceback will be sent to the chat step. If "ignore", the exception will be ignored.
* **`success_title`** (`str`): Title to display when status is success; if not provided and `collapsed_on_success` uses the last object's string. Defaults to `None`.
* **`default_title`** (`str`): The default title to display if the other title params are unset. Defaults to an empty string `""`.
* **`failed_title`** (`str`): Title to display when status is failed. Defaults to `None`.
* **`margin`** (`tuple`): Allows creating additional space around the component. May be specified as a two-tuple of the form (vertical, horizontal) or a four-tuple (top, right, bottom, left). Defaults to `(5, 5, 5, 10)`.
* **``objects``** (list): The list of objects to display in the `ChatStep`, which will be formatted like a `Column`. Should not generally be modified directly except when replaced in its entirety.
* **`pending_title`** (`str`): Title to display when status is pending. Defaults to `None`.
* **`running_title`** (`str`): Title to display when status is running. Defaults to `None`.
* **`status`** (`str`): The status of the chat step. Must be one of ["pending", "running", "success", "failed"]. Defaults to `"pending"`.

##### Styling

* **`collapsed`** (`bool`): Whether the contents of the `ChatStep` are collapsed. Defaults to `False`.
* **`default_badges`** (`dict`): Mapping from status to default status badge. Defaults to `DEFAULT_STATUS_BADGES`; keys must be one of 'pending', 'running', 'success', 'failed'.

#### Methods

##### Core

* **`stream`**: Stream a token to the last available string-like object.
* **`stream_title`**: Stream a token to the title header.
* **`serialize`**: Format the object to a string.

___

#### Basics

`ChatStep` can be initialized without any arguments.

```python
chat_step = pn.chat.ChatStep()
chat_step
```

Append `Markdown` objects to the chat step by calling `stream`.

```python
chat_step.stream("Just thinking...")
```

Calling it again will concatenate the text to the last available `Markdown` pane.

```python
chat_step.stream(" about `ChatStep`!")
```

Alternatively, setting `replace=True` will override the existing message.

```python
chat_step.stream("`ChatStep` can do a lot of things!", replace=True)
```

It's possible to also append any objects, like images.

```python
chat_step.append(pn.pane.Image("https://assets.holoviz.org/panel/samples/png_sample.png", width=50, height=50))
```

Calling `stream` afterwards will append a new `Markdown` pane below it.

```python
chat_step.stream("Like it can support images too! Above is a picture of dices.")
print(chat_step.objects)
```

To convert the objects into a string, call `serialize`, or simply use `str()`.

```python
chat_step.serialize()
```

#### Badges

The default avatars are `BooleanStatus`, but can be changed by providing `default_badges`. The values can be emojis, images, text, or Panel objects.

```python
chat_step = pn.chat.ChatStep(
    default_badges={
        "pending": "🤔",
        "running": "🏃",
        "success": "🎉",
        "failed": "😞",
    },
    status="success",
)
chat_step
```

#### Status

To show that the step is processing, you can set the status to `running` and provide a `running_title`.

```python
chat_step = pn.chat.ChatStep(status="running", running_title="Processing this step...")
chat_step.stream("Pretending to do something.")
chat_step
```

Upon completion, set the status to `success` and it'll automatically collapse the contents.

```python
chat_step.status = "success"
```

To have the title update on success, either provide the `success_title` or `default_title`.

```python
chat_step = pn.chat.ChatStep(status="running", running_title="Processing this step...", success_title="Pretend job done!")
chat_step.stream("Pretending to do something.")
chat_step.status = "success"
chat_step
```

To streamline this process, `ChatStep` may be used as a context manager.

Upon entry, the status will be changed from the default `pending` to `running`.

Exiting will change the status from `running` to `completed` if successful.

```python
chat_step = pn.chat.ChatStep(running_title="Processing this step...", success_title="Pretend job done!")
with chat_step:
    chat_step.stream("Pretending to do something.")

chat_step
```

However, if an exception occurs, the status will be set to "failed" and the error message will be displayed on the title.

```python
chat_step = pn.chat.ChatStep(running_title="Processing this step...", success_title="Pretend job done!")
chat_step
```

```python
try:
    with chat_step:
        chat_step.stream("Breaking something")
        raise RuntimeError("Just demoing!")
except RuntimeError as e:
    print("Comment this try/except to see what happens!")
```

The title can also be streamed.

```python
chat_step = pn.chat.ChatStep()
chat_step
```

```python
chat_step.status = "running"
for char in "It's streaming a title!":
    time.sleep(0.02)
    chat_step.stream_title(char)
```

It can be used with any `status`, like setting `status="pending"`.

```python
chat_step = pn.chat.ChatStep()
chat_step
```

```python
for char in "I'm deciding on a title... how about this one?":
    time.sleep(0.01)
    chat_step.stream_title(char, status="pending")
```

The title can also be completely replaced--equivalent to setting `chat_step.pending_title = "Nevermind!`

```python
chat_step.stream_title("Nevermind!", replace=True, status="pending")
```

Be sure to check out `ChatFeed` to see it works with a `ChatFeed` or `ChatInterface`!

---
