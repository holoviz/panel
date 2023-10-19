# Create Chat Interfaces

Both Streamlit and Panel provides special components to help you build conversational apps.

| Streamlit            | Panel               | Description                            |
| -------------------- | ------------------- | -------------------------------------- |
| [`chat_message`](https://docs.streamlit.io/library/api-reference/chat/st.chat_message)    | [`ChatMessage`](../../../examples/reference/chat/ChatMessage.ipynb) | Display a chat message  |
| [`chat_input`](https://docs.streamlit.io/library/api-reference/chat/st.chat_input) |  [`ChatInput` example](https://holoviz-topics.github.io/panel-chat-examples/components/#chat_input) | Input a chat message |
| [`status`](https://docs.streamlit.io/library/api-reference/status/st.status) | [`Status` example](https://holoviz-topics.github.io/panel-chat-examples/components/#status) | Display the output of long-running tasks in a container |
|                      | [`ChatFeed`](../../../examples/reference/chat/ChatFeed.ipynb)  | Display multiple chat messages         |
|                      | [`ChatInterface`](../../../examples/reference/chat/ChatInterface.ipynb)  | High-level, easy to use chat interface |
| [`StreamlitCallbackHandler`](https://python.langchain.com/docs/integrations/callbacks/streamlit) | [`PanelCallbackHandler`](../../../examples/reference/chat/ChatInterface.ipynb) | Display the thoughts and actions of a [LangChain](https://python.langchain.com/docs/get_started/introduction) agent |
| [`StreamlitChatMessageHistory`](https://python.langchain.com/docs/integrations/memory/streamlit_chat_message_history) |  | Persist the memory of a [LangChain](https://python.langchain.com/docs/get_started/introduction) agent |

The starting point for most Panel users is the *high-level* [`ChatInterface`](../../../examples/reference/chat/ChatInterface.ipyn), not the *low-level* [`ChatMessage`](../../../examples/reference/chat/ChatMessage.ipynb) and [`ChatFeed`](../../../examples/reference/chat/ChatFeed.ipynb) components.

For inspiration check out the many chat components and examples at [panel-chat-examples](https://holoviz-topics.github.io/panel-chat-examples/).

## Chat Message

Lets see how-to migrate an app that is using `st.chat_message`.

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
pn.chat.ChatMessage(message, user="user").servable()
```

![Panel ChatEntry](../../_static/images/panel_chat_entry.png)
