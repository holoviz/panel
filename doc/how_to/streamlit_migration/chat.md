# Create Chat Interfaces

Both Streamlit and Panel provides special components to help you build conversational apps.

| Streamlit            | Panel               | Description                            |
| -------------------- | ------------------- | -------------------------------------- |
| `st.chat_message`    | [`pn.chat.ChatEntry`](../../../examples/reference/chat/ChatEntry.ipynb) | Output a single chat message  |
| `st_chat_input`      |  | Input a chat message |
| `st.status`          | | Display output of long-running tasks in a container |
|                      | [`pn.chat.ChatFeed`](../../../examples/reference/chat/ChatFeed.ipynb)  | Output multiple of chat messages         |
|                      | [`pn.chat.ChatInterface`](../../../examples/reference/chat/ChatInterface.ipynb)  | High-level, easy to use chat interface |
| `langchain.callbacks.StreamlitCallbackHandler` | [`pn.chat.PanelCallbackHandler`](../../../examples/reference/chat/ChatInterface.ipynb) | Display the thoughts and actions of a LangChain agent |

The starting point for most Panel users would be the *high-level*, easy to use `ChatInterface` and `PanelCallbackHandler` components. Not the lower level `ChatEntry` and `ChatFeed` components.

You can find specialized chat components and examples at [panel-chat-examples/](https://holoviz-topics.github.io/panel-chat-examples/).

## Chat Message

Lets see how-to migrate an app using `st.chat_message`

### Streamlit Chat Message Example

```python
import streamlit as st

with st.chat_message("user"):
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png")
    st.write("# A faster way to build and share data apps")
```

![Streamlit chat_entry](../../_static/images/streamlit_chat_message.png)

### Panel Chat Message Example

```python
import panel as pn

pn.extension(design="material")

message = pn.Column(
    "https://panel.holoviz.org/_images/logo_horizontal_light_theme.png",
    "# The powerful data exploration & web app framework for Python"
)
pn.chat.ChatEntry(value=message, user="user").servable()
```

![Panel ChatEntry](../../_static/images/panel_chat_entry.png)

## Chat Input

### Streamlit Chat Input

```python
import streamlit as st

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
```

![Streamlit chat_input](../../_static/images/streamlit_chat_input.png)

### Panel Chat Input

Panel does not provide a dedicated *chat input* component because it is built into Panels high-level `ChatInterface`.

Below we will show you how to build a custom `ChatInput` widget.

```python
import param

import panel as pn

pn.extension(design="material")


class ChatInput(pn.viewable.Viewer):
    value = param.String()

    disabled = param.Boolean()
    max_length = param.Integer(default=5000)
    placeholder = param.String("Send a message")

    def __init__(self, **params):
        layout_params = {
            key: value
            for key, value in params.items()
            if not key in ["value", "placeholder", "disabled", "max_length"]
        }
        params = {
            key: value for key, value in params.items() if key not in layout_params
        }

        super().__init__(**params)

        self._text_input = pn.widgets.TextInput(
            align="center",
            disabled=self.param.disabled,
            max_length=self.param.max_length,
            name="Message",
            placeholder=self.param.placeholder,
            sizing_mode="stretch_width",
        )
        self._submit_button = pn.widgets.Button(
            align="center",
            disabled=self.param.disabled,
            icon="send",
            margin=(18, 5, 10, 0),
            name="",
            sizing_mode="fixed",
        )
        pn.bind(
            self._update_value,
            value=self._text_input,
            event=self._submit_button,
            watch=True,
        )

        self._layout = pn.Row(
            self._text_input, self._submit_button, align="center", **layout_params
        )

    def __panel__(self):
        return self._layout

    def _update_value(self, value, event):
        self.value = value or self.value
        self._text_input.value = ""


chat_input = ChatInput(placeholder="Say something")


@pn.depends(chat_input.param.value)
def message(prompt):
    if not prompt:
        return ""
    return f"User has sent the following prompt: {prompt}"


pn.Column(message, chat_input, margin=50).servable()
```

![Panel ChatInput](../../_static/images/panel_chat_input.png)
