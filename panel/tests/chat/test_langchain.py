import sys

import pytest

try:
    from langchain.agents import AgentType, initialize_agent, load_tools
    from langchain.llms.fake import FakeListLLM
except ImportError:
    pytest.skip("langchain not installed", allow_module_level=True)

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
    llm_kwargs = dict(responses=responses, callbacks=[callback_handler], streaming=streaming)
    if sys.version_info < (3, 9):
        llm_kwargs.pop("streaming")
    llm = FakeListLLM(**llm_kwargs)
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, callbacks=[callback_handler]
    )
    instance.send("2 + 2")
    assert len(instance.objects) == 3
    assert instance.objects[1].object == "Action: Python REPL\nAction Input: print(2 + 2)"
    assert instance.objects[2].object == "Final Answer: 4"
    assert not instance.disabled
