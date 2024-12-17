from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("langchain", reason="Cannot test PanelCallbackHandler without langchain")

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chat_models.openai import ChatOpenAI
from langchain.llms.fake import FakeListLLM

from panel.chat import ChatFeed, ChatInterface
from panel.chat.langchain import PanelCallbackHandler


@pytest.mark.parametrize("streaming", [True, False])
@pytest.mark.parametrize("instance_type", [ChatFeed, ChatInterface])
def test_panel_callback_handler(streaming, instance_type):
    async def callback(contents, user, instance):
        await agent.arun(contents)

    instance = instance_type(callback=callback, callback_user="Langchain")
    callback_handler = PanelCallbackHandler(instance)
    tools = load_tools(["python_repl"])
    responses = ["Action: Python REPL\nAction Input: print(2 + 2)", "Final Answer: 4"]
    llm_kwargs = dict(
        responses=responses, callbacks=[callback_handler], streaming=streaming
    )
    llm = FakeListLLM(**llm_kwargs)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        callbacks=[callback_handler],
    )
    instance.send("2 + 2")
    assert len(instance.objects) == 3
    assert (
        instance.objects[1].object == "Action: Python REPL\nAction Input: print(2 + 2)"
    )
    assert instance.objects[2].object == "Final Answer: 4"
    assert not instance.disabled


@pytest.mark.parametrize("instance_type", [ChatFeed, ChatInterface])
def test_chat_model(instance_type, mock_completion):
    async def callback(contents, user, instance):
        with patch.object(
            llm,
            "client",
            mock_client,
        ):
            res = llm.predict(contents)
            assert res == "Bar Baz"

    instance = instance_type(
        callback=callback, callback_user="Langchain", callback_exception="verbose"
    )
    callback_handler = PanelCallbackHandler(instance)
    llm = ChatOpenAI(callbacks=[callback_handler], streaming=False)
    mock_client = MagicMock()
    completed = False

    def mock_create(*args, **kwargs):
        nonlocal completed
        completed = True
        return mock_completion

    mock_client.create = mock_create
    instance.send("bar")
    assert completed
    assert not callback_handler._is_streaming
    callback_message = instance.objects[-1]
    assert callback_message.object == "Bar Baz"
    assert callback_message.user == "LangChain (gpt-3.5-turbo)"
    assert len(instance.objects) == 2


def test_stream():
    instance = ChatFeed(callback_user="Langchain")
    callback_handler = PanelCallbackHandler(instance)
    # send each token / chunk individually
    message = callback_handler._stream("Panel")
    callback_handler._message = message
    callback_handler._stream(" ")  # important it's still sent
    callback_handler._stream("Chat!")
    assert instance.objects[-1].object == "Panel Chat!"
