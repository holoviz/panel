from typing import Any, Dict, Union

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
except ImportError:
    BaseCallbackHandler = object
    AgentAction = None
    AgentFinish = None
    LLMResult = None

from panel.widgets import ChatInterface


class PanelCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        chat_interface: ChatInterface,
        user: str = "LangChain",
        avatar: str = "🦜️",
    ):
        if BaseCallbackHandler is object:
            raise ImportError(
                "LangChainCallbackHandler requires `langchain` to be installed."
            )
        self.chat_interface = chat_interface
        self._entry = None
        self._active_user = user
        self._active_avatar = avatar
        self._disabled_state = self.chat_interface.disabled

        self._input_user = user
        self._input_avatar = avatar

    def on_llm_start(self, serialized: Dict[str, Any], *args, **kwargs):
        model = kwargs.get("invocation_params", {}).get("model_name", "")
        entries = self.chat_interface.value
        if entries[-1].user != self._active_user:
            self._entry = None
        if self._active_user and model not in self._active_user:
            self._active_user = f"{self._active_user} ({model})"
        return super().on_llm_start(serialized, *args, **kwargs)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self._entry = self.chat_interface.stream(
            token,
            user=self._active_user,
            avatar=self._active_avatar,
            entry=self._entry,
        )
        return super().on_llm_new_token(token, **kwargs)

    def on_llm_end(self, response: LLMResult, *args, **kwargs):
        return super().on_llm_end(response, *args, **kwargs)

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], *args, **kwargs):
        return super().on_llm_error(error, *args, **kwargs)

    def on_agent_action(self, action: AgentAction, *args, **kwargs: Any) -> Any:
        return super().on_agent_action(action, *args, **kwargs)

    def on_agent_finish(self, finish: AgentFinish, *args, **kwargs: Any) -> Any:
        return super().on_agent_finish(finish, *args, **kwargs)

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, *args, **kwargs
    ):
        self._active_avatar = "🛠️"
        self._active_user = f"{self._active_user} - {serialized['name']}"
        return super().on_tool_start(serialized, input_str, *args, **kwargs)

    def on_tool_end(self, output, *args, **kwargs):
        self._active_user = self._input_user
        self._active_avatar = self._input_avatar
        return super().on_tool_end(output, *args, **kwargs)

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], *args, **kwargs
    ):
        return super().on_tool_error(error, *args, **kwargs)

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], *args, **kwargs
    ):
        self._entry = None
        self.chat_interface.disabled = True
        return super().on_chain_start(serialized, inputs, *args, **kwargs)

    def on_chain_end(self, outputs: Dict[str, Any], *args, **kwargs):
        self.chat_interface.disabled = self._disabled_state
        return super().on_chain_end(outputs, *args, **kwargs)

    def on_retriever_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever errors."""

    def on_retriever_end(
        self,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever ends running."""
