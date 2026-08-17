# panel.chat.langchain module

The langchain module integrates Langchain support with Panel.

class panel.chat.langchain.PanelCallbackHandler(instance: ChatFeed \| ChatInterface, user: str = 'LangChain', avatar: str = '🦜')
Bases: `object`

The Langchain PanelCallbackHandler itself is not a widget or pane, but
is useful for rendering and streaming the *chain of thought* from
Langchain Tools, Agents, and Chains as ChatMessage objects.

Reference: [https://panel.holoviz.org/reference/chat/PanelCallbackHandler.html](https://panel.holoviz.org/reference/chat/PanelCallbackHandler.html)

Example:

\>\>\> chat_interface
=
pn.widgets.ChatInterface(callback=callback,
callback_user="Langchain")
\>\>\> callback_handler
=
pn.widgets.langchain.PanelCallbackHandler(instance=chat_interface)
\>\>\> llm
=
ChatOpenAI(streaming=True,
callbacks=\[callback_handler\])
\>\>\> chain
=
ConversationChain(llm=llm)

on_chat_model_start(serialized: dict\[str, Any\], messages: list, **kwargs: Any) → None
To prevent the inherited class from raising NotImplementedError, will
not call super() here.

on_retriever_end(documents, **kwargs: Any) → Any
Run when Retriever ends running.

on_retriever_error(error: Exception \| KeyboardInterrupt, **kwargs: Any) → Any
Run when Retriever errors.

on_text(text: str, **kwargs: Any)
Run when text is received.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
