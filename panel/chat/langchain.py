"""The langchain module integrates Langchain support with Panel."""

from __future__ import annotations

from typing import Any, Dict, Union

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
except ImportError:
    BaseCallbackHandler = object
    AgentAction = None
    AgentFinish = None
    LLMResult = None

from panel.chat import ChatFeed, ChatInterface


class PanelCallbackHandler(BaseCallbackHandler):
    """
    The Langchain `PanelCallbackHandler` itself is not a widget or pane, but is useful for rendering
    and streaming output from Langchain Tools, Agents, and Chains as `ChatEntry` objects.

    Reference: https://panel.holoviz.org/reference/chat/PanelCallbackHandler.html

    :Example:

    >>> chat_interface = pn.widgets.ChatInterface(callback=callback, callback_user="Langchain")
    >>> callback_handler = pn.widgets.langchain.PanelCallbackHandler(instance=chat_interface)
    >>> llm = ChatOpenAI(streaming=True, callbacks=[callback_handler])
    >>> chain = ConversationChain(llm=llm)

    """

    def __init__(
        self,
        instance: ChatFeed | ChatInterface,
        user: str = "LangChain",
        avatar: str = "🦜️",
    ):
        if BaseCallbackHandler is object:
            raise ImportError(
                "LangChainCallbackHandler requires `langchain` to be installed."
            )
        self.instance = instance
        self._entry = None
        self._active_user = user
        self._active_avatar = avatar
        self._disabled_state = self.instance.disabled
        self._is_streaming = None

        self._input_user = user  # original user
        self._input_avatar = avatar

    def _update_active(self, avatar: str, label: str):
        """
        Prevent duplicate labels from being appended to the same user.
        """
        # not a typo; Langchain passes a string :/
        if label == "None":
            return

        if f"- {label}" not in self._active_user:
            self._active_user = f"{self._active_user} - {label}"

    def on_llm_start(self, serialized: Dict[str, Any], *args, **kwargs):
        model = kwargs.get("invocation_params", {}).get("model_name", "")
        self._is_streaming = serialized.get("kwargs", {}).get("streaming")
        entries = self.instance.value
        if entries[-1].user != self._active_user:
            self._entry = None
        if self._active_user and model not in self._active_user:
            self._active_user = f"{self._active_user} ({model})"
        return super().on_llm_start(serialized, *args, **kwargs)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self._entry = self.instance.stream(
            token,
            user=self._active_user,
            avatar=self._active_avatar,
            entry=self._entry,
        )
        return super().on_llm_new_token(token, **kwargs)

    def on_llm_end(self, response: LLMResult, *args, **kwargs):
        if not self._is_streaming:
            # on_llm_new_token does not get called if not streaming
            self._entry = self.instance.stream(
                response.generations[0][0].text,
                user=self._active_user,
                avatar=self._active_avatar,
                entry=self._entry,
            )
        if self._active_user != self._input_user:
            self._active_user = self._input_user
            self._active_avatar = self._input_avatar
            self._entry = None
        return super().on_llm_end(response, *args, **kwargs)

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], *args, **kwargs):
        return super().on_llm_error(error, *args, **kwargs)

    def on_agent_action(self, action: AgentAction, *args, **kwargs: Any) -> Any:
        self._update_active("🛠️", action.tool)
        return super().on_agent_action(action, *args, **kwargs)

    def on_agent_finish(self, finish: AgentFinish, *args, **kwargs: Any) -> Any:
        return super().on_agent_finish(finish, *args, **kwargs)

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, *args, **kwargs
    ):
        self._update_active("🛠️", serialized["name"])
        return super().on_tool_start(serialized, input_str, *args, **kwargs)

    def on_tool_end(self, output, *args, **kwargs):
        return super().on_tool_end(output, *args, **kwargs)

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], *args, **kwargs
    ):
        return super().on_tool_error(error, *args, **kwargs)

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], *args, **kwargs
    ):
        self.instance.disabled = True
        return super().on_chain_start(serialized, inputs, *args, **kwargs)

    def on_chain_end(self, outputs: Dict[str, Any], *args, **kwargs):
        self.instance.disabled = self._disabled_state
        return super().on_chain_end(outputs, *args, **kwargs)

    def on_retriever_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when Retriever errors."""
        return super().on_retriever_error(error, **kwargs)

    def on_retriever_end(self, **kwargs: Any) -> Any:
        """Run when Retriever ends running."""
        return super().on_retriever_end(**kwargs)

    def on_text(self, text: str, **kwargs: Any):
        """Run when text is received."""
        return super().on_text(text, **kwargs)
